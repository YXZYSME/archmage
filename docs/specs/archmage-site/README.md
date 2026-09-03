<!--​‌​‌‌​​‌​‌​‌‌​​​​‌​‌‌​‌​​‌​‌‌​​‌​‌​‌​​‌‌ YXZYS | saeng-il ai [systems] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# ARCHMAGE site handoff

| Field | Value |
|---|---|
| Spec ID | `WEB-ARCHMAGE-001` |
| Site | `archmage.saengil.ai` |
| Status | **READY FOR IMPLEMENTATION — CANONICAL HOST NO-GO** |
| Product owner | YXZYS |
| Delivery owner | `YXZYSME/archmage` maintainer |
| Approved proposal | [#11](https://github.com/YXZYSME/archmage/issues/11) |
| Platform | MkDocs Material → GitHub Actions → GitHub Pages |
| Canonical release | `archmage-ai==2.0.0` |
| Snapshot date | 2026-08-25 |
| TLS evidence refresh | 2026-09-03 |

## Purpose

This package is the source of truth for implementing, validating, launching, and
operating the ARCHMAGE documentation site. It turns the existing documentation
and Pages deployment into a handoff contract that another engineer can execute
without rediscovering product intent, security boundaries, domain ownership, or
launch criteria.

The site is a documentation-first developer portal. It is not a separate product
application, account surface, policy service, or marketing claims layer.

## Artifact map

| Artifact | Consumer | Decision it owns |
|---|---|---|
| [Site specification](SITE_SPEC.md) | Product, design, content, frontend | Audience, journeys, information architecture, visual system, content rules, accessibility, SEO, and performance |
| [Technical handoff](TECHNICAL_HANDOFF.md) | Platform and repository maintainer | Hosting architecture, source ownership, build/deploy contract, DNS/TLS boundary, security, and change control |
| [Launch runbook](LAUNCH_RUNBOOK.md) | Repository admin and DNS owner | Certificate recovery, HTTPS activation, verification, evidence capture, rollback, and incident response |
| [Acceptance matrix](ACCEPTANCE_MATRIX.md) | Reviewer and launch approver | Traceable requirements, present baseline, evidence, owners, and go/no-go state |

## Locked handoff decisions

1. MkDocs Material and GitHub Pages remain the v1 implementation. A framework or
   hosting migration requires a separate proposal.
2. The primary audience is coding-agent platform engineers, security reviewers,
   and integrators evaluating or adopting ARCHMAGE.
3. The site is public and static. It has no authentication, forms, user-provided
   data, cookies, or analytics at handoff.
4. Security language MUST remain bounded by the published limitations, threat
   model, tests, and revision-bound release evidence.
5. `https://archmage.saengil.ai/` becomes the advertised canonical entry point
   only after its certificate covers the exact hostname and GitHub Pages enforces
   HTTPS.
6. GitHub, PyPI, release attestations, and the repository remain the systems of
   record. The site explains and links to them; it does not reproduce mutable
   trust evidence without a version and source.

## Current launch status

The source and Pages workflow are healthy, DNS resolves to GitHub Pages, and
GitHub reports the custom domain as verified. A valid Let's Encrypt certificate
covering `archmage.saengil.ai` was observed at the edge on 2026-09-03 (issued
2026-09-03, Let's Encrypt YR2). That observation does **not** make the custom
host canonical.

Remaining TLS launch work is evidence, not issuance: Pages API
`https_enforced` has not been recaptured, and a formal launch-evidence package
has not been recorded. An HTTP 301 to `https://archmage.saengil.ai/` was also
observed from one public vantage point on 2026-09-03; treat that as
`READY TO VERIFY`, not as accepted HTTPS enforcement.

Independent of TLS, many launch-critical content, accessibility, metadata, and
validation rows remain non-`PASS`. Until every launch-critical row passes and a
maintainer records go, public release communications MUST use immutable GitHub
documentation links or the repository documentation source.

## Handoff-ready definition

The specification package is ready for implementation when:

- product scope and non-goals are explicit;
- every target route has a purpose, owner, and required evidence;
- design, accessibility, performance, privacy, and search requirements are
  testable;
- deployment, domain, certificate, rollback, and evidence procedures identify
  the responsible role;
- open implementation work is visible in the acceptance matrix; and
- no credential, provider token, private dashboard URL, or private repository
  history is embedded in the handoff.

## Execution order

1. Implement the site requirements and close `NOT IMPLEMENTED` rows.
2. Pass local and hosted documentation gates.
3. Recapture Pages API `https_enforced` and the formal TLS launch-evidence
   package. Certificate recovery is no longer the unique external blocker.
4. Close all `BLOCKED` and `READY TO VERIFY` launch rows with captured evidence.
5. Record maintainer go/no-go approval and advertise the canonical domain.
