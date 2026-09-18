# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Tests for the Claude Code PreToolUse verdict mapping hook."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = REPO_ROOT / "plugins" / "archmage" / "hooks" / "pretooluse.py"


def load_hook_module():
    spec = importlib.util.spec_from_file_location("archmage_pretooluse", HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hook = load_hook_module()


class TestClaudeCodePreToolUse(unittest.TestCase):
    def test_verdict_mapping_is_fail_closed(self) -> None:
        self.assertEqual(hook.map_verdict_to_permission("ALLOW"), "allow")
        self.assertEqual(hook.map_verdict_to_permission("DENY"), "deny")
        self.assertEqual(hook.map_verdict_to_permission("ESCALATE"), "ask")
        self.assertEqual(hook.map_verdict_to_permission("REPAIR"), "deny")
        self.assertEqual(hook.map_verdict_to_permission("ALLOW_WITH_OBLIGATIONS"), "ask")
        self.assertEqual(hook.map_verdict_to_permission("unknown"), "deny")
        self.assertEqual(hook.map_verdict_to_permission(""), "deny")

    def test_extracts_write_and_bash_targets(self) -> None:
        self.assertEqual(
            hook.extract_target_paths("Write", {"file_path": "src/feature.py"}),
            ["src/feature.py"],
        )
        self.assertEqual(
            hook.extract_target_paths("Bash", {"command": "ls", "cwd": "/workspace/project"}),
            ["/workspace/project"],
        )

    def test_unregistered_tool_is_denied(self) -> None:
        decision = hook.evaluate_payload(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": "README.md"},
                "cwd": str(REPO_ROOT),
            }
        )
        output = decision["hookSpecificOutput"]
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertIn("unregistered", output["permissionDecisionReason"])

    def test_compliant_write_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "src").mkdir()
            (workspace / "src" / "feature.py").write_text("value = 1\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
            subprocess.run(["git", "add", "src/feature.py"], cwd=workspace, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=mage@example.com",
                    "-c",
                    "user.name=Mage",
                    "commit",
                    "-m",
                    "init",
                ],
                cwd=workspace,
                check=True,
                capture_output=True,
            )
            audit = workspace / "audit.jsonl"
            payload = {
                "tool_name": "Write",
                "tool_input": {"file_path": "src/feature.py", "content": "value = 2\n"},
                "cwd": str(workspace),
                "tool_use_id": "tool-write-1",
            }
            with patch.dict(os.environ, {"ARCHMAGE_AUDIT_LOG": str(audit)}, clear=False):
                decision = hook.evaluate_payload(payload)
            output = decision["hookSpecificOutput"]
            self.assertEqual(output["permissionDecision"], "allow")
            self.assertIn("ALLOW", output["permissionDecisionReason"])

    def test_bash_asks_for_explicit_approval_obligation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "README.md").write_text("demo\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
            subprocess.run(["git", "add", "README.md"], cwd=workspace, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=mage@example.com",
                    "-c",
                    "user.name=Mage",
                    "commit",
                    "-m",
                    "init",
                ],
                cwd=workspace,
                check=True,
                capture_output=True,
            )
            audit = workspace / "audit.jsonl"
            payload = {
                "tool_name": "Bash",
                "tool_input": {"command": "echo hi", "cwd": str(workspace)},
                "cwd": str(workspace),
                "tool_use_id": "tool-bash-1",
            }
            with patch.dict(os.environ, {"ARCHMAGE_AUDIT_LOG": str(audit)}, clear=False):
                decision = hook.evaluate_payload(payload)
            output = decision["hookSpecificOutput"]
            self.assertEqual(output["permissionDecision"], "ask")
            self.assertIn("ALLOW_WITH_OBLIGATIONS", output["permissionDecisionReason"])

    def test_generic_label_is_denied_as_repair(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "utils.py").write_text("pass\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
            subprocess.run(["git", "add", "utils.py"], cwd=workspace, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.email=mage@example.com",
                    "-c",
                    "user.name=Mage",
                    "commit",
                    "-m",
                    "init",
                ],
                cwd=workspace,
                check=True,
                capture_output=True,
            )
            audit = workspace / "audit.jsonl"
            payload = {
                "tool_name": "Write",
                "tool_input": {"file_path": "utils.py", "content": "pass\n"},
                "cwd": str(workspace),
                "tool_use_id": "tool-repair-1",
            }
            with patch.dict(os.environ, {"ARCHMAGE_AUDIT_LOG": str(audit)}, clear=False):
                decision = hook.evaluate_payload(payload)
            output = decision["hookSpecificOutput"]
            self.assertEqual(output["permissionDecision"], "deny")
            self.assertIn("REPAIR", output["permissionDecisionReason"])

    def test_main_fail_closes_on_invalid_json(self) -> None:
        standard_output = io.StringIO()
        with patch("sys.stdin", io.StringIO("not-json\n")), redirect_stdout(standard_output):
            self.assertEqual(hook.main([]), 0)
        payload = json.loads(standard_output.getvalue())
        self.assertEqual(payload["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()


# <!-- yxzys:sg:ai -->
