# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [research]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
import unittest
from unittest.mock import patch

from evals.benchmark_runtime import environment_record


class TestBenchmarkRuntime(unittest.TestCase):
    def test_environment_accepts_workflow_revision(self):
        revision = "a" * 40

        with patch.dict("os.environ", {"ARCHMAGE_BENCHMARK_REVISION": revision}):
            environment = environment_record()

        self.assertEqual(environment["revision"], revision)

    def test_environment_rejects_mutable_revision_override(self):
        with patch.dict("os.environ", {"ARCHMAGE_BENCHMARK_REVISION": "HEAD"}):
            with self.assertRaisesRegex(ValueError, "immutable hexadecimal"):
                environment_record()


if __name__ == "__main__":
    unittest.main()
