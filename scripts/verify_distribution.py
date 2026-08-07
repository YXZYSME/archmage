# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [development]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Validate ARCHMAGE wheel and source-distribution boundaries."""

from __future__ import annotations

import argparse
import tarfile
import zipfile
from pathlib import Path
from typing import Iterable, Optional, Sequence

_REQUIRED_WHEEL_MEMBERS = {
    "archmage/__init__.py",
    "archmage/adapters/__init__.py",
    "archmage/evaluators/__init__.py",
    "archmage/mcp.py",
    "archmage/mcp_server.py",
    "archmage/runtime/__init__.py",
    "archmage/runtime/audit.py",
}
_REQUIRED_SDIST_MEMBERS = {
    Path("agent-plugin/mcp.json"),
    Path("agent-plugin/plugin.json"),
    Path("schemas/agent-plugins/1.0.0/mcp.schema.json"),
    Path("schemas/agent-plugins/1.0.0/plugin.schema.json"),
    Path("scripts/build_agent_plugin.py"),
    Path("scripts/verify_agent_plugin.py"),
}
_FORBIDDEN_WHEEL_ROOTS = {"adapters", "doctrine", "runtime", "skills", "tests"}
_FORBIDDEN_MEMBER_PARTS = {"__pycache__", ".pytest_cache"}


def validate_wheel(path: Path) -> list[str]:
    """Return contract violations found in a built wheel."""

    violations: list[str] = []
    with zipfile.ZipFile(path) as archive:
        members = set(archive.namelist())

    missing = sorted(_REQUIRED_WHEEL_MEMBERS - members)
    if missing:
        violations.append(f"{path.name}: missing required members: {', '.join(missing)}")

    for member in sorted(members):
        member_path = Path(member)
        if member_path.parts and member_path.parts[0] in _FORBIDDEN_WHEEL_ROOTS:
            violations.append(f"{path.name}: unexpected top-level package: {member}")
        if _FORBIDDEN_MEMBER_PARTS.intersection(member_path.parts):
            violations.append(f"{path.name}: generated cache included: {member}")
        if any(part == "tests" for part in member_path.parts):
            violations.append(f"{path.name}: test code included: {member}")

    return violations


def validate_sdist(path: Path) -> list[str]:
    """Return contract violations found in a source distribution."""

    violations: list[str] = []
    with tarfile.open(path, "r:gz") as archive:
        members = [Path(member.name) for member in archive.getmembers()]

    relative_members = {Path(*member.parts[1:]) for member in members if len(member.parts) > 1}
    missing = sorted(_REQUIRED_SDIST_MEMBERS - relative_members)
    if missing:
        violations.append(
            f"{path.name}: missing Agent Plugin sources: "
            + ", ".join(member.as_posix() for member in missing)
        )

    for member in members:
        if ".git" in member.parts:
            violations.append(f"{path.name}: git metadata included: {member}")
        if _FORBIDDEN_MEMBER_PARTS.intersection(member.parts):
            violations.append(f"{path.name}: generated cache included: {member}")

    return violations


def validate_distributions(paths: Iterable[Path]) -> list[str]:
    """Validate exactly one wheel and one gzipped source distribution."""

    artifacts = list(paths)
    wheels = [path for path in artifacts if path.suffix == ".whl"]
    sdists = [path for path in artifacts if path.name.endswith(".tar.gz")]
    violations: list[str] = []

    if len(wheels) != 1:
        violations.append(f"expected exactly one wheel, found {len(wheels)}")
    if len(sdists) != 1:
        violations.append(f"expected exactly one source distribution, found {len(sdists)}")

    for wheel in wheels:
        violations.extend(validate_wheel(wheel))
    for sdist in sdists:
        violations.extend(validate_sdist(sdist))

    return violations


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run distribution verification and return a process exit code."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", nargs="+", type=Path)
    arguments = parser.parse_args(argv)

    violations = validate_distributions(arguments.artifacts)
    if violations:
        for violation in violations:
            print(f"ERROR: {violation}")
        return 1

    print("Distribution contract verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
