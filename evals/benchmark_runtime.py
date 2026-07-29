# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [research]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Shared contracts for deterministic ARCHMAGE benchmark runners."""

from __future__ import annotations

import json
import os
import platform
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from archmage import (
    ActionProposal,
    ActorIdentity,
    PolicyContext,
    ProposedEffect,
)


def load_case_catalog(path: Path) -> List[Dict[str, Any]]:
    """Load a versioned case catalog from JSON."""

    document = json.loads(path.read_text(encoding="utf-8"))
    version = document.get("schema_version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"{path} must contain a non-empty 'schema_version'")
    cases = document.get("cases")
    if not isinstance(cases, list):
        raise ValueError(f"{path} must contain a 'cases' array")
    return [dict(case) for case in cases]


def case_catalog_version(path: Path) -> str:
    """Return the required schema version for a case catalog."""

    document = json.loads(path.read_text(encoding="utf-8"))
    version = document.get("schema_version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"{path} must contain a non-empty 'schema_version'")
    return version


def action_from_case(case: Mapping[str, Any]) -> ActionProposal:
    """Build an action proposal from a benchmark case."""

    proposal = _mapping(case, "proposal")
    actor_data = _mapping(proposal, "actor")
    effects = [
        ProposedEffect(
            effect_type=str(effect["effect_type"]),
            target=str(effect["target"]),
            payload=dict(effect.get("payload", {})),
        )
        for effect in proposal.get("requested_side_effects", [])
    ]
    return ActionProposal(
        task_id=str(proposal["task_id"]),
        actor=ActorIdentity(
            actor_id=str(actor_data["actor_id"]),
            actor_type=str(actor_data["actor_type"]),
        ),
        operation=str(proposal["operation"]),
        tool=str(proposal["tool"]),
        arguments=dict(proposal.get("arguments", {})),
        target_paths=[str(path) for path in proposal.get("target_paths", [])],
        requested_side_effects=effects,
        repository_revision=str(proposal["repository_revision"]),
        environment=str(proposal.get("environment", "benchmark")),
    )


def context_from_case(case: Mapping[str, Any]) -> PolicyContext:
    """Build a policy context from a benchmark case."""

    context = _mapping(case, "context")
    return PolicyContext(
        workspace=str(context["workspace"]),
        environment=str(context.get("environment", "benchmark")),
        audit_logger_configured=bool(context["audit_logger_configured"]),
    )


def environment_record() -> Dict[str, Any]:
    """Return environment metadata required for benchmark interpretation."""

    supplied_revision = os.environ.get("ARCHMAGE_BENCHMARK_REVISION")
    if supplied_revision and not re.fullmatch(r"[0-9a-fA-F]{7,64}", supplied_revision):
        raise ValueError("ARCHMAGE_BENCHMARK_REVISION must be an immutable hexadecimal revision")

    return {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "revision": supplied_revision.lower() if supplied_revision else _git_revision(),
    }


def display_path(path: Path) -> str:
    """Return a repository-relative path without leaking local workspace names."""

    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def write_json(path: Optional[Path], result: Mapping[str, Any]) -> None:
    """Write a deterministic JSON result when an output path is supplied."""

    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_markdown(path: Optional[Path], lines: Iterable[str]) -> None:
    """Write a Markdown scorecard when an output path is supplied."""

    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def percentile(values: Sequence[float], percentile_value: float) -> float:
    """Calculate a nearest-rank percentile for a non-empty sample."""

    if not values:
        raise ValueError("cannot calculate a percentile for an empty sample")
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * percentile_value)))
    return ordered[index]


def _mapping(values: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = values.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"case field '{key}' must be an object")
    return value


def _git_revision() -> str:
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=normal"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        return f"{revision}-dirty" if dirty else revision
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
