# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Require a valid Developer Certificate of Origin sign-off on each commit."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Set

_SIGN_OFF_PATTERN = re.compile(
    r"^Signed-off-by:\s*(.+?)\s*<([^<>]+)>\s*$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class CommitRecord:
    """Identity and message fields required for DCO validation."""

    revision: str
    author_email: str
    committer_email: str
    message: str


def parse_commit_records(output: str) -> List[CommitRecord]:
    """Parse records emitted by the stable git-log format."""
    records: List[CommitRecord] = []
    for raw_record in output.split("\x1e"):
        raw_record = raw_record.strip("\n")
        if not raw_record:
            continue
        fields = raw_record.split("\x00", 5)
        if len(fields) != 6:
            raise ValueError("unexpected git log record")
        revision, _author_name, author_email, _committer_name, committer_email, message = fields
        records.append(
            CommitRecord(
                revision=revision,
                author_email=author_email,
                committer_email=committer_email,
                message=message,
            )
        )
    return records


def load_commits(repository: Path, base: str, head: str) -> List[CommitRecord]:
    """Load commits in the contribution range from a local repository."""
    command = [
        "git",
        "-C",
        str(repository),
        "log",
        "--format=%H%x00%an%x00%ae%x00%cn%x00%ce%x00%B%x1e",
        f"{base}..{head}",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return parse_commit_records(result.stdout)


def signoff_emails(message: str) -> Set[str]:
    """Return normalized DCO sign-off emails from a commit message."""
    return {match.group(2).strip().casefold() for match in _SIGN_OFF_PATTERN.finditer(message)}


def has_valid_signoff(commit: CommitRecord) -> bool:
    """Return whether a sign-off matches the commit author or committer."""
    identities = {
        commit.author_email.strip().casefold(),
        commit.committer_email.strip().casefold(),
    }
    return bool(signoff_emails(commit.message) & identities)


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Validate DCO sign-offs for a commit range."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parsed = parser.parse_args(arguments)

    commits = load_commits(parsed.repository, parsed.base, parsed.head)
    if not commits:
        print("No contribution commits found.")
        return 1

    invalid = [commit for commit in commits if not has_valid_signoff(commit)]
    if invalid:
        print("DCO sign-off is missing or does not match the author/committer:")
        for commit in invalid:
            print(f"- {commit.revision[:12]}")
        print("Amend each commit with: git commit --amend --signoff")
        return 1

    print(f"DCO sign-off verified for {len(commits)} commit(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
