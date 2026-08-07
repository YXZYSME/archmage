# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Tests for the newline-delimited MCP command entry point."""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from archmage.mcp import main


class TestMCPCommand(unittest.TestCase):
    def test_stdio_loop_emits_responses_and_parse_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            audit_path = Path(directory) / "audit.jsonl"
            standard_input = io.StringIO(
                "\n".join(
                    [
                        "",
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "id": 1,
                                "method": "initialize",
                                "params": {},
                            }
                        ),
                        "[]",
                        "not-json",
                        json.dumps(
                            {
                                "jsonrpc": "2.0",
                                "method": "notifications/initialized",
                            }
                        ),
                        "",
                    ]
                )
            )
            standard_output = io.StringIO()

            with patch("sys.stdin", standard_input), redirect_stdout(standard_output):
                main(["--audit-log", str(audit_path)])

            responses = [json.loads(line) for line in standard_output.getvalue().splitlines()]
            self.assertEqual(responses[0]["result"]["serverInfo"]["name"], "archmage")
            self.assertEqual(
                [response["error"]["code"] for response in responses[1:]], [-32700, -32700]
            )

    def test_environment_can_configure_audit_log(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            standard_output = io.StringIO()
            environment = {"ARCHMAGE_AUDIT_LOG": str(Path(directory) / "audit.jsonl")}
            standard_input = io.StringIO('{"jsonrpc":"2.0","id":1,"method":"ping"}\n')
            with patch.dict(os.environ, environment, clear=False):
                with patch("sys.stdin", standard_input), redirect_stdout(standard_output):
                    main([])

            response = json.loads(standard_output.getvalue())
            self.assertEqual(response["result"], {})

    def test_missing_audit_log_is_rejected(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.stdin", io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    main([])


if __name__ == "__main__":
    unittest.main()


# <!-- yxzys:sg:ai -->
