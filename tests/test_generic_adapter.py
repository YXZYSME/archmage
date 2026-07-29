# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [development]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
import unittest
from datetime import datetime, timezone

from archmage.adapters import GenericAdapter
from archmage.runtime.defaults import create_default_policy_decision_point
from archmage.runtime.domain import ApprovalRecord, VerdictDecision
from archmage.runtime.exceptions import UnfulfilledObligationError
from archmage.runtime.pdp import PolicyEnforcementPoint


class RecordingEnforcementPoint:
    def __init__(self):
        self.action = None

    def intercept(self, action, context):
        self.action = action
        return VerdictDecision.ALLOW


class NullAuditLogger:
    def log(self, event):
        return None


class TestGenericAdapter(unittest.TestCase):
    def setUp(self):
        self.pep = RecordingEnforcementPoint()
        self.adapter = GenericAdapter(self.pep)
        self.context = {
            "task_id": "task-1",
            "actor_id": "agent-1",
            "workspace": "/tmp/workspace",
            "git_sha": "a" * 40,
        }

    def test_registered_write_declares_file_effect(self):
        allowed = self.adapter.intercept_tool_call(
            "write_to_file",
            {"TargetFile": "/tmp/workspace/src/main.py", "CodeContent": "value = 1"},
            self.context,
        )

        self.assertTrue(allowed)
        self.assertEqual(self.pep.action.requested_side_effects[0].effect_type, "file_write")

    def test_registered_command_declares_shell_effect(self):
        allowed = self.adapter.intercept_tool_call(
            "run_command",
            {"Cwd": "/tmp/workspace", "CommandLine": "python -m pytest"},
            self.context,
        )

        self.assertTrue(allowed)
        self.assertEqual(self.pep.action.requested_side_effects[0].effect_type, "shell_command")

    def test_unregistered_tool_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unregistered tool"):
            self.adapter.intercept_tool_call("unknown_tool", {}, self.context)

    def test_missing_target_path_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "TargetFile"):
            self.adapter.intercept_tool_call(
                "write_to_file",
                {"CodeContent": "value = 1"},
                self.context,
            )

    def test_non_json_payload_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "canonical JSON"):
            self.adapter.intercept_tool_call(
                "write_to_file",
                {"TargetFile": "artifact.bin", "CodeContent": b"secret"},
                self.context,
            )

    def test_default_policy_requires_approval_for_shell(self):
        adapter = GenericAdapter(
            PolicyEnforcementPoint(
                create_default_policy_decision_point(),
                audit_logger=NullAuditLogger(),
            )
        )

        with self.assertRaises(UnfulfilledObligationError):
            adapter.intercept_tool_call(
                "run_command",
                {"Cwd": "/tmp/workspace", "CommandLine": "python -m pytest"},
                self.context,
            )

    def test_default_policy_accepts_verified_digest_bound_shell_approval(self):
        adapter = GenericAdapter(
            PolicyEnforcementPoint(
                create_default_policy_decision_point(),
                audit_logger=NullAuditLogger(),
                approval_verifier=lambda record, verdict, obligation: (
                    record.approver_id == "trusted-human"
                ),
            )
        )
        arguments = {"Cwd": "/tmp/workspace", "CommandLine": "python -m pytest"}

        with self.assertRaises(UnfulfilledObligationError) as captured:
            adapter.intercept_tool_call(
                "run_command",
                arguments,
                self.context,
            )

        approval = ApprovalRecord(
            approval_id="approval-shell-1",
            action_digest=captured.exception.verdict.action_digest,
            approver_id="trusted-human",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        allowed = adapter.intercept_tool_call(
            "run_command",
            arguments,
            self.context,
            approval_records=[approval],
        )

        self.assertTrue(allowed)


if __name__ == "__main__":
    unittest.main()
