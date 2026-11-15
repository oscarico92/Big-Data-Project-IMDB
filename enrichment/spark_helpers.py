"""Spark transformations for the enrichment notebook."""
import shutil
from pyspark.sql import functions as F, Window


def top_films(titles, ratings, first_year=1980, last_year=2025, top_n=10):
    eligible = (titles.filter(F.col("is_feature_film") & F.col("startYear").between(first_year, last_year))
                .select("tconst", "primaryTitle", "startYear", "genres")
                .join(ratings.select("tconst", "numVotes", "averageRating"), "tconst", "left")
                .withColumn("genre", F.explode(F.array_distinct("genres"))).drop("genres")
                .filter(F.col("genre").isNotNull() & (F.trim("genre") != "")))
    ranking = Window.partitionBy("startYear", "genre").orderBy(
        F.desc_nulls_last("numVotes"), F.desc_nulls_last("averageRating"), "tconst")
    return eligible.withColumn("genre_rank", F.row_number().over(ranking)).filter(F.col("genre_rank") <= top_n)


def principal_candidates(principals, films):
    rows = principals.join(F.broadcast(films.select("tconst").distinct()), "tconst", "left_semi")
    # All credited principals are candidates; actor/director credits get priority.
    rows = rows.withColumn("role_priority", F.when(F.col("category").isin("actor", "actress", "director"), 0).otherwise(1))
    unique = Window.partitionBy("tconst", "nconst").orderBy("role_priority", F.asc_nulls_last("ordering"), "category")
    return rows.withColumn("duplicate_rank", F.row_number().over(unique)).filter("duplicate_rank = 1").drop("duplicate_rank")


def choose_principals(candidates, count=3):
    if "qid" in candidates.columns:
        # IMDb can contain two credited IDs for the same sourced person.
        # Such aliases must not count as two different biographies.
        candidates = candidates.withColumn("_person_identity", F.when(
            F.col("has_text") & F.col("qid").isNotNull(), F.concat(F.lit("wikidata:"), "qid"))
            .otherwise(F.concat(F.lit("imdb:"), "nconst")))
        aliases = Window.partitionBy("tconst", "_person_identity").orderBy(
            "role_priority", F.asc_nulls_last("ordering"), "nconst")
        candidates = (candidates.withColumn("_alias_rank", F.row_number().over(aliases))
                      .filter("_alias_rank = 1").drop("_alias_rank", "_person_identity"))
    order = Window.partitionBy("tconst").orderBy(
        F.desc("has_text"), "role_priority", F.asc_nulls_last("ordering"), "nconst")
    return candidates.withColumn("principal_rank", F.row_number().over(order)).filter(F.col("principal_rank") <= count)


def export_csv(df, target):
    """Spark writes all rows; rename its single part for a predictable filename."""
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.parent / ("." + target.stem + "-parts")
    df.coalesce(1).write.mode("overwrite").option("header", True).option("quoteAll", True).csv(str(staging))
    part = next(staging.glob("part-*.csv"))
    part.replace(target)
    shutil.rmtree(staging)
