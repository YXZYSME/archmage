# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Behavior tests for the MCP enforcement adapter."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional

from archmage.mcp_server import ArchmageMCPServer
from archmage.runtime.audit import JsonlAuditLogger
from archmage.runtime.domain import (
    ActionProposal,
    Obligation,
    PolicyContext,
    PolicyVerdict,
    RepairInstruction,
    VerdictDecision,
)
from archmage.runtime.evaluators import BaseEvaluator
from archmage.runtime.pdp import PolicyDecisionPoint


class StaticEvaluator(BaseEvaluator):
    def __init__(
        self,
        decision: VerdictDecision,
        obligations: Optional[List[Obligation]] = None,
    ) -> None:
        self.decision = decision
        self.obligations = obligations or []

    def evaluate(
        self,
        action: ActionProposal,
        context: PolicyContext,
        action_digest: str,
    ) -> PolicyVerdict:
        repair = None
        if self.decision == VerdictDecision.REPAIR:
            repair = RepairInstruction(operation="repair_action", required_fields=[])
        return PolicyVerdict(
            decision=self.decision,
            policy_id="POL-MCP-TEST",
            policy_version="1.0.0",
            law_ids=[8],
            severity="high",
            confidence=1.0,
            actor_id=action.actor.actor_id,
            task_id=action.task_id,
            action_digest=action_digest,
            artifacts=action.target_paths,
            finding="MCP contract test verdict.",
            repair=repair,
            obligations=self.obligations,
        )


