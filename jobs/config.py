"""Paths and dataset names of the IMDb project.

Pure Python on purpose (no pyspark import): scripts that do not need Spark,
like the download job, can run with a plain `python` command.
"""
import os
from pathlib import Path

# data/ lives at the root of the repository (mounted in the container)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("IMDB_DATA_DIR", PROJECT_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"        # original .tsv.gz files from IMDb
BRONZE_DIR = DATA_DIR / "bronze"  # same data, typed, as Parquet
SILVER_DIR = DATA_DIR / "silver"  # cleaned data (data preparation section)

IMDB_BASE_URL = "https://datasets.imdbws.com"

DATASETS = [
    "title.basics",
    "title.akas",
    "title.crew",
    "title.episode",
    "title.principals",
    "title.ratings",
    "name.basics",
]
