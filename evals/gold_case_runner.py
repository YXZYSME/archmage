# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [research]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Run exact-decision gold cases and emit drift-aware scorecards."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from archmage import create_default_policy_decision_point

from .benchmark_runtime import (
    action_from_case,
    case_catalog_version,
    context_from_case,
    display_path,
    environment_record,
    load_case_catalog,
    percentile,
    write_json,
    write_markdown,
)

_DEFAULT_CASES = Path(__file__).parent / "cases" / "gold_cases.json"


def run_cases(case_path: Path) -> Dict[str, Any]:
    """Evaluate all catalog cases and calculate exact/intervention metrics."""

    pdp = create_default_policy_decision_point()
    outcomes: List[Dict[str, Any]] = []
    latencies_ms: List[float] = []

    for case in load_case_catalog(case_path):
        action = action_from_case(case)
        context = context_from_case(case)
        started = time.perf_counter_ns()
        verdict = pdp.evaluate(action, context)
        latency_ms = (time.perf_counter_ns() - started) / 1_000_000
        expected = str(case["expected_decision"])
        actual = verdict.decision.value
        latencies_ms.append(latency_ms)
        outcomes.append(
            {
                "case_id": str(case["case_id"]),
                "title": str(case["title"]),
                "suite": str(case.get("suite", "gold")),
                "expected_decision": expected,
                "actual_decision": actual,
                "policy_id": verdict.policy_id,
                "exact_match": actual == expected,
                "latency_ms": round(latency_ms, 6),
            }
        )

    expected_interventions = [
        outcome for outcome in outcomes if outcome["expected_decision"] != "ALLOW"
    ]
    actual_interventions = [
        outcome for outcome in outcomes if outcome["actual_decision"] != "ALLOW"
    ]
    true_interventions = [
        outcome
        for outcome in outcomes
        if outcome["expected_decision"] != "ALLOW" and outcome["actual_decision"] != "ALLOW"
    ]
    false_positives = [
        outcome
        for outcome in outcomes
        if outcome["expected_decision"] == "ALLOW" and outcome["actual_decision"] != "ALLOW"
    ]
    false_negatives = [
        outcome
        for outcome in outcomes
        if outcome["expected_decision"] != "ALLOW" and outcome["actual_decision"] == "ALLOW"
    ]

    return {
        "schema_version": "1.0.0",
        "case_catalog": display_path(case_path),
        "case_catalog_version": case_catalog_version(case_path),
        "environment": environment_record(),
        "evaluator_count": len(pdp.evaluators),
        "metrics": {
            "cases": len(outcomes),
            "exact_matches": sum(bool(outcome["exact_match"]) for outcome in outcomes),
            "exact_accuracy": _ratio(
                sum(bool(outcome["exact_match"]) for outcome in outcomes),
                len(outcomes),
            ),
            "intervention_precision": _ratio(
                len(true_interventions),
                len(actual_interventions),
            ),
            "intervention_recall": _ratio(
                len(true_interventions),
                len(expected_interventions),
            ),
            "false_positives": len(false_positives),
            "false_negatives": len(false_negatives),
            "latency_ms": {
                "p50": round(percentile(latencies_ms, 0.50), 6),
                "p95": round(percentile(latencies_ms, 0.95), 6),
                "max": round(max(latencies_ms), 6),
            },
        },
        "outcomes": outcomes,
    }


def compare_baseline(
    result: Dict[str, Any],
    baseline_path: Optional[Path],
) -> List[Dict[str, str]]:
    """Return decision changes from a prior result artifact."""

    if baseline_path is None:
        return []
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    prior = {
        str(outcome["case_id"]): str(outcome["actual_decision"])
        for outcome in baseline.get("outcomes", [])
    }
    changes = []
    for outcome in result["outcomes"]:
        case_id = str(outcome["case_id"])
        previous_decision = prior.get(case_id)
        current_decision = str(outcome["actual_decision"])
        if previous_decision is not None and previous_decision != current_decision:
            changes.append(
                {
                    "case_id": case_id,
                    "previous_decision": previous_decision,
                    "current_decision": current_decision,
                }
            )
    return changes


def markdown_scorecard(result: Mapping[str, Any]) -> List[str]:
    """Render a compact reader-facing benchmark scorecard."""

    metrics = result["metrics"]
    lines = [
        "<!-- YXZYS | saeng-il ai [research] — © YXZYS @ saengil.ai -->",
        "<!-- yxzys:sg:ai -->",
        "",
        "# ARCHMAGE Gold-Case Scorecard",
        "",
        f"- Cases: {metrics['cases']}",
        f"- Exact decision accuracy: {metrics['exact_accuracy']:.3f}",
        f"- Intervention precision: {metrics['intervention_precision']:.3f}",
        f"- Intervention recall: {metrics['intervention_recall']:.3f}",
        f"- False positives: {metrics['false_positives']}",
        f"- False negatives: {metrics['false_negatives']}",
        f"- Full-PDP latency p95: {metrics['latency_ms']['p95']:.6f} ms",
        "",
        "| Case | Expected | Actual | Policy | Match |",
        "|---|---|---|---|:---:|",
    ]
    for outcome in result["outcomes"]:
        mark = "yes" if outcome["exact_match"] else "no"
        lines.append(
            f"| {outcome['case_id']} | {outcome['expected_decision']} | "
            f"{outcome['actual_decision']} | {outcome['policy_id']} | {mark} |"
        )
    return lines


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the gold suite and return nonzero on mismatch or policy drift."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=_DEFAULT_CASES)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    parser.add_argument("--baseline", type=Path)
    arguments = parser.parse_args(argv)

    result = run_cases(arguments.cases)
    changes = compare_baseline(result, arguments.baseline)
    result["policy_drift"] = changes
    write_json(arguments.json_out, result)
    write_markdown(arguments.markdown_out, markdown_scorecard(result))
    print(json.dumps(result, indent=2, sort_keys=True))

    metrics = result["metrics"]
    return 0 if metrics["exact_matches"] == metrics["cases"] and not changes else 1


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


if __name__ == "__main__":
    raise SystemExit(main())