class TestArchmageMCPServer(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.audit_path = Path(self.temp_directory.name) / "audit.jsonl"

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def _server(
        self,
        decision: VerdictDecision = VerdictDecision.ALLOW,
        obligations: Optional[List[Obligation]] = None,
    ) -> ArchmageMCPServer:
        evaluator = StaticEvaluator(decision, obligations)
        return ArchmageMCPServer(
            pdp=PolicyDecisionPoint([evaluator]),
            audit_logger=JsonlAuditLogger(self.audit_path),
        )

    @staticmethod
    def _action_arguments(task_id: str = "mcp-task") -> dict[str, object]:
        return {
            "task_id": task_id,
            "actor_id": "mcp-agent",
            "actor_type": "agent",
            "operation": "inspect_file",
            "tool": "read_file",
            "arguments": {},
            "target_paths": [],
            "requested_side_effects": [],
            "repository_revision": "0123456789abcdef0123456789abcdef01234567",
            "workspace": "/tmp/workspace",
            "environment": "local",
        }

    @staticmethod
    def _payload(response: dict[str, object]) -> dict[str, object]:
        content = response["content"]
        assert isinstance(content, list)
        first = content[0]
        assert isinstance(first, dict)
        return json.loads(str(first["text"]))

    def test_allow_verdict_is_executable_and_audited(self) -> None:
        server = self._server()

        response = server.handle_tool_call("evaluate_action", self._action_arguments())
        payload = self._payload(response)

        self.assertFalse(response["isError"])
        self.assertTrue(payload["executable"])
        self.assertEqual(payload["verdict"], "ALLOW")
        records = [json.loads(line) for line in self.audit_path.read_text().splitlines()]
        self.assertEqual(records[0]["record_type"], "policy_decision")

    def test_deny_and_repair_verdicts_are_not_executable(self) -> None:
        for decision in (VerdictDecision.DENY, VerdictDecision.REPAIR):
            with self.subTest(decision=decision):
                server = self._server(decision)
                response = server.handle_tool_call(
                    "evaluate_action", self._action_arguments(task_id=decision.value)
                )
                payload = self._payload(response)
                self.assertTrue(response["isError"])
                self.assertFalse(payload["executable"])
                self.assertEqual(payload["verdict"], decision.value)

    def test_normal_obligation_must_be_acknowledged_before_execution(self) -> None:
        obligation = Obligation(type="must_review", required_before="execution")
        server = self._server(VerdictDecision.ALLOW_WITH_OBLIGATIONS, [obligation])

        blocked = server.handle_tool_call("evaluate_action", self._action_arguments())
        digest = self._payload(blocked)["action_digest"]
        server.handle_tool_call(
            "acknowledge_obligations",
            {
                "task_id": "mcp-task",
                "action_digest": digest,
                "obligations": ["must_review"],
            },
        )
        allowed = server.handle_tool_call("evaluate_action", self._action_arguments())

        self.assertTrue(blocked["isError"])
        self.assertFalse(allowed["isError"])
        self.assertEqual(self._payload(blocked)["unfulfilled_obligations"], ["must_review"])
        self.assertEqual(self._payload(allowed)["unfulfilled_obligations"], [])

    def test_raw_explicit_approval_is_rejected(self) -> None:
        server = self._server()
        evaluation = server.handle_tool_call("evaluate_action", self._action_arguments())
        digest = self._payload(evaluation)["action_digest"]

        with self.assertRaisesRegex(ValueError, "verified ApprovalRecord"):
            server.handle_tool_call(
                "acknowledge_obligations",
                {
                    "task_id": "mcp-task",
                    "action_digest": digest,
                    "obligations": ["explicit_approval"],
                },
            )

    def test_obligation_acknowledgement_is_bound_to_the_action_digest(self) -> None:
        obligation = Obligation(type="must_review", required_before="execution")
        server = self._server(VerdictDecision.ALLOW_WITH_OBLIGATIONS, [obligation])
        blocked = server.handle_tool_call("evaluate_action", self._action_arguments())
        digest = self._payload(blocked)["action_digest"]
        server.handle_tool_call(
            "acknowledge_obligations",
            {
                "task_id": "mcp-task",
                "action_digest": digest,
                "obligations": ["must_review"],
            },
        )
        with self.assertRaisesRegex(ValueError, "unknown action_digest"):
            server.handle_tool_call(
                "acknowledge_obligations",
                {
                    "task_id": "mcp-task",
                    "action_digest": "f" * 64,
                    "obligations": ["must_review"],
                },
            )
        with self.assertRaisesRegex(ValueError, "task_id does not match"):
            server.handle_tool_call(
                "acknowledge_obligations",
                {
                    "task_id": "different-task",
                    "action_digest": digest,
                    "obligations": ["must_review"],
                },
            )

        changed = self._action_arguments()
        changed["arguments"] = {"changed": True}
        changed_result = server.handle_tool_call("evaluate_action", changed)

        self.assertTrue(changed_result["isError"])
        self.assertNotEqual(self._payload(changed_result)["action_digest"], digest)

    def test_reconcile_result_is_bound_to_a_known_decision_and_persisted(self) -> None:
        server = self._server()
        evaluation = server.handle_tool_call("evaluate_action", self._action_arguments())
        digest = self._payload(evaluation)["action_digest"]

        response = server.handle_tool_call(
            "reconcile_result",
            {
                "task_id": "mcp-task",
                "action_digest": digest,
                "status": "SUCCESS",
                "result_summary": "Read completed.",
            },
        )

        payload = self._payload(response)
        self.assertTrue(payload["reconciled"])
        records = [json.loads(line) for line in self.audit_path.read_text().splitlines()]
        self.assertEqual(records[-1]["record_type"], "execution_result")
        self.assertEqual(records[-1]["record"]["result_summary"], "Read completed.")
        with self.assertRaisesRegex(ValueError, "already been reconciled"):
            server.handle_tool_call(
                "reconcile_result",
                {
                    "task_id": "mcp-task",
                    "action_digest": digest,
                    "status": "SUCCESS",
                },
            )

    def test_reconcile_rejects_unknown_or_inconsistent_results(self) -> None:
        server = self._server(VerdictDecision.DENY)
        evaluation = server.handle_tool_call("evaluate_action", self._action_arguments())
        digest = self._payload(evaluation)["action_digest"]

        with self.assertRaisesRegex(ValueError, "unknown action_digest"):
            server.handle_tool_call(
                "reconcile_result",
                {
                    "task_id": "mcp-task",
                    "action_digest": "f" * 64,
                    "status": "BLOCKED",
                },
            )
        with self.assertRaisesRegex(ValueError, "cannot report SUCCESS"):
            server.handle_tool_call(
                "reconcile_result",
                {
                    "task_id": "mcp-task",
                    "action_digest": digest,
                    "status": "SUCCESS",
                },
            )

    def test_reconcile_requires_matching_task_and_durable_audit(self) -> None:
        server = self._server()
        evaluation = server.handle_tool_call("evaluate_action", self._action_arguments())
        digest = self._payload(evaluation)["action_digest"]

        with self.assertRaisesRegex(ValueError, "task_id does not match"):
            server.handle_tool_call(
                "reconcile_result",
                {
                    "task_id": "different-task",
                    "action_digest": digest,
                    "status": "FAILURE",
                },
            )

        evaluator = StaticEvaluator(VerdictDecision.ALLOW)
        server_without_audit = ArchmageMCPServer(pdp=PolicyDecisionPoint([evaluator]))
        decision = server_without_audit.handle_tool_call(
            "evaluate_action", self._action_arguments(task_id="no-audit")
        )
        digest_without_audit = self._payload(decision)["action_digest"]
        with self.assertRaisesRegex(ValueError, "durable audit logger"):
            server_without_audit.handle_tool_call(
                "reconcile_result",
                {
                    "task_id": "no-audit",
                    "action_digest": digest_without_audit,
                    "status": "FAILURE",
                },
            )

    def test_inspection_unknown_tools_and_json_rpc_tool_calls(self) -> None:
        server = self._server()
        inspection = server.handle_tool_call("inspect_policy", {})
        inspection_payload = self._payload(inspection)

        self.assertTrue(inspection_payload["audit_logger_configured"])
        self.assertEqual(inspection_payload["evaluators_count"], 1)
        with self.assertRaisesRegex(ValueError, "Unknown tool"):
            server.handle_tool_call("missing", {})

        invalid_params = server.handle_request(
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": []}
        )
        invalid_tool = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {"name": "missing", "arguments": {}},
            }
        )
        valid_tool = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {"name": "inspect_policy", "arguments": {}},
            }
        )
        ignored_notification = server.handle_request(
            {"jsonrpc": "2.0", "method": "unknown-notification"}
        )

        assert invalid_params is not None
        assert invalid_tool is not None
        assert valid_tool is not None
        self.assertEqual(invalid_params["error"]["code"], -32602)
        self.assertEqual(invalid_tool["error"]["code"], -32602)
        self.assertIn("result", valid_tool)
        self.assertIsNone(ignored_notification)

    def test_json_rpc_lifecycle_and_errors(self) -> None:
        server = self._server()

        initialized = server.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        )
        listed = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        pinged = server.handle_request({"jsonrpc": "2.0", "id": 3, "method": "ping"})
        notification = server.handle_request(
            {"jsonrpc": "2.0", "method": "notifications/initialized"}
        )
        unknown = server.handle_request({"jsonrpc": "2.0", "id": 4, "method": "unknown"})

        assert initialized is not None
        assert listed is not None
        assert pinged is not None
        assert unknown is not None
        self.assertEqual(initialized["result"]["protocolVersion"], "2024-11-05")
        self.assertEqual(len(listed["result"]["tools"]), 4)
        self.assertEqual(pinged["result"], {})
        self.assertIsNone(notification)
        self.assertEqual(unknown["error"]["code"], -32601)


if __name__ == "__main__":
    unittest.main()
