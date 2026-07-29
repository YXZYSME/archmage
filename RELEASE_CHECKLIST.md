<!-- YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# ARCHMAGE Public Repository Launch Record

This checklist records the public repository launch and separates it from the
later package-publication gate.

## Gate status

| Gate | Status | Evidence or blocker |
|---|---|---|
| Exposure freeze | Complete | The canonical public repository contains only the sanitized `main`; the original history remains in a separate private archive. |
| Current-tree redaction | Green | Gitleaks and targeted identifier/attribution scans pass on the complete working tree. |
| Git-history sanitization | Green | The canonical history has one independently re-audited clean root. The complete original remote remains recoverable from a verified private all-ref bundle. |
| Package layout | Green on candidate | Distribution is `archmage-ai`; hosted distribution smoke tests import `archmage` from `src/archmage`. |
| Python 3.9–3.13 | Green on candidate | Hosted Linux CI and local macOS validation pass on all five declared versions. |
| Build and wheel smoke test | Green on candidate | Hosted and local clean builds passed metadata/content checks and isolated wheel import smoke tests. |
| Supply-chain workflow | Green for repository launch | Actions are SHA-pinned; the release workflow emits checksums, an SPDX SBOM, and GitHub attestations. Package publication remains tag- and environment-gated. |
| PyPI trusted publishing | Green | PyPI accepted the pending `archmage-ai` publisher for `YXZYSME/archmage`, `release.yml`, and the `pypi` environment; no long-lived upload token is used. |
| Security policy | Green | The maintainer approved `SECURITY.md`, including private vulnerability reporting, response targets, scope, coordinated disclosure, and safe harbor. |
| Security scan and threat model | Green locally | The standard scan reviewed 76/76 files; its one medium and three low findings are remediated with regression tests. No high or critical findings were reported. |
| Docs | Green on candidate | MkDocs content, strict hosted build gate, and a SHA-pinned, public-visibility-gated Pages workflow exist. |
| Benchmarks | Green on clean root | Hosted clean-root runners emit revision-bound JSON plus one unified scorecard with case versions and environment details. |
| Public repository controls | Provisioning | Dependabot security updates, secret scanning, push protection, private vulnerability reporting, and strict `main` protection are enabled. The verified Pages custom domain is live while GitHub provisions its TLS certificate. |

## Public repository launch gates

- [x] Full-history and current-tree secret/identifier scans are clean.
- [x] The selected history-sanitization strategy is executed and independently re-audited.
- [x] CI passes lint, type checks, docs, build verification, and tests on Python 3.9–3.13.
- [x] A clean wheel and source distribution pass `twine check` and
      `scripts/verify_distribution.py`.
- [x] The wheel imports `archmage`, `archmage.runtime`, `archmage.adapters`, and
      `archmage.evaluators` in an isolated environment.
- [x] `SECURITY.md` and the threat model are approved and committed.
- [x] The hosted benchmark scorecard identifies its exact revision, case versions, and environment.
- [x] GitHub Pages and repository security controls are enabled.
- [ ] GitHub has issued the custom-domain certificate and HTTPS enforcement is enabled.
- [x] PyPI trusted publishing is configured without a long-lived upload token.
- [x] The maintainer records final go/no-go approval in the private launch-gate issue.

## Package publication gate

- [ ] A tagged release produces downloadable checksums, an SPDX SBOM, verifiable
      attestations, and the first `archmage-ai` publication.

## History-sanitization decision

Two safe public outcomes are available:

1. Rewrite the existing history to remove local paths and normalize
   metadata, then force-update the still-private remote after review.
2. Create a new public root commit from the sanitized tree and retain the private
   history outside the public repository.

The maintainer selected option 2 on July 29, 2026. The existing repository
remains private, and only the newly verified root became public. The complete
pre-sanitization remote is preserved in
`archmage-private-history-20260729.bundle` with SHA-256
`b67217284892ea6845667449c83b596c43d950e087e138f0e7e7accfea9ff4f4`.

## External settings

- GitHub Pages source: GitHub Actions. Public domain:
  `https://archmage.saengil.ai/`. Internal environment: `github-pages`.
- `main` protection: require pull requests and 12 strict status checks, enforce
  rules for administrators, require linear history and resolved conversations,
  and block force pushes and deletion. The review count is zero because GitHub
  does not permit self-approval; `@YXZYSME` is the only repository collaborator
  and final merger.
- Contribution governance: issue-first, scoped 30-day approval, DCO sign-off,
  sanitized prompt evidence, and one B/A/S/SS rank label per pull request.
- `pypi` environment: created with a `v*` tag policy.
- PyPI pending trusted publisher: project `archmage-ai`, owner `YXZYSME`,
  repository `archmage`, workflow `release.yml`, environment `pypi`. PyPI
  converts it to an ordinary trusted publisher on the first successful release.
- Repository security: vulnerability alerts, automated security updates, secret
  scanning, push protection, and private vulnerability reporting are enabled.
