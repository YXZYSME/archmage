# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [research]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Measure deterministic proposal repair and resubmission outcomes."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from archmage import VerdictDecision, create_default_policy_decision_point

from .benchmark_runtime import (
    action_from_case,
    case_catalog_version,
    context_from_case,
    display_path,
    environment_record,
    load_case_catalog,
    write_json,
    write_markdown,
)

_DEFAULT_CASES = Path(__file__).parent / "cases" / "repair_cases.json"


def run_repair_cases(case_path: Path) -> Dict[str, Any]:
    """Run repair sequences and report retries required for compliance."""

    pdp = create_default_policy_decision_point()
    outcomes: List[Dict[str, Any]] = []

    for case in load_case_catalog(case_path):
        action = action_from_case(case)
        context = context_from_case(case)
        decisions = []
        repairs = list(case.get("repairs", []))
        retries = 0

        while True:
            verdict = pdp.evaluate(action, context)
            decisions.append(verdict.decision.value)
            if verdict.decision == VerdictDecision.ALLOW:
                break
            if verdict.decision != VerdictDecision.REPAIR or retries >= len(repairs):
                break
            action = _apply_repair(action, repairs[retries])
            retries += 1

        outcomes.append(
            {
                "case_id": str(case["case_id"]),
                "title": str(case["title"]),
                "decisions": decisions,
                "retries": retries,
                "success": decisions[-1] == "ALLOW",
            }
        )

    successes = [outcome for outcome in outcomes if outcome["success"]]
    return {
        "schema_version": "1.0.0",
        "case_catalog": display_path(case_path),
        "case_catalog_version": case_catalog_version(case_path),
        "environment": environment_record(),
        "metrics": {
            "cases": len(outcomes),
            "successes": len(successes),
            "repair_success_rate": len(successes) / len(outcomes) if outcomes else 1.0,
            "average_retries_to_compliance": (
                sum(int(outcome["retries"]) for outcome in successes) / len(successes)
                if successes
                else None
            ),
        },
        "outcomes": outcomes,
    }


def markdown_scorecard(result: Mapping[str, Any]) -> List[str]:
    """Render a repair-loop scorecard."""

    metrics = result["metrics"]
    lines = [
        "<!-- YXZYS | saeng-il ai [research] — © YXZYS @ saengil.ai -->",
        "<!-- yxzys:sg:ai -->",
        "",
        "# ARCHMAGE Repair-Loop Scorecard",
        "",
        f"- Cases: {metrics['cases']}",
        f"- Repair success rate: {metrics['repair_success_rate']:.3f}",
        f"- Average retries to compliance: {metrics['average_retries_to_compliance']}",
        "",
        "| Case | Decision sequence | Retries | Success |",
        "|---|---|---:|:---:|",
    ]
    for outcome in result["outcomes"]:
        sequence = " → ".join(outcome["decisions"])
        mark = "yes" if outcome["success"] else "no"
        lines.append(f"| {outcome['case_id']} | {sequence} | {outcome['retries']} | {mark} |")
    return lines


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run repair cases and return nonzero when a case cannot reach compliance."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=_DEFAULT_CASES)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    arguments = parser.parse_args(argv)

    result = run_repair_cases(arguments.cases)
    write_json(arguments.json_out, result)
    write_markdown(arguments.markdown_out, markdown_scorecard(result))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["metrics"]["successes"] == result["metrics"]["cases"] else 1


def _apply_repair(action: Any, repair: Mapping[str, Any]) -> Any:
    arguments = dict(action.arguments)
    arguments.update(dict(repair.get("arguments", {})))
    target_paths = [str(path) for path in repair.get("target_paths", action.target_paths)]
    return replace(action, arguments=arguments, target_paths=target_paths)


if __name__ == "__main__":
    raise SystemExit(main())
