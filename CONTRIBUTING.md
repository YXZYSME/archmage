<!-- YXZYS | saeng-il ai [development] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Contributing to ARCHMAGE

ARCHMAGE accepts focused changes to deterministic policy enforcement, adapters,
tests, documentation, and reproducible evaluations.

## Development setup

```bash
git clone https://github.com/YXZYSME/archmage.git
cd archmage
python -m venv .venv
source .venv/bin/activate
python -m pip install --editable ".[dev,docs]"
```

Run the same gates used in CI:

```bash
python -m ruff format --check .
python -m ruff check .
python -m mypy
python -m pytest --cov=archmage
python -m mkdocs build --strict
python -m build
python scripts/verify_distribution.py dist/*
```

## Change contract

1. Define or preserve the public interface before implementing behavior.
2. Use the canonical terms in `src/archmage/doctrine/glossary.yaml`.
3. Keep adapters at the boundary; core policy code must not invoke host tools.
4. Add a failing test for the unsafe or incorrect case.
5. Add a passing test for the compliant case.
6. Attach benchmark evidence to performance, reliability, or security claims.
7. Update the policy table, limitations, and compatibility matrix when behavior
   changes.

## Policy evaluators

A new core policy requires:

- a unique `POL-*` identifier;
- a typed `PolicyVerdict`;
- explicit law or invariant ownership;
- documented inputs and failure behavior;
- allow and intervention cases;
- an entry in `manifest.yaml` when it becomes part of the default bundle.

The third-party entry-point API is intentionally not stable yet. Custom evaluators
can be injected explicitly as shown in
[`docs/custom-evaluators.md`](docs/custom-evaluators.md).

## Security reports

Do not open a public issue for a suspected vulnerability. Use the private
disclosure route in `SECURITY.md` after that release-gate policy is approved.

## Conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
