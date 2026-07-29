# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [research]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
import unittest

from evals.benchmark_scorecard import render_scorecard


class TestBenchmarkScorecard(unittest.TestCase):
    def setUp(self):
        self.environment = {
            "python": "3.13.14",
            "python_implementation": "CPython",
            "platform": "Linux-test",
            "revision": "a" * 40,
        }
        self.gold = {
            "schema_version": "1.0.0",
            "case_catalog": "evals/cases/gold_cases.json",
            "case_catalog_version": "1.0.0",
            "environment": self.environment,
            "evaluator_count": 11,
            "metrics": {
                "cases": 13,
                "exact_matches": 13,
                "exact_accuracy": 1.0,
                "intervention_precision": 1.0,
                "intervention_recall": 1.0,
                "false_positives": 0,
                "false_negatives": 0,
                "latency_ms": {"p95": 0.3},
            },
            "outcomes": [
                {"suite": "indirect_instruction", "exact_match": True},
                {"suite": "indirect_instruction", "exact_match": True},
            ],
        }
        self.repair = {
            "schema_version": "1.0.0",
            "case_catalog": "evals/cases/repair_cases.json",
            "case_catalog_version": "1.0.0",
            "environment": self.environment,
            "metrics": {
                "cases": 2,
                "successes": 2,
                "repair_success_rate": 1.0,
                "average_retries_to_compliance": 1.0,
            },
        }
        self.latency = {
            "schema_version": "1.0.0",
            "environment": self.environment,
            "iterations": 5000,
            "warmup": 100,
            "results": {
                "full_default_pdp": {
                    "evaluator_count": 11,
                    "wall_time_ms": {"p95": 0.35},
                    "cpu_time_ms": {"p95": 0.34},
                    "throughput_evaluations_per_second": 3132.472,
                    "peak_traced_memory_bytes": 8192,
                }
            },
        }

    def test_scorecard_records_provenance_and_results(self):
        scorecard = "\n".join(render_scorecard(self.gold, self.repair, self.latency))

        self.assertIn(f"Revision | `{'a' * 40}`", scorecard)
        self.assertIn("Gold cases | `evals/cases/gold_cases.json` | `1.0.0`", scorecard)
        self.assertIn("Repair cases | `evals/cases/repair_cases.json` | `1.0.0`", scorecard)
        self.assertIn("Gold-case compliance | 13/13 exact", scorecard)
        self.assertIn("Indirect-instruction subset | 2/2 exact", scorecard)
        self.assertIn("Full-PDP overhead | 0.350000 ms p95", scorecard)
        self.assertIn("CPython 3.13.14", scorecard)
        self.assertIn("5,000 measured; 100 warmup", scorecard)

    def test_scorecard_rejects_mixed_revisions(self):
        self.repair = dict(self.repair)
        self.repair["environment"] = dict(self.environment, revision="b" * 40)

        with self.assertRaisesRegex(ValueError, "revision"):
            render_scorecard(self.gold, self.repair, self.latency)


if __name__ == "__main__":
    unittest.main()
