# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Contract tests for registry listing drafts and Claude Code marketplace files."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skills_ref import validate as validate_agent_skill

from archmage import __version__

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestRegistryListings(unittest.TestCase):
    def test_readme_contains_pypi_mcp_name_marker(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("<!-- mcp-name: io.github.YXZYSME/archmage -->", readme)
        self.assertNotIn("mcpName", (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    def test_server_json_matches_pypi_stdio_identity(self) -> None:
        server = json.loads((REPO_ROOT / "server.json").read_text(encoding="utf-8"))
        self.assertEqual(
            server["$schema"],
            "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
        )
        self.assertEqual(server["name"], "io.github.YXZYSME/archmage")
        self.assertEqual(server["version"], __version__)
        self.assertLessEqual(len(server["description"]), 100)
        self.assertEqual(len(server["packages"]), 1)
        package = server["packages"][0]
        self.assertEqual(package["registryType"], "pypi")
        self.assertEqual(package["identifier"], "archmage-ai")
        self.assertEqual(package["version"], __version__)
        self.assertEqual(package["transport"]["type"], "stdio")
        self.assertEqual(package["runtimeHint"], "uvx")
        self.assertNotIn("remotes", server)
        env_names = [item["name"] for item in package["environmentVariables"]]
        self.assertIn("ARCHMAGE_AUDIT_LOG", env_names)
        entrypoints = [item.get("value") for item in package["packageArguments"]]
        self.assertIn("archmage-mcp", entrypoints)

    def test_marketplace_lists_archmage_plugin(self) -> None:
        marketplace = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["name"], "archmage")
        self.assertEqual(marketplace["owner"]["name"], "YXZYSME")
        self.assertEqual(len(marketplace["plugins"]), 1)
        plugin = marketplace["plugins"][0]
        self.assertEqual(plugin["name"], "archmage")
        self.assertEqual(plugin["source"], "./plugins/archmage")
        plugin_root = REPO_ROOT / "plugins" / "archmage"
        self.assertTrue((plugin_root / ".claude-plugin" / "plugin.json").is_file())
        self.assertTrue((plugin_root / ".mcp.json").is_file())
        self.assertTrue((plugin_root / "hooks" / "hooks.json").is_file())
        self.assertTrue((plugin_root / "hooks" / "pretooluse.py").is_file())

    def test_claude_plugin_wires_local_stdio_mcp(self) -> None:
        plugin = json.loads(
            (REPO_ROOT / "plugins" / "archmage" / ".claude-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        mcp = json.loads(
            (REPO_ROOT / "plugins" / "archmage" / ".mcp.json").read_text(encoding="utf-8")
        )
        hooks = json.loads(
            (REPO_ROOT / "plugins" / "archmage" / "hooks" / "hooks.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(plugin["name"], "archmage")
        self.assertEqual(plugin["version"], __version__)
        server = mcp["mcpServers"]["archmage"]
        self.assertEqual(server["command"], "python")
        self.assertEqual(server["args"], ["-m", "archmage.mcp"])
        self.assertIn("ARCHMAGE_AUDIT_LOG", server["env"])
        self.assertIn("PreToolUse", hooks["hooks"])

    def test_glama_json_names_maintainer(self) -> None:
        glama = json.loads((REPO_ROOT / "glama.json").read_text(encoding="utf-8"))
        self.assertEqual(glama["maintainers"], ["YXZYSME"])

    def test_root_skill_frontmatter_matches_agentskills_spec(self) -> None:
        text = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: archmage", text)
        self.assertIn("license: Apache-2.0", text)
        with tempfile.TemporaryDirectory() as directory:
            skill_directory = Path(directory) / "archmage"
            skill_directory.mkdir()
            (skill_directory / "SKILL.md").write_text(text, encoding="utf-8")
            self.assertEqual(validate_agent_skill(skill_directory), [])

    def test_agent_plugin_template_is_untouched(self) -> None:
        manifest = json.loads(
            (REPO_ROOT / "agent-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "archmage")
        self.assertEqual(
            manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
        )


if __name__ == "__main__":
    unittest.main()


# <!-- yxzys:sg:ai -->
