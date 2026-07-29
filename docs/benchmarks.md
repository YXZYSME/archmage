<!-- YXZYS | saeng-il ai [research] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Benchmarks

ARCHMAGE benchmarks policy intervention behavior, not abstract model safety.

## Suites

- Gold-case compliance: expected versus actual typed decisions per policy.
- Repair loop: retries required to turn a repairable proposal into a compliant
  proposal.
- Policy drift: changes from the checked-in decision baseline.
- Latency overhead: local deterministic evaluation p50, p95, and p99.
- Indirect-instruction translation: dangerous tool proposals attributed to
  untrusted repository text.

## Run

```bash
python -m evals.gold_case_runner
python -m evals.repair_loop_benchmark
python -m evals.latency_benchmark --iterations 5000
```

CI and release workflows combine the three revision-bound JSON results into
`SCORECARD.md`. The scorecard records the exact revision, case-catalog versions,
Python runtime, platform, iteration count, and evaluator count. Fixed cases must
have deterministic expected decisions.

## Interpretation

An intervention match shows that the evaluated proposal triggered the expected
policy. It does not prove that an agent cannot bypass the adapter or that every
semantic form of the underlying intent is detected.

Benchmark results should be compared at the same case version and environment.
Do not publish a performance or safety claim without the corresponding result
artifact.
