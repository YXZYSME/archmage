# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Tests for durable ARCHMAGE audit records."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from archmage.runtime.audit import JsonlAuditLogger
from archmage.runtime.domain import (
    AuditEvent,
    ExecutionStatus,
    ReconciliationRecord,
    VerdictDecision,
)


class TestJsonlAuditLogger(unittest.TestCase):
    def test_persists_policy_decisions_and_execution_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "audit.jsonl"
            logger = JsonlAuditLogger(path)
            logger.log(
                AuditEvent(
                    event_id="evt-test",
                    action_digest="a" * 64,
                    verdicts=[],
                    final_decision=VerdictDecision.ALLOW,
                    timestamp="2026-08-07T00:00:00+00:00",
                )
            )
            logger.log_reconciliation(
                ReconciliationRecord(
                    event_id="evt-result",
                    task_id="task-1",
                    action_digest="a" * 64,
                    status=ExecutionStatus.SUCCESS,
                    result_summary="Completed.",
                    timestamp="2026-08-07T00:00:01+00:00",
                )
            )

            records = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(
                [record["record_type"] for record in records],
                ["policy_decision", "execution_result"],
            )
            self.assertEqual(records[0]["record"]["final_decision"], "ALLOW")
            self.assertEqual(records[1]["record"]["status"], "SUCCESS")

    def test_rejects_values_without_a_json_representation(self) -> None:
        with self.assertRaisesRegex(TypeError, "not JSON serializable"):
            JsonlAuditLogger._serialize_value(object())


if __name__ == "__main__":
    unittest.main()
