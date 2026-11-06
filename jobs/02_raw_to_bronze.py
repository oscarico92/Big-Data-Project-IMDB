"""Convert the raw IMDb .tsv.gz files into typed Parquet tables (bronze layer).

Usage (inside the pyspark_notebook container, from /home/jovyan/work):
    python jobs/02_raw_to_bronze.py                    # all tables
    python jobs/02_raw_to_bronze.py title.ratings      # only some tables

What it does, and nothing more (cleaning is done in the data preparation
section, on top of this layer):
- explicit schema from common.SCHEMAS (no schema inference on GBs of text)
- IMDb writes missing values as \\N -> read as null
- quoting disabled: titles contain " characters that are not CSV quotes
- comma-separated list columns -> arrays (common.ARRAY_COLUMNS)
- Parquet, because .gz is not splittable: every later read of the Parquet
  files runs in parallel instead of on a single core
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pyspark.sql import functions as F  # noqa: E402

from common import (  # noqa: E402
    ARRAY_COLUMNS, BRONZE_DIR, DATASETS, RAW_DIR, SCHEMAS, get_spark,
)


def convert(spark, name):
    source = RAW_DIR / f"{name}.tsv.gz"
    if not source.exists():
        raise FileNotFoundError(f"{source} missing: run jobs/01_download_imdb.py first")
    start = time.time()
    df = (
        spark.read
        .option("sep", "\t")
        .option("header", True)
        .option("nullValue", "\\N")
        .option("quote", "")
        .option("mode", "PERMISSIVE")
        .schema(SCHEMAS[name])
        .csv(str(source))
    )
    for column in ARRAY_COLUMNS.get(name, []):
        df = df.withColumn(column, F.split(F.col(column), ","))
    target = BRONZE_DIR / name
    df.repartition(16).write.mode("overwrite").parquet(str(target))
    rows = spark.read.parquet(str(target)).count()
    print(f"[done] {name}: {rows:,} rows in {time.time() - start:.0f} s -> {target}")


def main():
    names = sys.argv[1:] or DATASETS
    unknown = set(names) - set(DATASETS)
    if unknown:
        sys.exit(f"unknown table(s): {', '.join(sorted(unknown))}")
    spark = get_spark("imdb_raw_to_bronze")
    spark.sparkContext.setLogLevel("WARN")
    for name in names:
        convert(spark, name)
    spark.stop()


if __name__ == "__main__":
    main()
