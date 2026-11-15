"""Focused regression checks; run with spark-submit --driver-memory 1g."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "jobs")]
from common import get_spark
from enrichment.spark_helpers import top_films, choose_principals, principal_candidates
from enrichment.wikipedia import Collector


class SparkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = get_spark("enrichment_regressions", driver_memory="1g", cores=1)
        cls.spark.sparkContext.setLogLevel("ERROR")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_top_films_ties_boundaries_multigenre_and_unrated(self):
        titles = self.spark.createDataFrame([
            ("tt1", "A", 1980, ["Drama", "Comedy", "Drama"], True),
            ("tt2", "B", 1980, ["Drama"], True),
            ("tt3", "C", 1979, ["Drama"], True),
            ("tt4", "D", 2025, ["Drama"], True),
            ("tt5", "E", 2026, ["Drama"], True),
            ("tt6", "F", 1980, ["Drama"], False),
        ], "tconst string, primaryTitle string, startYear int, genres array<string>, is_feature_film boolean")
        ratings = self.spark.createDataFrame([("tt1", 100, 7.), ("tt2", 100, 7.)],
                                             "tconst string, numVotes int, averageRating double")
        rows = top_films(titles, ratings, top_n=1).collect()
        self.assertEqual({(r.tconst, r.genre) for r in rows}, {("tt1", "Comedy"), ("tt1", "Drama"), ("tt4", "Drama")})
        self.assertEqual(len(rows), 3)

    def test_distinct_principals_and_sourced_fallback(self):
        principals = self.spark.createDataFrame([
            ("tt1", "nm1", 1, "actor"), ("tt1", "nm1", 4, "director"),
            ("tt1", "nm2", 2, "actor"), ("tt1", "nm3", 3, "actress"),
            ("tt1", "nm4", 5, "writer"), ("tt2", "nm5", 1, "actor"),
        ], "tconst string, nconst string, ordering int, category string")
        films = self.spark.createDataFrame([("tt1",)], "tconst string")
        rows = principal_candidates(principals, films)
        from pyspark.sql import functions as F
        result = choose_principals(rows.withColumn("has_text", F.col("nconst") != "nm1")).collect()
        self.assertEqual({r.nconst for r in result}, {"nm2", "nm3", "nm4"})

    def test_notebook_explicit_schemas_parse(self):
        notebook = json.loads((ROOT / "notebooks/03_data_enrichment.ipynb").read_text())
        import ast
        for cell in notebook["cells"]:
            if cell["cell_type"] != "code":
                continue
            tree = ast.parse("".join(cell["source"]))
            for statement in tree.body:
                if isinstance(statement, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {"identity_schema", "page_schema"} for t in statement.targets):
                    self.spark.createDataFrame([], ast.literal_eval(statement.value))


class CollectionTests(unittest.TestCase):
    def test_successful_response_is_reused(self):
        import io
        with tempfile.TemporaryDirectory() as folder:
            client = Collector(folder)
            with patch("urllib.request.urlopen", return_value=io.BytesIO(b'{"query": {"pages": []}}')) as request:
                first = client.request("test", "https://example.org/api", {"x": 1})
                second = client.request("test", "https://example.org/api", {"x": 1})
            self.assertEqual(first, second)
            self.assertEqual(request.call_count, 1)
            self.assertIn("retrieved_at", json.loads(first.read_text()))

    def test_nonretryable_api_error_does_not_enter_cache(self):
        import io
        with tempfile.TemporaryDirectory() as folder:
            with patch("urllib.request.urlopen", return_value=io.BytesIO(b'{"error":{"code":"badvalue"}}')):
                with self.assertRaises(ValueError):
                    Collector(folder).request("test", "https://example.org/api", {})
            self.assertFalse(list(Path(folder).rglob("*.json")))


if __name__ == "__main__":
    unittest.main()
