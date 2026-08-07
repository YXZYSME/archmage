# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Build the self-contained ARCHMAGE Agent Plugin release archive."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Dict, Iterator, Optional, Sequence, Tuple

_EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def _portable_files(repo_root: Path) -> Iterator[Tuple[str, Path]]:
    template_root = repo_root / "agent-plugin"
    for source in sorted(template_root.rglob("*")):
        if source.is_file():
            yield source.relative_to(template_root).as_posix(), source

    yield "skills/archmage/SKILL.md", repo_root / "SKILL.md"
    yield "ai.saengil.archmage/manifest.yaml", repo_root / "manifest.yaml"
    yield "LICENSE", repo_root / "LICENSE"

    package_root = repo_root / "src" / "archmage"
    for source in sorted(package_root.rglob("*")):
        relative = source.relative_to(package_root)
        if (
            source.is_file()
            and not _EXCLUDED_PARTS.intersection(relative.parts)
            and source.suffix not in {".pyc", ".pyo"}
        ):
            yield f"python/archmage/{relative.as_posix()}", source


def build_agent_plugin(repo_root: Path, output_path: Path) -> Path:
    """Build a reproducible ZIP whose root is the plugin root."""

    repo_root = repo_root.resolve()
    output_path = output_path.resolve()
    members: Dict[str, Path] = {}
    for archive_name, source in _portable_files(repo_root):
        if archive_name in members:
            raise ValueError(f"duplicate plugin member: {archive_name}")
        if source.is_symlink():
            raise ValueError(f"plugin source must not be a symbolic link: {source}")
        if not source.is_file():
            raise FileNotFoundError(f"required plugin source is missing: {source}")
        members[archive_name] = source

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for archive_name, source in sorted(members.items()):
            info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())
    return output_path


def _default_output_path(repo_root: Path, output_directory: Optional[Path]) -> Path:
    manifest = json.loads((repo_root / "agent-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = str(manifest["version"])
    directory = output_directory or repo_root / "dist"
    return directory / f"archmage-agent-plugin-{version}.zip"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--output-directory", type=Path)
    arguments = parser.parse_args(argv)
    if arguments.output is not None and arguments.output_directory is not None:
        parser.error("output and --output-directory are mutually exclusive")
    output_path = arguments.output or _default_output_path(
        arguments.repo_root,
        arguments.output_directory,
    )
    built_path = build_agent_plugin(arguments.repo_root, output_path)
    print(built_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# <!-- yxzys:sg:ai -->
