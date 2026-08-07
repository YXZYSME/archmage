# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Validate the ARCHMAGE Agent Plugin archive and its portable contracts."""

from __future__ import annotations

import argparse
import json
import re
import stat
import tempfile
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Sequence, Tuple

from jsonschema import Draft202012Validator
from strictyaml import YAMLValidationError, dirty_load

_REQUIRED_MEMBERS = {
    "LICENSE",
    "plugin.json",
    "mcp.json",
    "skills/archmage/SKILL.md",
    "python/archmage/__init__.py",
    "python/archmage/mcp.py",
    "python/archmage/mcp_server.py",
    "ai.saengil.archmage/extension.json",
    "ai.saengil.archmage/manifest.yaml",
}
_ALLOWED_SKILL_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
_SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _unsafe_archive_member(member: str) -> bool:
    normalized = member.replace("\\", "/")
    path = PurePosixPath(normalized)
    return (
        "\x00" in member
        or path.is_absolute()
        or ".." in path.parts
        or bool(path.parts and path.parts[0].endswith(":"))
    )


def _load_json(archive: zipfile.ZipFile, member: str) -> Tuple[Optional[Any], List[str]]:
    try:
        return json.loads(archive.read(member).decode("utf-8")), []
    except KeyError:
        return None, [f"missing required member: {member}"]
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return None, [f"{member}: invalid JSON: {error}"]


def _validate_schema(
    document: Any,
    schema_path: Path,
    document_name: str,
) -> List[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    violations: List[str] = []
    for error in Draft202012Validator(schema).iter_errors(document):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        violations.append(f"{document_name}:{location}: {error.message}")
    return violations


def _skill_frontmatter(text: str) -> Tuple[Optional[Dict[str, Any]], str, List[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "", ["skills/archmage/SKILL.md: missing YAML frontmatter"]
    try:
        closing_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration:
        return None, "", ["skills/archmage/SKILL.md: unterminated YAML frontmatter"]

    try:
        loaded = dirty_load(
            "\n".join(lines[1:closing_index]),
            allow_flow_style=True,
        ).data
    except YAMLValidationError as error:
        return None, "", [f"skills/archmage/SKILL.md: invalid YAML: {error}"]
    if not isinstance(loaded, dict):
        return None, "", ["skills/archmage/SKILL.md: frontmatter must be a mapping"]
    return loaded, "\n".join(lines[closing_index + 1 :]).strip(), []


def _validate_skill(text: str) -> List[str]:
    metadata, body, violations = _skill_frontmatter(text)
    if metadata is None:
        return violations

    unknown_fields = sorted(set(metadata) - _ALLOWED_SKILL_FIELDS)
    if unknown_fields:
        violations.append(
            "skills/archmage/SKILL.md: unsupported frontmatter fields: " + ", ".join(unknown_fields)
        )
    name = metadata.get("name")
    if not isinstance(name, str) or not _SKILL_NAME.fullmatch(name) or len(name) > 64:
        violations.append("skills/archmage/SKILL.md: invalid skill name")
    elif name != "archmage":
        violations.append("skills/archmage/SKILL.md: name must match parent directory")
    description = metadata.get("description")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        violations.append("skills/archmage/SKILL.md: invalid description")
    compatibility = metadata.get("compatibility")
    if compatibility is not None and (
        not isinstance(compatibility, str) or not 1 <= len(compatibility) <= 500
    ):
        violations.append("skills/archmage/SKILL.md: invalid compatibility")
    custom_metadata = metadata.get("metadata")
    if custom_metadata is not None and (
        not isinstance(custom_metadata, dict)
        or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in custom_metadata.items()
        )
    ):
        violations.append("skills/archmage/SKILL.md: metadata values must be strings")
    if not body:
        violations.append("skills/archmage/SKILL.md: instruction body is empty")

    try:
        from skills_ref import validate as validate_agent_skill
    except ImportError:
        pass
    else:
        with tempfile.TemporaryDirectory() as directory:
            skill_directory = Path(directory) / "archmage"
            skill_directory.mkdir()
            (skill_directory / "SKILL.md").write_text(text, encoding="utf-8")
            violations.extend(
                f"skills/archmage/SKILL.md: {error}"
                for error in validate_agent_skill(skill_directory)
            )
    return violations


def _validate_mcp_semantics(document: Any) -> List[str]:
    try:
        server = document["mcpServers"]["archmage"]
    except (KeyError, TypeError):
        return ["mcp.json: missing archmage server"]
    violations: List[str] = []
    if server.get("env", {}).get("PYTHONPATH") != "${PLUGIN_ROOT}/python":
        violations.append("mcp.json: archmage must load the bundled Python runtime")
    arguments = server.get("args", [])
    if "--audit-log" not in arguments or "${PLUGIN_DATA}/audit.jsonl" not in arguments:
        violations.append("mcp.json: archmage must configure a durable plugin-data audit log")
    return violations


def validate_agent_plugin(path: Path, repo_root: Path) -> List[str]:
    """Return all portable bundle contract violations."""

    violations: List[str] = []
    schema_root = repo_root / "schemas" / "agent-plugins" / "1.0.0"
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as error:
        return [f"invalid plugin archive: {error}"]

    with archive:
        names = archive.namelist()
        for name, count in Counter(names).items():
            if count > 1:
                violations.append(f"duplicate archive member: {name}")
        for info in archive.infolist():
            if _unsafe_archive_member(info.filename):
                violations.append(f"archive member escapes the plugin root: {info.filename}")
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                violations.append(f"archive member is a symbolic link: {info.filename}")
            member_path = PurePosixPath(info.filename)
            if "__pycache__" in member_path.parts or member_path.suffix in {".pyc", ".pyo"}:
                violations.append(f"generated Python cache included: {info.filename}")

        missing = sorted(_REQUIRED_MEMBERS - set(names))
        for member in missing:
            violations.append(f"missing required member: {member}")

        plugin, errors = _load_json(archive, "plugin.json")
        violations.extend(errors)
        if plugin is not None:
            violations.extend(
                _validate_schema(
                    plugin,
                    schema_root / "plugin.schema.json",
                    "plugin.json",
                )
            )

        mcp, errors = _load_json(archive, "mcp.json")
        violations.extend(errors)
        if mcp is not None:
            violations.extend(
                _validate_schema(
                    mcp,
                    schema_root / "mcp.schema.json",
                    "mcp.json",
                )
            )
            violations.extend(_validate_mcp_semantics(mcp))

        try:
            skill_text = archive.read("skills/archmage/SKILL.md").decode("utf-8")
        except KeyError:
            pass
        except UnicodeDecodeError as error:
            violations.append(f"skills/archmage/SKILL.md: invalid UTF-8: {error}")
        else:
            violations.extend(_validate_skill(skill_text))

    return violations


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    arguments = parser.parse_args(argv)
    violations = validate_agent_plugin(arguments.archive, arguments.repo_root)
    if violations:
        for violation in violations:
            print(f"ERROR: {violation}")
        return 1
    print("Agent Plugin contract verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# <!-- yxzys:sg:ai -->
