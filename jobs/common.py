"""Shared helpers for the IMDb project: paths, schemas and the Spark session.

Every notebook and job imports this module, so the whole team reads the data
with the same schemas and from the same folders.
"""
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DoubleType, IntegerType, StringType, StructField, StructType,
)

# paths and dataset names live in config.py (no pyspark needed there)
from config import (  # noqa: F401  (re-exported for the notebooks)
    BRONZE_DIR, DATA_DIR, DATASETS, IMDB_BASE_URL, PROJECT_ROOT, RAW_DIR,
    SILVER_DIR,
)


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

assert set(SCHEMAS) == set(DATASETS)


def get_spark(app_name="imdb_project", driver_memory="4g", with_kafka=False):
    """Create (or get) the Spark session used by every notebook and job.

    In local mode the driver also runs the tasks, so driver_memory is the
    memory available to Spark. It is only applied when the JVM is started by
    this call (in a notebook: restart the kernel to change it; with
    spark-submit: use the --driver-memory option instead).
    """
    builder = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.driver.memory", driver_memory)
        .config("spark.sql.shuffle.partitions", "16")
        .config("spark.sql.session.timeZone", "UTC")
        # data/ is a Windows folder mounted in Docker: reads are slow, and the
        # vectored Parquet reader times out (300 s) on big row groups
        .config("spark.hadoop.parquet.hadoop.vectored.io.enabled", "false")
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
