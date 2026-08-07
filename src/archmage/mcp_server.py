# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""MCP tool contracts backed by the authoritative policy enforcement point."""

import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from .runtime.audit import JsonlAuditLogger
from .runtime.defaults import create_default_policy_decision_point
from .runtime.domain import (
    ActionDigest,
    ActionProposal,
    ActorIdentity,
    ExecutionStatus,
    PolicyContext,
    PolicyVerdict,
    ProposedEffect,
    ReconciliationRecord,
)
from .runtime.exceptions import (
    PolicyViolationError,
    RepairRequiredError,
    UnfulfilledObligationError,
)
from .runtime.pdp import PolicyDecisionPoint, PolicyEnforcementPoint


class ArchmageMCPServer:
    """Expose ARCHMAGE enforcement as a four-tool MCP server."""

    def __init__(
        self,
        pdp: Optional[PolicyDecisionPoint] = None,
        audit_logger: Optional[JsonlAuditLogger] = None,
    ) -> None:
        self.pdp = pdp or create_default_policy_decision_point()
        self.audit_logger = audit_logger
        self.pep = PolicyEnforcementPoint(self.pdp, audit_logger=audit_logger)
        self.acknowledged_obligations: Dict[str, List[str]] = {}
        self._known_decisions: Dict[str, Tuple[str, bool]] = {}
        self._reconciled_digests: set[str] = set()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "evaluate_action",
                "description": (
                    "Evaluate and enforce a proposed action before any side effect occurs."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "actor_id": {"type": "string"},
                        "actor_type": {
                            "type": "string",
                            "enum": ["agent", "human"],
                            "default": "agent",
                        },
                        "operation": {"type": "string"},
                        "tool": {"type": "string"},
                        "arguments": {"type": "object"},
                        "target_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "requested_side_effects": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "effect_type": {"type": "string"},
                                    "target": {"type": "string"},
                                    "payload": {"type": "object"},
                                },
                                "required": ["effect_type", "target"],
                            },
                        },
                        "repository_revision": {"type": "string"},
                        "workspace": {"type": "string"},
                        "environment": {"type": "string", "default": "local"},
                    },
                    "required": [
                        "task_id",
                        "actor_id",
                        "operation",
                        "tool",
                        "workspace",
                    ],
                },
            },
            {
                "name": "acknowledge_obligations",
                "description": (
                    "Acknowledge non-approval obligations for a task before reevaluation."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "action_digest": {"type": "string"},
                        "obligations": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["task_id", "action_digest", "obligations"],
                },
            },
            {
                "name": "reconcile_result",
                "description": (
                    "Persist the actual result of an action bound to a known policy decision."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "action_digest": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["SUCCESS", "FAILURE", "BLOCKED"],
                        },
                        "result_summary": {"type": "string"},
                    },
                    "required": ["task_id", "action_digest", "status"],
                },
            },
            {
                "name": "inspect_policy",
                "description": "Inspect active policy evaluators and enforcement capabilities.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"workspace": {"type": "string"}},
                },
            },
        ]

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        handlers = {
            "evaluate_action": self._handle_evaluate_action,
            "acknowledge_obligations": self._handle_acknowledge_obligations,
            "reconcile_result": self._handle_reconcile_result,
            "inspect_policy": self._handle_inspect_policy,
        }
        handler = handlers.get(name)
        if handler is None:
            raise ValueError(f"Unknown tool: {name}")
        return handler(arguments)

    def _handle_evaluate_action(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = str(args["task_id"])
        action = ActionProposal(
            task_id=task_id,
            actor=ActorIdentity(
                actor_id=str(args["actor_id"]),
                actor_type=str(args.get("actor_type", "agent")),
            ),
            operation=str(args["operation"]),
            tool=str(args["tool"]),
            arguments=dict(args.get("arguments", {})),
            target_paths=list(args.get("target_paths", [])),
            requested_side_effects=[
                ProposedEffect(
                    effect_type=str(effect["effect_type"]),
                    target=str(effect["target"]),
                    payload=dict(effect.get("payload", {})),
                )
                for effect in args.get("requested_side_effects", [])
            ],
            repository_revision=str(args.get("repository_revision", "HEAD")),
            environment=str(args.get("environment", "local")),
        )
        context = PolicyContext(
            workspace=str(args["workspace"]),
            environment=str(args.get("environment", "local")),
        )
        proposed_digest = ActionDigest.compute(action).digest_hash
        acknowledged = self.acknowledged_obligations.get(proposed_digest, [])
        unfulfilled: List[str] = []
        executable = False

        try:
            verdict = self.pep.evaluate_and_enforce(
                action,
                context,
                acknowledged_obligations=acknowledged,
            )
            executable = True
        except UnfulfilledObligationError as error:
            verdict = error.verdict
            unfulfilled = [error.obligation.type]
        except (PolicyViolationError, RepairRequiredError) as error:
            verdict = error.verdict

        self._known_decisions[verdict.action_digest] = (task_id, executable)
        return self._tool_response(
            self._verdict_payload(verdict, executable, unfulfilled),
            is_error=not executable,
        )

    def _handle_acknowledge_obligations(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = str(args["task_id"])
        action_digest = str(args["action_digest"])
        obligations = [str(item) for item in args.get("obligations", [])]
        if "explicit_approval" in obligations:
            raise ValueError("explicit_approval requires a verified ApprovalRecord")

        known = self._known_decisions.get(action_digest)
        if known is None:
            raise ValueError(f"unknown action_digest: {action_digest}")
        known_task_id, _ = known
        if known_task_id != task_id:
            raise ValueError("task_id does not match the policy decision")

        acknowledged = self.acknowledged_obligations.setdefault(action_digest, [])
        for obligation in obligations:
            if obligation not in acknowledged:
                acknowledged.append(obligation)
        return self._tool_response(
            {
                "task_id": task_id,
                "action_digest": action_digest,
                "acknowledged_obligations": acknowledged,
                "status": "ACKNOWLEDGED",
            }
        )

    def _handle_reconcile_result(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = str(args["task_id"])
        action_digest = str(args["action_digest"])
        known = self._known_decisions.get(action_digest)
        if known is None:
            raise ValueError(f"unknown action_digest: {action_digest}")
        known_task_id, executable = known
        if known_task_id != task_id:
            raise ValueError("task_id does not match the policy decision")

        status = ExecutionStatus(str(args["status"]))
        if action_digest in self._reconciled_digests:
            raise ValueError("action_digest has already been reconciled")
        if status == ExecutionStatus.SUCCESS and not executable:
            raise ValueError("cannot report SUCCESS for a non-executable policy decision")
        if self.audit_logger is None:
            raise ValueError("reconciliation requires a durable audit logger")

        record = ReconciliationRecord(
            event_id="evt-result-" + uuid4().hex,
            task_id=task_id,
            action_digest=action_digest,
            status=status,
            result_summary=str(args.get("result_summary", "")),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.audit_logger.log_reconciliation(record)
        self._reconciled_digests.add(action_digest)
        return self._tool_response(
            {
                "event_id": record.event_id,
                "task_id": task_id,
                "action_digest": action_digest,
                "status": status.value,
                "reconciled": True,
            }
        )

    def _handle_inspect_policy(self, args: Dict[str, Any]) -> Dict[str, Any]:
        del args
        evaluators = [
            {
                "class_name": evaluator.__class__.__name__,
                "module": evaluator.__class__.__module__,
            }
            for evaluator in self.pdp.evaluators
        ]
        return self._tool_response(
            {
                "evaluators_count": len(evaluators),
                "evaluators": evaluators,
                "audit_logger_configured": self.audit_logger is not None,
                "verified_approvals_configured": self.pep.approval_verifier is not None,
                "pdp_precedence": [
                    "DENY",
                    "ESCALATE",
                    "REPAIR",
                    "ALLOW_WITH_OBLIGATIONS",
                    "ALLOW",
                ],
            }
        )

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "archmage", "version": "2.0.0"},
                },
            }
        if method == "notifications/initialized":
            return None
        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.get_tool_definitions()},
            }
        if method == "tools/call":
            if not isinstance(params, dict):
                return self._json_rpc_error(request_id, -32602, "Invalid params")
            try:
                result = self.handle_tool_call(
                    str(params.get("name", "")),
                    dict(params.get("arguments", {})),
                )
            except (KeyError, TypeError, ValueError) as error:
                return self._json_rpc_error(request_id, -32602, str(error))
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        if request_id is None:
            return None
        return self._json_rpc_error(
            request_id,
            -32601,
            f"Method not found: {method}",
        )

    @staticmethod
    def _verdict_payload(
        verdict: PolicyVerdict,
        executable: bool,
        unfulfilled: List[str],
    ) -> Dict[str, Any]:
        return {
            "executable": executable,
            "verdict": verdict.decision.value,
            "policy_id": verdict.policy_id,
            "policy_version": verdict.policy_version,
            "law_ids": verdict.law_ids,
            "severity": verdict.severity,
            "confidence": verdict.confidence,
            "finding": verdict.finding,
            "action_digest": verdict.action_digest,
            "artifacts": verdict.artifacts,
            "repair": asdict(verdict.repair) if verdict.repair else None,
            "obligations": [asdict(obligation) for obligation in verdict.obligations],
            "unfulfilled_obligations": unfulfilled,
        }

    @staticmethod
    def _tool_response(
        payload: Dict[str, Any],
        is_error: bool = False,
    ) -> Dict[str, Any]:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(payload, separators=(",", ":"), sort_keys=True),
                }
            ],
            "isError": is_error,
        }

    @staticmethod
    def _json_rpc_error(
        request_id: Any,
        code: int,
        message: str,
    ) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }


# <!-- yxzys:sg:ai -->
