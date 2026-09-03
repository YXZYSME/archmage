<!--​‌​‌‌​​‌​‌​‌‌​​​​‌​‌‌​‌​​‌​‌‌​​‌​‌​‌​​‌‌ YXZYS | saeng-il ai [systems] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# ARCHMAGE site handoff

| Field | Value |
|---|---|
| Spec ID | `WEB-ARCHMAGE-001` |
| Site | `archmage.saengil.ai` |
| Status | **PRODUCTION GO — canonical https://archmage.saengil.ai/** |
| Product owner | YXZYS |
| Delivery owner | `YXZYSME/archmage` maintainer |
| Approved proposal | [#11](https://github.com/YXZYSME/archmage/issues/11) |
| Platform | MkDocs Material → GitHub Actions → GitHub Pages |
| Canonical release | `archmage-ai==2.0.0` |
| Snapshot date | 2026-08-25 |
| Production GO | 2026-09-03 |

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
5. `https://archmage.saengil.ai/` is the advertised canonical entry point.
   Certificate coverage for the exact hostname and GitHub Pages HTTPS
   enforcement were accepted on 2026-09-03.
6. GitHub, PyPI, release attestations, and the repository remain the systems of
   record. The site explains and links to them; it does not reproduce mutable
   trust evidence without a version and source.

## Current launch status

YXZYS recorded production **GO** on 2026-09-03 for
`https://archmage.saengil.ai/`. The source and Pages workflow are healthy, DNS
resolves to GitHub Pages, and GitHub reports the custom domain as verified.
Pages API capture ~2026-09-03T13:03Z UTC reports `https_enforced: true` and an
approved Let's Encrypt certificate covering `archmage.saengil.ai` (YR2,
notBefore 2026-09-03, notAfter 2026-12-02). HTTP 301 to HTTPS, critical HTTPS
routes 200 without TLS bypass, and github.io 301 to the HTTPS custom host
were observed at the same capture.

Advertise `https://archmage.saengil.ai/` as the canonical published
documentation host. Remaining launch-critical content, accessibility,
metadata, and validation rows are site-implementation work; they do not
reopen the custom-domain TLS GO.

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

1. Custom-domain TLS/HTTPS GO is recorded; keep advertising
   `https://archmage.saengil.ai/` as canonical.
2. Implement remaining site requirements and close `NOT IMPLEMENTED` rows.
3. Pass local and hosted documentation gates for those implementation changes.
4. Close remaining non-`PASS` implementation and operations rows with captured
   evidence, including recurring certificate/route checks and the seven-day
   post-launch review.
