"""Download the IMDb non-commercial datasets into data/raw/.

Usage (inside the pyspark_notebook container, from /home/jovyan/work):
    python jobs/01_download_imdb.py            # skip files already there
    python jobs/01_download_imdb.py --force    # download everything again

The files are about 1.5 GB in total. They are downloaded one after the
other (no parallel requests) to stay polite with the IMDb server.
"""
import argparse
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATASETS, IMDB_BASE_URL, RAW_DIR  # noqa: E402


def download(name, force=False):
    target = RAW_DIR / f"{name}.tsv.gz"
    if target.exists() and not force:
        print(f"[skip] {target.name} already downloaded")
        return
    url = f"{IMDB_BASE_URL}/{name}.tsv.gz"
    tmp = target.with_suffix(".part")
    print(f"[get ] {url}")
    start = time.time()
    request = urllib.request.Request(
        url, headers={"User-Agent": "ece-big-data-student-project"})
    with urllib.request.urlopen(request) as response, open(tmp, "wb") as out:
        while chunk := response.read(1 << 20):
            out.write(chunk)
    tmp.rename(target)  # only complete files get the final name
    size_mb = target.stat().st_size / 1e6
    print(f"[done] {target.name}: {size_mb:.0f} MB in {time.time() - start:.0f} s")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name in DATASETS:
        download(name, args.force)
        time.sleep(1)


if __name__ == "__main__":
    main()
