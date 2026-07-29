# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [development]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Canonical workspace-path resolution for policy evaluators."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ResolvedWorkspaceTarget:
    """A target resolved against a declared workspace boundary."""

    workspace: Path
    target: Path
    relative_path: Optional[Path]

    @property
    def is_within_workspace(self) -> bool:
        """Return whether the resolved target is contained by the workspace."""

        return self.relative_path is not None


def resolve_workspace_target(workspace: str, target: str) -> ResolvedWorkspaceTarget:
    """Resolve a target without relying on vulnerable string-prefix comparisons."""

    if not workspace or not target:
        raise ValueError("workspace and target must be non-empty")

    resolved_workspace = Path(workspace).expanduser().resolve(strict=False)
    candidate = Path(target).expanduser()
    if not candidate.is_absolute():
        candidate = resolved_workspace / candidate
    resolved_target = candidate.resolve(strict=False)

    try:
        relative_path: Optional[Path] = resolved_target.relative_to(resolved_workspace)
    except ValueError:
        relative_path = None

    return ResolvedWorkspaceTarget(
        workspace=resolved_workspace,
        target=resolved_target,
        relative_path=relative_path,
    )
