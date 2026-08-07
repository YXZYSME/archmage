# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Contract tests for the standalone Agent Plugins 1.0.0 bundle."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator

from archmage import __version__
from scripts.build_agent_plugin import build_agent_plugin
from scripts.verify_agent_plugin import validate_agent_plugin


class TestAgentPluginBundle(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.template_root = self.repo_root / "agent-plugin"
        self.schema_root = self.repo_root / "schemas" / "agent-plugins" / "1.0.0"

    def test_template_manifests_match_vendored_agent_plugin_schemas(self) -> None:
        manifest = json.loads((self.template_root / "plugin.json").read_text(encoding="utf-8"))
        mcp = json.loads((self.template_root / "mcp.json").read_text(encoding="utf-8"))
        manifest_schema = json.loads(
            (self.schema_root / "plugin.schema.json").read_text(encoding="utf-8")
        )
        mcp_schema = json.loads((self.schema_root / "mcp.schema.json").read_text(encoding="utf-8"))

        Draft202012Validator(manifest_schema).validate(manifest)
        Draft202012Validator(mcp_schema).validate(mcp)
        self.assertEqual(manifest["version"], __version__)

    def test_builds_a_self_contained_valid_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "archmage-agent-plugin.zip"

            build_agent_plugin(self.repo_root, output)

            self.assertEqual(validate_agent_plugin(output, self.repo_root), [])
            with zipfile.ZipFile(output) as archive:
                members = set(archive.namelist())
            self.assertIn("plugin.json", members)
            self.assertIn("mcp.json", members)
            self.assertIn("skills/archmage/SKILL.md", members)
            self.assertIn("python/archmage/mcp.py", members)
            self.assertIn("ai.saengil.archmage/manifest.yaml", members)

    def test_bundled_mcp_server_starts_without_installing_archmage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            output = temp_root / "archmage-agent-plugin.zip"
            plugin_root = temp_root / "plugin"
            plugin_data = temp_root / "data"
            build_agent_plugin(self.repo_root, output)
            with zipfile.ZipFile(output) as archive:
                archive.extractall(plugin_root)
            plugin_data.mkdir()

            config = json.loads((plugin_root / "mcp.json").read_text(encoding="utf-8"))
            server = config["mcpServers"]["archmage"]
            replacements = {
                "${PLUGIN_ROOT}": str(plugin_root),
                "${PLUGIN_DATA}": str(plugin_data),
            }

            def expand(value: str) -> str:
                for placeholder, replacement in replacements.items():
                    value = value.replace(placeholder, replacement)
                return value

            environment = os.environ.copy()
            environment.update({key: expand(value) for key, value in server["env"].items()})
            command = [sys.executable, *[expand(value) for value in server["args"]]]
            requests = "\n".join(
                [
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "initialize",
                            "params": {},
                        }
                    ),
                    json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
                    "",
                ]
            )

            completed = subprocess.run(
                command,
                check=True,
                capture_output=True,
                cwd=plugin_root,
                env=environment,
                input=requests,
                text=True,
            )

            responses = [json.loads(line) for line in completed.stdout.splitlines()]
            self.assertEqual(responses[0]["result"]["serverInfo"]["name"], "archmage")
            tool_names = {tool["name"] for tool in responses[1]["result"]["tools"]}
            self.assertEqual(
                tool_names,
                {
                    "acknowledge_obligations",
                    "evaluate_action",
                    "inspect_policy",
                    "reconcile_result",
                },
            )

    def test_rejects_archive_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "invalid.zip"
            with zipfile.ZipFile(output, "w") as archive:
                archive.writestr("../escape", "no")

            violations = validate_agent_plugin(output, self.repo_root)

            self.assertIn("archive member escapes the plugin root: ../escape", violations)

    def test_skill_validation_falls_back_when_reference_library_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "archmage-agent-plugin.zip"
            build_agent_plugin(self.repo_root, output)

            with patch.dict(sys.modules, {"skills_ref": None}):
                violations = validate_agent_plugin(output, self.repo_root)

            self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
