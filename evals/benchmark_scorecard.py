# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [research]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Combine benchmark results into one provenance-bound Markdown scorecard."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .benchmark_runtime import write_markdown

_ENVIRONMENT_FIELDS = ("revision", "python", "python_implementation", "platform")


def render_scorecard(
    gold: Mapping[str, Any],
    repair: Mapping[str, Any],
    latency: Mapping[str, Any],
) -> List[str]:
    """Render a scorecard after validating shared benchmark provenance."""

    environment = _shared_environment(gold, repair, latency)
    revision = str(environment["revision"])
    if not re.fullmatch(r"[0-9a-fA-F]{7,64}", revision):
        raise ValueError("benchmark revision must be an immutable hexadecimal revision")

    gold_metrics = _mapping(gold, "metrics")
    repair_metrics = _mapping(repair, "metrics")
    latency_results = _mapping(latency, "results")
    full_pdp = _mapping(latency_results, "full_default_pdp")
    wall_time = _mapping(full_pdp, "wall_time_ms")
    cpu_time = _mapping(full_pdp, "cpu_time_ms")

    gold_outcomes = _list_of_mappings(gold, "outcomes")
    indirect_outcomes = [
        outcome for outcome in gold_outcomes if outcome.get("suite") == "indirect_instruction"
    ]
    indirect_matches = sum(bool(outcome.get("exact_match")) for outcome in indirect_outcomes)

    runtime = f"{environment['python_implementation']} {environment['python']}"
    lines = [
        "<!-- YXZYS | saeng-il ai [research] — © YXZYS @ saengil.ai -->",
        "<!-- yxzys:sg:ai -->",
        "",
        "# ARCHMAGE Benchmark Scorecard",
        "",
        "## Provenance",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Revision | `{revision}` |",
        f"| Runtime | {runtime} |",
        f"| Platform | `{environment['platform']}` |",
        (
            "| Result schemas | "
            f"gold `{gold['schema_version']}`; "
            f"repair `{repair['schema_version']}`; "
            f"latency `{latency['schema_version']}` |"
        ),
        "",
        "## Case catalogs",
        "",
        "| Suite | Catalog | Version |",
        "|---|---|---|",
        (f"| Gold cases | `{gold['case_catalog']}` | `{gold['case_catalog_version']}` |"),
        (f"| Repair cases | `{repair['case_catalog']}` | `{repair['case_catalog_version']}` |"),
        "",
        "## Results",
        "",
        "| Suite | Result | Scope |",
        "|---|---:|---|",
        (
            f"| Gold-case compliance | {gold_metrics['exact_matches']}/"
            f"{gold_metrics['cases']} exact; "
            f"{gold_metrics['false_positives']} false positives; "
            f"{gold_metrics['false_negatives']} false negatives | "
            f"Fixed catalog; {gold['evaluator_count']} default evaluators |"
        ),
        (
            f"| Repair loop | {repair_metrics['successes']}/"
            f"{repair_metrics['cases']} compliant; "
            f"{float(repair_metrics['average_retries_to_compliance']):.3f} "
            "average retries | Fixed machine-readable repairs |"
        ),
        (
            f"| Indirect-instruction subset | {indirect_matches}/"
            f"{len(indirect_outcomes)} exact | "
            "Dangerous tool proposals attributed to untrusted repository text |"
        ),
        (
            f"| Full-PDP overhead | {float(wall_time['p95']):.6f} ms p95; "
            f"{float(full_pdp['throughput_evaluations_per_second']):,.3f} "
            "evaluations/s | "
            f"{int(latency['iterations']):,} measured; "
            f"{int(latency['warmup']):,} warmup; "
            f"{full_pdp['evaluator_count']} evaluators |"
        ),
        "",
        "### Runtime detail",
        "",
        f"- Full-PDP CPU p95: {float(cpu_time['p95']):.6f} ms.",
        (f"- Full-PDP peak traced memory: {int(full_pdp['peak_traced_memory_bytes']):,} bytes."),
        "",
        "These deterministic proposal-level results describe this exact artifact "
        "set. They do not establish universal agent safety or prove that a host "
        "cannot bypass the enforcement adapter.",
    ]
    return lines


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Read suite results, validate provenance, and write one scorecard."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--repair", type=Path, required=True)
    parser.add_argument("--latency", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    arguments = parser.parse_args(argv)

    lines = render_scorecard(
        _read_result(arguments.gold),
        _read_result(arguments.repair),
        _read_result(arguments.latency),
    )
    write_markdown(arguments.markdown_out, lines)
    return 0


def _read_result(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _shared_environment(
    gold: Mapping[str, Any],
    repair: Mapping[str, Any],
    latency: Mapping[str, Any],
) -> Mapping[str, Any]:
    environments = [
        _mapping(gold, "environment"),
        _mapping(repair, "environment"),
        _mapping(latency, "environment"),
    ]
    reference = environments[0]
    for field in _ENVIRONMENT_FIELDS:
        if field not in reference:
            raise ValueError(f"gold environment is missing {field}")
        for candidate in environments[1:]:
            if candidate.get(field) != reference[field]:
                raise ValueError(f"benchmark environment mismatch for {field}")
    return reference


def _mapping(values: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = values.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"benchmark field '{key}' must be an object")
    return value


def _list_of_mappings(
    values: Mapping[str, Any],
    key: str,
) -> List[Mapping[str, Any]]:
    value = values.get(key)
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise ValueError(f"benchmark field '{key}' must be an array of objects")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
