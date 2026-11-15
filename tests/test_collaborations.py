"""Regression checks for chronology, duplicates and the film-level denominator."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "jobs")]
from common import get_spark
from analysis.collaborations import collaboration_history, film_exposure


class CollaborationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = get_spark("collaboration_regressions", driver_memory="1g", cores=1)
        cls.spark.sparkContext.setLogLevel("ERROR")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_prior_year_history_precohort_duplicates_and_self_pairs(self):
        titles = self.spark.createDataFrame([
            ("tt1", 1979, True), ("tt2", 1980, True), ("tt3", 1980, True),
            ("tt4", 1981, True), ("tt5", 2026, True), ("tt6", None, True),
        ], "tconst string, startYear int, is_feature_film boolean")
        principals = self.spark.createDataFrame(
            [(x, "a", "actor") for x in ["tt1", "tt2", "tt2", "tt3", "tt4", "tt5", "tt6"]]
            + [("tt2", "b", "actress"), ("tt3", "b", "actress"), ("tt4", "b", "actor"), ("tt2", "d", "actor")],
            "tconst string, nconst string, category string")
        crew = self.spark.createDataFrame([(f"tt{i}", ["d", "d"]) for i in range(1, 7)], "tconst string, directors array<string>")
        history = collaboration_history(titles, principals, crew)
        result = {(r.tconst, r.actor_id): r.prior_films for r in history.collect()}
        self.assertEqual(result, {("tt1", "a"): 0, ("tt2", "a"): 1, ("tt3", "a"): 1,
                                  ("tt4", "a"): 3, ("tt2", "b"): 0, ("tt3", "b"): 0, ("tt4", "b"): 2})
        exposure = {r.tconst: r.asDict() for r in film_exposure(history).collect()}
        self.assertEqual(len(exposure), 4)
        self.assertEqual(exposure["tt2"]["repeat_share"], 0.5)
        self.assertEqual(exposure["tt1"]["collaboration_group"], "first_only")


if __name__ == "__main__":
    unittest.main()
