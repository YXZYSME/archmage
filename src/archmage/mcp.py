# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Stdio entry point for the ARCHMAGE MCP policy adapter."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from .mcp_server import ArchmageMCPServer
from .runtime.audit import JsonlAuditLogger

__all__ = ["ArchmageMCPServer", "main"]


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ARCHMAGE MCP policy adapter.")
    parser.add_argument(
        "--audit-log",
        default=os.environ.get("ARCHMAGE_AUDIT_LOG"),
        help="Required path for durable policy and reconciliation audit records.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Read newline-delimited MCP JSON-RPC requests from standard input."""

    parser = _argument_parser()
    arguments = parser.parse_args(list(argv) if argv is not None else None)
    if not arguments.audit_log:
        parser.error("--audit-log or ARCHMAGE_AUDIT_LOG is required")

    server = ArchmageMCPServer(audit_logger=JsonlAuditLogger(Path(str(arguments.audit_log))))
    for line in sys.stdin:
        if not line.strip():
            continue
        response: Optional[Dict[str, Any]]
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise ValueError("request must be a JSON object")
            response = server.handle_request(request)
        except (json.JSONDecodeError, ValueError) as error:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {error}"},
            }
        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()


# <!-- yxzys:sg:ai -->
