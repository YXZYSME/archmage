# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [integration]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
from datetime import date
from decimal import Decimal
from pathlib import Path

from scripts.check_contribution_contract import validate_contract
from scripts.check_coverage_regression import coverage_decreased
from scripts.check_dco import CommitRecord, has_valid_signoff


def complete_pull_request() -> dict[str, object]:
    body = """
## Approved proposal
Issue: #12
Approval date: 2026-07-29
Expiry date: 2026-08-28
Assigned rank: B-Rank Archmage

## Change summary and design alignment
This focused change preserves the deterministic policy boundary.

## Prompt disclosure
No agentic tools used.

## Regression tests
The regression and compliant paths are both covered.

## Coverage
Base coverage: 91.2
Pull-request coverage: 91.3
Result: no reduction.

## Benchmark evidence
N/A
Reason: Documentation wording cannot affect executable runtime behavior.

## Security impact
No security boundary or trusted input changes.

## Documentation
The contributor policy documentation is updated.

## Backward compatibility
No public runtime interface changes.
"""
    return {"body": body, "labels": [{"name": "B-Rank Archmage"}]}


def test_complete_contract_is_accepted() -> None:
    errors = validate_contract(complete_pull_request(), today=date(2026, 7, 29))
    assert errors == []


def test_contract_requires_exactly_one_rank() -> None:
    pull_request = complete_pull_request()
    pull_request["labels"] = []
    errors = validate_contract(pull_request, today=date(2026, 7, 29))
    assert "pull request must have exactly one ARCHMAGE rank label" in errors


def test_contract_rejects_expired_approval() -> None:
    errors = validate_contract(complete_pull_request(), today=date(2026, 8, 29))
    assert "contribution approval has expired" in errors


def test_dco_signoff_must_match_commit_identity() -> None:
    commit = CommitRecord(
        revision="a" * 40,
        author_email="mage@example.com",
        committer_email="mage@example.com",
        message="fix: preserve policy boundary\n\nSigned-off-by: Mage <mage@example.com>",
    )
    assert has_valid_signoff(commit)


def test_coverage_regression_is_detected() -> None:
    assert coverage_decreased(Decimal("91.20"), Decimal("91.19"))
    assert not coverage_decreased(Decimal("91.20"), Decimal("91.20"))


def test_maintainer_maintenance_form_is_strictly_bounded() -> None:
    template = Path(".github/ISSUE_TEMPLATE/maintainer-maintenance.yml").read_text(encoding="utf-8")
    labels = template.split("labels:", 1)[1].split("body:", 1)[0]

    assert 'title: "maintenance: "' in template
    assert "maintenance" in labels
    assert "status:awaiting-archmage-review" in labels
    assert "status:approved-to-build" not in labels
    assert "SS-Rank Archmage" not in labels

    required_boundaries = (
        "runtime behavior",
        "public API",
        "security boundary",
        "workflow or repository permissions",
        "repository permissions",
        "dependency resolution",
        "release or publishing",
        "package identity",
        "domain routing",
        "license, or governance",
        "full contribution proposal",
        "DCO",
        "every required check",
    )
    for boundary in required_boundaries:
        assert boundary in template
