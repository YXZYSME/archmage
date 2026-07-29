# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Validate the evidence and approval contract of a pull request."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

RANK_LABELS = {
    "B-Rank Archmage",
    "A-Rank Archmage",
    "S-Rank Archmage",
    "SS-Rank Archmage",
}

REQUIRED_SECTIONS = (
    "approved proposal",
    "change summary and design alignment",
    "prompt disclosure",
    "regression tests",
    "coverage",
    "benchmark evidence",
    "security impact",
    "documentation",
    "backward compatibility",
)

_SECTION_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)
_ISSUE_PATTERN = re.compile(
    r"(?:https://github\.com/YXZYSME/archmage/issues/\d+|(?<!\w)#\d+)",
    re.IGNORECASE,
)
_EXPIRY_PATTERN = re.compile(r"Expiry date:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)


def parse_sections(body: str) -> Dict[str, str]:
    """Return normalized level-two Markdown sections keyed by heading."""
    matches = list(_SECTION_PATTERN.finditer(body))
    sections: Dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[match.group(1).strip().casefold()] = body[start:end].strip()
    return sections


def visible_text(value: str) -> str:
    """Remove template comments and Markdown-only formatting from a response."""
    without_comments = _COMMENT_PATTERN.sub("", value)
    return re.sub(r"[\s:#*`_-]+", " ", without_comments).strip()


def label_names(pull_request: Mapping[str, Any]) -> List[str]:
    """Return label names from a GitHub pull-request event."""
    labels = pull_request.get("labels", [])
    if not isinstance(labels, list):
        return []
    return [
        str(label.get("name", ""))
        for label in labels
        if isinstance(label, Mapping) and label.get("name")
    ]


def validate_contract(
    pull_request: Mapping[str, Any],
    *,
    today: Optional[date] = None,
) -> List[str]:
    """Return all contribution-contract violations for one pull request."""
    errors: List[str] = []
    labels = set(label_names(pull_request))
    ranks = sorted(labels & RANK_LABELS)
    if len(ranks) != 1:
        errors.append("pull request must have exactly one ARCHMAGE rank label")

    body = str(pull_request.get("body") or "")
    sections = parse_sections(body)
    for required in REQUIRED_SECTIONS:
        content = visible_text(sections.get(required, ""))
        if len(content) < 12:
            errors.append(f"section '{required}' is missing or incomplete")

    proposal = sections.get("approved proposal", "")
    if proposal and not _ISSUE_PATTERN.search(proposal):
        errors.append("approved proposal must link an ARCHMAGE issue")

    expiry_match = _EXPIRY_PATTERN.search(proposal)
    if not expiry_match:
        errors.append("approved proposal must include 'Expiry date: YYYY-MM-DD'")
    else:
        try:
            expires_on = date.fromisoformat(expiry_match.group(1))
        except ValueError:
            errors.append("approval expiry date is invalid")
        else:
            if expires_on < (today or date.today()):
                errors.append("contribution approval has expired")

    prompt = sections.get("prompt disclosure", "")
    if "no agentic tools used" not in prompt.casefold():
        prompt_lower = prompt.casefold()
        if "### starter prompt" not in prompt_lower:
            errors.append("prompt disclosure must include a starter prompt")
        if "### material follow-up prompts" not in prompt_lower:
            errors.append("prompt disclosure must include material follow-up prompts")

    benchmark_section = sections.get("benchmark evidence", "")
    benchmark = visible_text(benchmark_section)
    if re.search(r"\bn/?a\b", benchmark, re.IGNORECASE):
        reason_match = re.search(r"\breason\s*:\s*(.+)", benchmark_section, re.IGNORECASE)
        if not reason_match or len(reason_match.group(1).strip()) < 20:
            errors.append("benchmark N/A requires a specific reason")

    return errors


def event_pull_request(event: Mapping[str, Any]) -> Mapping[str, Any]:
    """Extract the pull-request object from a GitHub event document."""
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, Mapping):
        raise ValueError("event does not contain a pull_request object")
    return pull_request


def load_event(path: Path) -> Mapping[str, Any]:
    """Load one GitHub event document."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError("event document must be a JSON object")
    return value


def format_errors(errors: Iterable[str]) -> str:
    """Render contract violations for a CI log."""
    return "\n".join(f"- {error}" for error in errors)


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Validate a GitHub pull-request event."""
    parser = argparse.ArgumentParser()
    parser.add_argument("event", type=Path)
    parsed = parser.parse_args(arguments)

    pull_request = event_pull_request(load_event(parsed.event))
    errors = validate_contract(pull_request)
    if errors:
        print("ARCHMAGE contribution contract failed:")
        print(format_errors(errors))
        return 1

    ranks = sorted(set(label_names(pull_request)) & RANK_LABELS)
    print(f"ARCHMAGE contribution contract satisfied ({ranks[0]}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
