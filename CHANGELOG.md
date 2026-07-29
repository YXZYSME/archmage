<!-- YXZYS | saeng-il ai [development] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Changelog

All notable public changes to ARCHMAGE are documented here. The format is based
on Keep a Changelog, and the project uses Semantic Versioning.

## [Unreleased]

### Security

- Require explicit adapter execution context and immutable revision labels.
- Resolve workspace paths canonically and deny prefix/symlink escapes.
- Reject unregistered adapter tools and incomplete path-sensitive proposals.
- Fail closed when a policy evaluator raises unexpectedly.
- Derive audit availability from the configured PEP instead of action metadata.
- Require an explicit obligation for shell-command proposals.
- Bind explicit approvals to the exact action digest, a verifier-accepted
  approver, a freshness window, and single-use consumption.
- Reject ambiguous non-JSON values before payload sizing or action hashing.
- Keep exported contract evaluators side-effect-free by requiring source content
  instead of reading proposal target paths.
- Gate documentation deployment and release publication on public repository
  visibility.

### Added

- Reproducible gold-case, indirect-instruction, repair-loop, drift, and latency
  benchmark runners.
- A provenance-bound benchmark scorecard that rejects mixed revisions and records
  case-catalog versions, runtime details, and headline results.
- MkDocs documentation, security claims, threat model, and limitations.
- SHA-pinned CI, release, documentation, provenance, SBOM, and PyPI trusted-
  publishing workflows.
- Production security scorecard and pre-public launch gate.

### Changed

- Package distribution is `archmage-ai` with the import namespace `archmage`.
- Runtime, adapters, evaluators, and doctrine now use a standard `src` layout.
- Public positioning is narrowed to deterministic pre-execution control for
  coding-agent actions.

[Unreleased]: https://github.com/YXZYSME/archmage/compare/v2.0.0...HEAD
