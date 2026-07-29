<!-- YXZYS | saeng-il ai [research] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Security Claims Policy

ARCHMAGE claims only deterministic behavior that is backed by a test or a
versioned benchmark case. It does not generalize those results into claims about
model safety, sandboxing, authentication, or complete attack prevention.

## Claim matrix

| Claim | Evidence | Boundary |
|---|---|---|
| Declared paths outside a workspace are denied after canonical resolution. | `tests/test_adversarial.py`, `tests/test_evaluators.py`, `GC-002` | Applies only to complete `target_paths` routed through the evaluator. |
| Existing symlink and prefix-collision escapes are denied. | `tests/test_adversarial.py` | Does not replace operating-system containment or eliminate time-of-check/time-of-use races in a separate executor. |
| Declared mutations of bundled policy/runtime paths are denied. | `tests/test_evaluators.py`, `GC-003`, `PI-002` | Applies to declared target paths; arbitrary shell effects cannot be inferred completely. |
| Missing actor/task declarations and mutable revision labels are denied. | `tests/test_evaluators.py`, `GC-005`, `GC-008` | Declaration validation is not caller authentication or revision existence verification. |
| An evaluator exception produces a typed fail-closed denial. | `tests/test_integration.py` | Covers the PDP evaluator loop, not failures in an executor after authorization. |
| Default adapters reject unregistered tools and missing required path fields. | `tests/test_generic_adapter.py`, `tests/test_antigravity_adapter.py` | Covers the shipped registries only; custom adapters own their schemas. |
| Non-canonical JSON tool payloads are rejected before evaluation. | `tests/test_generic_adapter.py`, `tests/test_domain.py`, `tests/test_integration.py` | Direct Python hosts must preserve the same canonical schema before constructing proposals. |
| Shell-command proposals require a verified, fresh, digest-bound, single-use approval record under the default policy. | `tests/test_generic_adapter.py`, `tests/test_evaluators.py`, `tests/test_pep.py` | The embedding host must authenticate and authorize the approver and sandbox execution. |
| Exported contract evaluators do not read source from proposal target paths. | `tests/test_contracts.py` | Hosts must provide proposed source content explicitly for contract analysis. |
| Fixed indirect-instruction proposals receive the expected deterministic verdict. | `PI-001`, `PI-002` in `evals/cases/gold_cases.json` | This is not a claim that ARCHMAGE detects injected text or defeats every prompt injection. |

## Publication rules

- Cite the exact release, case catalog, revision, environment, and artifact when
  publishing benchmark numbers.
- Use “denies the evaluated proposal” instead of “prevents the behavior” unless
  the complete executor boundary is in evidence.
- Treat a new security statement as a change requiring a negative test and a
  compliant-path test.
- Do not compare releases across different case catalogs without identifying the
  catalog change.
- Do not publish latency from a dirty tree or describe a local machine result as
  a platform-wide guarantee.
- Keep limitations adjacent to any benchmark or security result.

Release workflows attach benchmark artifacts to the exact build workflow. See
the [benchmark guide](benchmarks.md) and [supply-chain guide](supply-chain.md)
before citing results.
