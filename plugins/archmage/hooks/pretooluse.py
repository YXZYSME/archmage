#!/usr/bin/env python3
# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Claude Code PreToolUse hook that maps ARCHMAGE verdicts to permission decisions.

Fail-closed mapping (see plugins/archmage/README.md):

- ALLOW -> allow
- DENY -> deny
- ESCALATE -> ask
- REPAIR -> deny
- ALLOW_WITH_OBLIGATIONS -> ask
- import, parse, or evaluation failure -> deny
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Mapping, Optional, Tuple

PERMISSION_ALLOW = "allow"
PERMISSION_DENY = "deny"
PERMISSION_ASK = "ask"

_FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
_SHELL_TOOLS = {"Bash"}
_PATH_KEYS = (
    "file_path",
    "filePath",
    "path",
    "TargetFile",
    "notebook_path",
    "notebookPath",
)


def map_verdict_to_permission(verdict: str) -> str:
    """Return a PreToolUse permissionDecision for one ARCHMAGE verdict."""

    normalized = verdict.strip().upper()
    if normalized == "ALLOW":
        return PERMISSION_ALLOW
    if normalized == "ESCALATE":
        return PERMISSION_ASK
    if normalized == "ALLOW_WITH_OBLIGATIONS":
        return PERMISSION_ASK
    return PERMISSION_DENY


def hook_output(
    permission: str,
    reason: str,
    *,
    verdict: Optional[str] = None,
    policy_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the Claude Code PreToolUse JSON response."""

    detail = reason
    if verdict:
        detail = f"{verdict}: {reason}"
    if policy_id:
        detail = f"{detail} ({policy_id})"
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": permission,
            "permissionDecisionReason": detail,
        }
    }


def fail_closed(reason: str) -> Dict[str, Any]:
    """Deny when evaluation cannot complete."""

    return hook_output(PERMISSION_DENY, reason)


def _string_field(mapping: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = mapping.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def extract_target_paths(tool_name: str, tool_input: Mapping[str, Any]) -> List[str]:
    """Collect declared filesystem targets from a Claude Code tool payload."""

    paths: List[str] = []
    for key in _PATH_KEYS:
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            paths.append(value.strip())
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, Mapping):
                nested = _string_field(edit, *_PATH_KEYS)
                if nested:
                    paths.append(nested)
    if tool_name in _SHELL_TOOLS:
        cwd = _string_field(tool_input, "cwd", "Cwd")
        if cwd:
            paths.append(cwd)
    # Preserve order while dropping duplicates.
    return list(dict.fromkeys(paths))


def resolve_workspace(payload: Mapping[str, Any], tool_input: Mapping[str, Any]) -> str:
    """Prefer an absolute workspace from the hook payload or environment."""

    candidates = [
        _string_field(payload, "cwd"),
        os.environ.get("CLAUDE_PROJECT_DIR", ""),
        os.environ.get("PWD", ""),
        _string_field(tool_input, "cwd", "Cwd"),
    ]
    for candidate in candidates:
        if candidate and os.path.isabs(candidate):
            return os.path.abspath(candidate)
    return ""


def resolve_repository_revision(workspace: str) -> str:
    """Read an immutable git revision; empty when lineage cannot be proven."""

    if not workspace:
        return ""
    try:
        completed = subprocess.run(
            ["git", "-C", workspace, "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""
    revision = completed.stdout.strip()
    if completed.returncode != 0 or not revision:
        return ""
    return revision


def audit_logger_configured() -> bool:
    """Treat a configured audit path as the host's transparency obligation."""

    return bool(os.environ.get("ARCHMAGE_AUDIT_LOG", "").strip())


def build_proposal(
    payload: Mapping[str, Any],
) -> Tuple[Any, Any]:
    """Convert a PreToolUse event into an ActionProposal and PolicyContext."""

    from archmage import ActionProposal, ActorIdentity, PolicyContext, ProposedEffect

    tool_name = _string_field(payload, "tool_name")
    raw_input = payload.get("tool_input")
    tool_input: Dict[str, Any] = dict(raw_input) if isinstance(raw_input, Mapping) else {}
    workspace = resolve_workspace(payload, tool_input)
    if not workspace:
        raise ValueError("absolute workspace is required for fail-closed evaluation")

    if tool_name in _SHELL_TOOLS:
        operation = "run_command"
        effect_type = "shell_command"
    elif tool_name in _FILE_TOOLS:
        operation = "write_file"
        effect_type = "file_write"
    else:
        raise ValueError(f"unregistered Claude Code tool '{tool_name}' is denied")

    target_paths = extract_target_paths(tool_name, tool_input)
    session_id = _string_field(payload, "session_id", "sessionId") or "claude-code"
    tool_use_id = _string_field(payload, "tool_use_id", "toolUseId")
    task_id = tool_use_id or session_id
    revision = resolve_repository_revision(workspace)
    if not revision:
        raise ValueError("immutable repository revision is required")

    proposal = ActionProposal(
        task_id=task_id,
        actor=ActorIdentity(actor_id="claude-code", actor_type="agent"),
        operation=operation,
        tool=tool_name,
        arguments=tool_input,
        target_paths=target_paths,
        requested_side_effects=[
            ProposedEffect(effect_type=effect_type, target=tool_name, payload=tool_input)
        ],
        repository_revision=revision,
        environment="local",
    )
    context = PolicyContext(
        workspace=workspace,
        environment="local",
        audit_logger_configured=audit_logger_configured(),
    )
    return proposal, context


def evaluate_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Evaluate one PreToolUse event and return the hook JSON object."""

    try:
        from archmage import VerdictDecision, create_default_policy_decision_point
    except ImportError:
        return fail_closed("archmage is not installed; run: python -m pip install archmage-ai")

    try:
        proposal, context = build_proposal(payload)
        verdict = create_default_policy_decision_point().evaluate(proposal, context)
    except Exception as error:  # noqa: BLE001 - hook must fail closed on any evaluation error
        return fail_closed(f"evaluation failed: {error}")

    decision = (
        verdict.decision.value
        if isinstance(verdict.decision, VerdictDecision)
        else str(verdict.decision)
    )
    permission = map_verdict_to_permission(decision)
    return hook_output(
        permission,
        verdict.finding or decision,
        verdict=decision,
        policy_id=verdict.policy_id,
    )


def main(argv: Optional[List[str]] = None) -> int:
    """Read one PreToolUse JSON object from stdin and print the decision."""

    del argv
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        json.dump(fail_closed(f"invalid PreToolUse JSON: {error}"), sys.stdout)
        sys.stdout.write("\n")
        return 0
    if not isinstance(payload, dict):
        json.dump(fail_closed("PreToolUse payload must be a JSON object"), sys.stdout)
        sys.stdout.write("\n")
        return 0
    json.dump(evaluate_payload(payload), sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# <!-- yxzys:sg:ai -->
