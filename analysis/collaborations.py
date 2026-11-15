"""Release-year-aware actor/director collaboration analysis in Spark."""
import shutil
from pyspark.sql import functions as F, Window


def collaboration_history(titles, principals, crew, last_year=2025):
    films = titles.filter(F.col("is_feature_film") & F.col("startYear").isNotNull()
                          & (F.col("startYear") <= last_year)).select("tconst", "startYear")
    actors = (principals.filter(F.col("category").isin("actor", "actress"))
              .select("tconst", F.col("nconst").alias("actor_id")).distinct()
              .join(films.select("tconst"), "tconst", "left_semi"))
    directors = crew.select("tconst", F.explode("directors").alias("director_id")).distinct()
    pairs = (films.join(actors, "tconst").join(directors, "tconst")
             .filter(F.col("actor_id") != F.col("director_id"))
             .dropDuplicates(["tconst", "actor_id", "director_id"]))
    # Same-year films have no known order: only strictly earlier years count.
    earlier = Window.partitionBy("actor_id", "director_id").orderBy("startYear").rangeBetween(Window.unboundedPreceding, -1)
    return (pairs.withColumn("prior_films", F.coalesce(F.count("*").over(earlier), F.lit(0)))
            .withColumn("repeat_pair", F.col("prior_films") > 0))


def film_exposure(history):
    return (history.groupBy("tconst").agg(F.count("*").alias("credited_pairs"),
            F.sum(F.col("repeat_pair").cast("int")).alias("repeat_pairs"),
            F.countDistinct("actor_id").alias("credited_actors"),
            F.countDistinct("director_id").alias("credited_directors"))
            .withColumn("repeat_share", F.col("repeat_pairs") / F.col("credited_pairs"))
            .withColumn("collaboration_group", F.when(F.col("repeat_pairs") > 0, "at_least_one_repeat").otherwise("first_only")))


def summaries(films, min_votes):
    eligible = films.filter(F.col("numVotes") >= min_votes)
    return (eligible.groupBy("collaboration_group").agg(
        F.count("*").alias("films"), F.avg("averageRating").alias("mean_rating"),
        F.expr("percentile_approx(averageRating, 0.5, 10000)").alias("median_rating"),
        F.avg("numVotes").alias("mean_votes"),
        F.expr("percentile_approx(numVotes, 0.5, 10000)").alias("median_votes"),
        F.avg(F.log1p("numVotes")).alias("mean_log1p_votes"),
        F.avg("repeat_share").alias("mean_repeat_share"))
        .withColumn("minimum_votes", F.lit(min_votes)))


def year_genre_comparison(films, min_votes=100, minimum_cell=5):
    memberships = (films.filter(F.col("numVotes") >= min_votes)
                   .withColumn("genre", F.explode(F.array_distinct("genres"))))
    grouped = memberships.groupBy("startYear", "genre", "collaboration_group").agg(
        F.count("*").alias("n"), F.avg("averageRating").alias("rating"),
        F.avg(F.log1p("numVotes")).alias("log_votes"))
    first = grouped.filter("collaboration_group = 'first_only'").select(
        "startYear", "genre", F.col("n").alias("first_n"), F.col("rating").alias("first_rating"), F.col("log_votes").alias("first_log_votes"))
    repeat = grouped.filter("collaboration_group = 'at_least_one_repeat'").select(
        "startYear", "genre", F.col("n").alias("repeat_n"), F.col("rating").alias("repeat_rating"), F.col("log_votes").alias("repeat_log_votes"))
    return (first.join(repeat, ["startYear", "genre"])
        .filter((F.col("first_n") >= minimum_cell) & (F.col("repeat_n") >= minimum_cell))
        .withColumn("weight", F.col("first_n") * F.col("repeat_n") / (F.col("first_n") + F.col("repeat_n")))
        .withColumn("rating_difference", F.col("repeat_rating") - F.col("first_rating"))
        .withColumn("log_votes_difference", F.col("repeat_log_votes") - F.col("first_log_votes")))


def export_csv(df, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.parent / ("." + target.stem + "-parts")
    df.coalesce(1).write.mode("overwrite").option("header", True).option("quoteAll", True).csv(str(staging))
    next(staging.glob("part-*.csv")).replace(target)
    shutil.rmtree(staging)
