# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [development]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Validated execution context shared by runtime adapters."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from archmage.runtime._serialization import canonical_json_bytes

_GIT_REVISION = re.compile(r"^[0-9a-fA-F]{7,64}$")
_UNDECLARED_IDENTIFIERS = {"", "none", "unknown"}
_MAX_TOOL_PAYLOAD_BYTES = 1_048_576


@dataclass(frozen=True)
class AdapterExecutionContext:
    """Required identity, scope, and lineage fields for an intercepted tool call."""

    task_id: str
    actor_id: str
    workspace: str
    repository_revision: str
    environment: str

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "AdapterExecutionContext":
        """Validate untrusted adapter metadata and return a normalized context."""

        task_id = _required_text(values, "task_id")
        actor_id = _required_text(values, "actor_id")
        workspace = _required_text(values, "workspace")
        repository_revision = _required_text(values, "git_sha")
        environment = str(values.get("environment", "local")).strip() or "local"

        if task_id.lower() in _UNDECLARED_IDENTIFIERS:
            raise ValueError("context_meta.task_id must declare a concrete task identity")
        if actor_id.lower() in _UNDECLARED_IDENTIFIERS:
            raise ValueError("context_meta.actor_id must declare a concrete actor identity")
        if not Path(workspace).expanduser().is_absolute():
            raise ValueError("context_meta.workspace must be an absolute path")
        if not _GIT_REVISION.fullmatch(repository_revision):
            raise ValueError("context_meta.git_sha must be an immutable hexadecimal revision")

        return cls(
            task_id=task_id,
            actor_id=actor_id,
            workspace=workspace,
            repository_revision=repository_revision.lower(),
            environment=environment,
        )


def _required_text(values: Mapping[str, Any], key: str) -> str:
    value = values.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"context_meta.{key} is required")
    return value.strip()


def validate_tool_payload(tool_name: str, arguments: Mapping[str, Any]) -> None:
    """Reject missing tool identity or payloads large enough to exhaust the gate."""

    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("tool_name must be non-empty")
    try:
        encoded = canonical_json_bytes(arguments)
    except ValueError as error:
        raise ValueError("tool arguments must contain only canonical JSON values") from error
    if len(encoded) > _MAX_TOOL_PAYLOAD_BYTES:
        raise ValueError("tool arguments exceed the 1 MiB adapter limit")
