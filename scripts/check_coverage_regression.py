# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Reject pull requests that reduce measured ARCHMAGE coverage."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Mapping, Optional, Sequence


def load_coverage(path: Path) -> Decimal:
    """Load the exact total coverage percentage from coverage.py JSON."""
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    totals = document.get("totals")
    if not isinstance(totals, Mapping):
        raise ValueError(f"{path} does not contain coverage totals")
    percent = totals.get("percent_covered")
    if not isinstance(percent, (int, float)):
        raise ValueError(f"{path} does not contain numeric percent_covered")
    return Decimal(str(percent))


def coverage_decreased(base: Decimal, candidate: Decimal) -> bool:
    """Return whether candidate coverage is lower than base coverage."""
    return candidate < base


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Compare base and candidate coverage reports."""
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("candidate", type=Path)
    parsed = parser.parse_args(arguments)

    base = load_coverage(parsed.base)
    candidate = load_coverage(parsed.candidate)
    print(f"Base coverage: {base:.4f}%")
    print(f"Pull-request coverage: {candidate:.4f}%")
    if coverage_decreased(base, candidate):
        print(f"Coverage regression: {base - candidate:.4f} percentage points")
        return 1

    print("Coverage did not decrease.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
