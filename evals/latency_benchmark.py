# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [research]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Measure deterministic evaluator wall time, CPU time, throughput, and memory."""

from __future__ import annotations

import argparse
import json
import statistics
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from archmage import (
    ActionProposal,
    ActorIdentity,
    PolicyContext,
    PolicyDecisionPoint,
    create_default_policy_decision_point,
)
from archmage.evaluators import ScopeEnforcementEvaluator

from .benchmark_runtime import environment_record, percentile, write_json


def run_latency_benchmark(iterations: int, warmup: int) -> Dict[str, Any]:
    """Measure one evaluator and the full default decision point."""

    if iterations < 100:
        raise ValueError("iterations must be at least 100")
    if warmup < 0:
        raise ValueError("warmup must not be negative")

    action = ActionProposal(
        task_id="latency-task",
        actor=ActorIdentity(actor_id="benchmark-agent", actor_type="agent"),
        operation="write_file",
        tool="write_to_file",
        arguments={"TargetFile": "src/feature.py"},
        target_paths=["src/feature.py"],
        requested_side_effects=[],
        repository_revision="0123456789abcdef0123456789abcdef01234567",
        environment="benchmark",
    )
    context = PolicyContext(
        workspace="/workspace/project",
        environment="benchmark",
        audit_logger_configured=True,
    )
    configurations = {
        "single_scope_evaluator": PolicyDecisionPoint([ScopeEnforcementEvaluator()]),
        "full_default_pdp": create_default_policy_decision_point(),
    }
    results = {}
    for name, pdp in configurations.items():
        results[name] = _measure(pdp, action, context, iterations, warmup)

    return {
        "schema_version": "1.0.0",
        "environment": environment_record(),
        "iterations": iterations,
        "warmup": warmup,
        "results": results,
    }


def _measure(
    pdp: PolicyDecisionPoint,
    action: ActionProposal,
    context: PolicyContext,
    iterations: int,
    warmup: int,
) -> Dict[str, Any]:
    for _ in range(warmup):
        pdp.evaluate(action, context)

    wall_samples_ms: List[float] = []
    cpu_samples_ms: List[float] = []
    total_started = time.perf_counter_ns()
    for _ in range(iterations):
        wall_started = time.perf_counter_ns()
        cpu_started = time.process_time_ns()
        pdp.evaluate(action, context)
        cpu_samples_ms.append((time.process_time_ns() - cpu_started) / 1_000_000)
        wall_samples_ms.append((time.perf_counter_ns() - wall_started) / 1_000_000)
    total_seconds = (time.perf_counter_ns() - total_started) / 1_000_000_000

    tracemalloc.start()
    for _ in range(min(iterations, 1_000)):
        pdp.evaluate(action, context)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "evaluator_count": len(pdp.evaluators),
        "wall_time_ms": _summarize(wall_samples_ms),
        "cpu_time_ms": _summarize(cpu_samples_ms),
        "throughput_evaluations_per_second": round(iterations / total_seconds, 3),
        "peak_traced_memory_bytes": peak_bytes,
    }


def _summarize(values: Sequence[float]) -> Dict[str, float]:
    return {
        "mean": round(statistics.fmean(values), 6),
        "p50": round(percentile(values, 0.50), 6),
        "p95": round(percentile(values, 0.95), 6),
        "p99": round(percentile(values, 0.99), 6),
        "max": round(max(values), 6),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the latency benchmark."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=5_000)
    parser.add_argument("--warmup", type=int, default=100)
    parser.add_argument("--json-out", type=Path)
    arguments = parser.parse_args(argv)

    result = run_latency_benchmark(arguments.iterations, arguments.warmup)
    write_json(arguments.json_out, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
