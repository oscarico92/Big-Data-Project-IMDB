# ECE Big Data Processing project: IMDb (group gr-02)

## Contributors

| Name | Email | GitHub |
|---|---|---|
| Oscar SCHWARTZ | TODO | oscarico92 |
| Mathis LEITAO | TODO | Latru3lle |
| Hugo BASSAGET | TODO | Bassaget |

## Requirements

- Docker Desktop (with Docker Compose), with at least 8 GB of memory allocated to Docker
- About 10 GB of free disk space (raw files + Parquet)
- Python 3.10+ on the host, only for the Kafka producer of the streaming section

## Running the project from scratch

All commands are run from the root of the repository.

### 1. Start the environment

```bash
docker compose up -d
docker logs pyspark_notebook 2>&1 | grep "token="   # Windows: findstr "token="
```

Open the `http://127.0.0.1:8888/lab?token=...` link. The repository is mounted in the container as `/home/jovyan/work`.

### 2. Download the IMDb dataset (about 1.5 GB)

```bash
docker exec pyspark_notebook python jobs/01_download_imdb.py
```

### 3. Convert it to Parquet (bronze layer)

```bash
docker exec pyspark_notebook python jobs/02_raw_to_bronze.py
```

### 4. Run the notebooks in order

| Notebook | Section |
|---|---|
| `notebooks/01_data_preparation.ipynb` | Data preparation (writes the cleaned silver layer) |
| `notebooks/02_data_exploration.ipynb` | Data exploration |
| `notebooks/03_data_enrichment.ipynb` | Data enrichment |
| `notebooks/04_streaming.ipynb` | Streaming (see `streaming/` for the producer) |
| `notebooks/05_open_question.ipynb` | Open question |

### Data layout

| Folder | Content | Produced by |
|---|---|---|
| `data/raw/` | original `.tsv.gz` files | `jobs/01_download_imdb.py` |
| `data/bronze/<table>/` | same data, typed Parquet (`\N` -> null, lists -> arrays) | `jobs/02_raw_to_bronze.py` |
| `data/silver/<table>/` | cleaned tables | `notebooks/01_data_preparation.ipynb` |

Every notebook uses `jobs/common.py` (`get_spark()`, `read_bronze()`, `read_silver()`), so the schemas and paths are the same for everyone.

## Use of AI / LLM tools

| Tool | Used by | Tasks |
|---|---|---|
| Claude (Anthropic) | Oscar SCHWARTZ | Project skeleton: Docker Compose file, download and Parquet conversion jobs (`jobs/`), notebook templates |
| TODO | TODO | TODO |

No AI tool was used to write the explanations or reasoning in `REPORT.md`.
