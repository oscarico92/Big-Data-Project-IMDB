"""Shared helpers for the IMDb project: paths, schemas and the Spark session.

Every notebook and job imports this module, so the whole team reads the data
with the same schemas and from the same folders.
"""
import os
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DoubleType, IntegerType, StringType, StructField, StructType,
)

# data/ lives at the root of the repository (mounted in the container)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("IMDB_DATA_DIR", PROJECT_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"        # original .tsv.gz files from IMDb
BRONZE_DIR = DATA_DIR / "bronze"  # same data, typed, as Parquet
SILVER_DIR = DATA_DIR / "silver"  # cleaned data (data preparation section)

IMDB_BASE_URL = "https://datasets.imdbws.com"


def _schema(*fields):
    return StructType([StructField(name, dtype, True) for name, dtype in fields])


S, I, D = StringType(), IntegerType(), DoubleType()

# Official schemas: https://developer.imdb.com/non-commercial-datasets/
# Columns holding comma-separated lists are listed in ARRAY_COLUMNS and are
# split into arrays when converting to Parquet.
SCHEMAS = {
    "title.basics": _schema(
        ("tconst", S), ("titleType", S), ("primaryTitle", S),
        ("originalTitle", S), ("isAdult", I), ("startYear", I),
        ("endYear", I), ("runtimeMinutes", I), ("genres", S)),
    "title.akas": _schema(
        ("titleId", S), ("ordering", I), ("title", S), ("region", S),
        ("language", S), ("types", S), ("attributes", S),
        ("isOriginalTitle", I)),
    "title.crew": _schema(
        ("tconst", S), ("directors", S), ("writers", S)),
    "title.episode": _schema(
        ("tconst", S), ("parentTconst", S), ("seasonNumber", I),
        ("episodeNumber", I)),
    "title.principals": _schema(
        ("tconst", S), ("ordering", I), ("nconst", S), ("category", S),
        ("job", S), ("characters", S)),
    "title.ratings": _schema(
        ("tconst", S), ("averageRating", D), ("numVotes", I)),
    "name.basics": _schema(
        ("nconst", S), ("primaryName", S), ("birthYear", I),
        ("deathYear", I), ("primaryProfession", S), ("knownForTitles", S)),
}

ARRAY_COLUMNS = {
    "title.basics": ["genres"],
    "title.akas": ["types", "attributes"],
    "title.crew": ["directors", "writers"],
    "name.basics": ["primaryProfession", "knownForTitles"],
}

DATASETS = list(SCHEMAS)


def get_spark(app_name="imdb_project", driver_memory="4g", with_kafka=False):
    """Create (or get) the Spark session used by every notebook and job.

    In local mode the driver also runs the tasks, so driver_memory is the
    memory available to Spark. It is only applied if no session exists yet
    (restart the kernel to change it).
    """
    builder = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.driver.memory", driver_memory)
        .config("spark.sql.shuffle.partitions", "16")
        .config("spark.sql.session.timeZone", "UTC")
    )
    if with_kafka:
        import pyspark
        builder = builder.config(
            "spark.jars.packages",
            f"org.apache.spark:spark-sql-kafka-0-10_2.13:{pyspark.__version__}",
        )
    return builder.getOrCreate()


def read_bronze(spark, name):
    """Read one IMDb table from the bronze (typed Parquet) layer."""
    return spark.read.parquet(str(BRONZE_DIR / name))


def read_silver(spark, name):
    """Read one IMDb table from the silver (cleaned) layer."""
    return spark.read.parquet(str(SILVER_DIR / name))
