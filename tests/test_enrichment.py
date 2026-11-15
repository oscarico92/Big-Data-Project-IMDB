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

    def test_alias_imdb_ids_do_not_count_as_distinct_biographies(self):
        candidates = self.spark.createDataFrame([
            ("tt1", "nm1", "Q1", True, 0, 1),
            ("tt1", "nm2", "Q1", True, 0, 2),
            ("tt1", "nm3", "Q2", True, 0, 3),
            ("tt1", "nm4", "Q3", True, 0, 4),
        ], "tconst string, nconst string, qid string, has_text boolean, role_priority int, ordering int")
        rows = choose_principals(candidates).collect()
        self.assertEqual({r.nconst for r in rows}, {"nm1", "nm3", "nm4"})
        self.assertEqual(len({r.qid for r in rows}), 3)


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

    def test_rate_limit_retries_after_server_delay(self):
        import io
        import urllib.error
        from email.message import Message
        headers = Message()
        headers["Retry-After"] = "12"
        failure = urllib.error.HTTPError("https://example.org/api", 429, "Too Many Requests", headers, None)
        with tempfile.TemporaryDirectory() as folder:
            with patch("urllib.request.urlopen", side_effect=[failure, io.BytesIO(b'{"query":{"pages":[]}}')]) as request:
                with patch("time.sleep") as sleep:
                    path = Collector(folder).request("test", "https://example.org/api", {})
            self.assertTrue(path.exists())
            self.assertEqual(request.call_count, 2)
            self.assertIn(unittest.mock.call(12.0), sleep.call_args_list)

    def test_optimized_identity_requests_resume_from_cache(self):
        import io
        from urllib.parse import urlparse, parse_qs
        with tempfile.TemporaryDirectory() as folder:
            client = Collector(folder)
            with patch("urllib.request.urlopen", return_value=io.BytesIO(b'{"results":{"bindings":[]}}')) as request:
                first = client.identities(["tt0133093"])
                second = client.identities(["tt0133093"])
            self.assertEqual(first, second)
            self.assertEqual(request.call_count, 1)
            saved = json.loads(Path(first[0]).read_text())
            query = parse_qs(urlparse(saved["request_url"]).query)["query"][0]
            self.assertIn('hint:optimizer "None"', query)


if __name__ == "__main__":
    unittest.main()
