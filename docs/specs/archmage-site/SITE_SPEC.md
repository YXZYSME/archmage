<!--​‌​‌‌​​‌​‌​‌‌​​​​‌​‌‌​‌​​‌​‌‌​​‌​‌​‌​​‌‌ YXZYS | saeng-il ai [systems] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# WEB-ARCHMAGE-001 — Site specification

| Field | Value |
|---|---|
| Status | READY FOR IMPLEMENTATION |
| Phase | Public documentation v1 |
| Owner | YXZYS |
| Updated | 2026-08-25 |
| Canonical host | `archmage.saengil.ai` after TLS acceptance |

## Intent

`archmage.saengil.ai` MUST help a technically sophisticated visitor answer four
questions quickly:

1. What does ARCHMAGE control?
2. What does it deliberately not control?
3. Can I install and evaluate it safely?
4. What evidence supports the release and its security claims?

The experience SHOULD feel exact, calm, technical, and slightly arcane without
obscuring implementation facts. Trust comes from reproducible evidence and
clearly stated boundaries, not superlatives.

## Audience and jobs

| Priority | Audience | Job to be done | Success signal |
|---:|---|---|---|
| 1 | Coding-agent platform engineer | Decide whether ARCHMAGE fits a tool-call enforcement boundary | Reaches architecture, limitations, and an integration path without guessing |
| 2 | Evaluating developer | Install the stable package and produce one deterministic verdict | Completes the quickstart in five minutes or less |
| 3 | Security or release reviewer | Check claims, threat assumptions, artifacts, and attestations | Finds evidence tied to an exact release and revision |
| 4 | Integration maintainer | Choose a native adapter, MCP edge, or custom evaluator path | Understands the PEP/PDP boundary and host obligations |
| 5 | Contributor or reporter | Find contribution and private vulnerability routes | Reaches the correct route without opening sensitive material publicly |

## Product principles

- **Boundary before benefit:** explain what the host must enforce adjacent to
  every security benefit.
- **Install before abstraction:** provide one stable package command and one
  complete example before deeper concepts.
- **Evidence before claims:** benchmark and supply-chain statements link to an
  exact release artifact or workflow.
- **One canonical vocabulary:** use the doctrine glossary and existing runtime
  names; do not create competing names for PEP, PDP, proposal, verdict, repair,
  obligation, or adapter.
- **Progressive depth:** the home page orients, the quickstart proves, concept
  pages explain, and evidence pages support review.
- **Static by default:** every critical path works without accounts, client data,
  or remote application services.

## Scope

### IN

- A public documentation home and developer quickstart.
- Conceptual, policy, architecture, adapter, plugin, and evaluator guidance.
- Revision-bound benchmarks, security claims, threat model, limitations, and
  supply-chain verification.
- Release, repository, PyPI, contribution, and vulnerability-reporting routes.
- Responsive light and dark presentation using the existing MkDocs stack.
- Search, copyable code, canonical metadata, sitemap, robots policy, social
  metadata, favicon, custom 404, and accessible navigation.
- GitHub Pages deployment and the `archmage.saengil.ai` custom domain.

### OUT

- Authentication, accounts, dashboards, hosted policy evaluation, or execution.
- Uploads, comments, newsletter collection, support forms, payments, or any other
  user-data collection.
- Runtime telemetry, customer analytics, behavioral profiling, or advertising.
- A claims page that exceeds the published evidence boundary.
- API-reference generation from Python docstrings in v1.
- Replacing GitHub, PyPI, or release attestations as systems of record.

### DEFERRED

- Versioned documentation for multiple maintained major releases.
- Localization.
- Interactive playgrounds or browser-executed policy evaluation.
- Blog, changelog feed, case studies, and community showcase.
- Privacy-preserving analytics, pending an explicit measurement and retention
  decision.
- Migration away from GitHub Pages if response headers, edge logic, or uptime
  requirements outgrow static hosting.

## Primary journeys

### J1 — Evaluate fit

Home → architecture → limitations → security claims → GitHub/PyPI.

The visitor MUST see that ARCHMAGE is an application-layer policy runtime and
not an operating-system sandbox before encountering broad benefit language.

### J2 — First deterministic decision

Home install command → quickstart → `ALLOW` and `DENY` example → next integration
step.

The command MUST target the stable `archmage-ai` distribution. Examples MUST be
copyable, complete, and tested against the current stable release.

### J3 — Choose an integration surface

Architecture → Agent Plugin or adapters → host obligations → limitations.

The Agent Plugin MUST be described as an edge/distribution adapter converging on
the same PEP/PDP boundary, not a second policy implementation.

### J4 — Verify trust evidence

Current release → checksums → SBOM → GitHub provenance → PyPI attestations →
benchmark revision.

The user MUST be able to distinguish artifact integrity from vulnerability
absence.

### J5 — Contribute or report

Repository → contribution policy, or security page → private reporting route.

Suspected vulnerabilities MUST NOT be directed to public issues.

## Target information architecture

| Group | Route or destination | Purpose | Required page outcome |
|---|---|---|---|
| Start | `/` | Orientation and decision path | Product boundary, stable version, install command, verdict model, quickstart and evidence calls to action |
| Start | `/quickstart/` | First working evaluation | Reproducible setup, complete example, expected output, next steps |
| Understand | `/concepts/` | Domain vocabulary | Proposal → PEP → PDP → verdict model |
| Understand | `/policy-model/` | Evaluator and aggregation semantics | Fail-closed behavior and policy ownership |
| Understand | `/architecture/` | Trust and dependency boundaries | Host bypass risk and adapter convergence |
| Integrate | `/agent-plugin/` | Portable plugin path | Archive verification, install sequence, MCP boundary |
| Integrate | `/adapters/` | Native host path | Required trusted metadata and tool registry contract |
| Integrate | `/custom-evaluators/` | Extension path | Explicit injection and trusted-code warning |
| Evidence | `/benchmarks/` | Reproducible results | Version, revision, case catalog, environment, limitations |
| Evidence | `/security-claims/` | Allowed public claims | Claim-to-test matrix and boundary |
| Evidence | `/threat-model/` | Attacker model | Assets, boundaries, mitigations, residual risks |
| Evidence | `/limitations/` | Non-guarantees | Honest operating boundary adjacent to adoption |
| Evidence | `/supply-chain/` | Release verification | Exact commands for checksums and attestations |
| Project | GitHub release | Stable artifacts | Current release with immutable assets |
| Project | PyPI | Package install source | `archmage-ai` package and publish attestations |
| Project | `SECURITY.md` | Vulnerability route | Private reporting, scope, response expectations |
| Project | `CONTRIBUTING.md` | Contribution route | Approval-first governance and evidence contract |

The MkDocs navigation SHOULD group pages as Start, Understand, Integrate,
Evidence, and Project. External project links MUST be visibly distinguishable
from site routes.

## Home-page composition

The home page SHOULD use this order:

1. **Identity:** ARCHMAGE, one-sentence purpose, stable version.
2. **Boundary statement:** pre-execution policy evaluation; not a sandbox.
3. **Primary actions:** Install, Quickstart, Verify release.
4. **Verdict model:** `ALLOW`, `ALLOW_WITH_OBLIGATIONS`, `REPAIR`, `DENY`,
   `ESCALATE` with concise semantics.
5. **How it fits:** proposal → adapter → PEP/PDP → typed verdict → host dispatch.
6. **Integration paths:** Python library, native adapter, Agent Plugin/MCP.
7. **Evidence:** benchmark snapshot, security-claim policy, attestations.
8. **Limitations callout:** direct link before footer.
9. **Project routes:** GitHub, PyPI, security, contribution, Apache-2.0.

The current wizard artwork MAY support the identity area, but MUST NOT displace
the product boundary, install command, or primary actions below the initial
viewport on a typical mobile device.

## Functional requirements

- **SITE-FR-001:** Global navigation MUST expose every primary journey in at
  most two deliberate selections from the home page.
- **SITE-FR-002:** Site search MUST index all public documentation pages and be
  keyboard reachable.
- **SITE-FR-003:** Code blocks MUST provide copy controls with an accessible
  label and preserve exact whitespace.
- **SITE-FR-004:** Every page MUST expose a repository edit/view route or a
  stable source link.
- **SITE-FR-005:** The current stable version MUST appear on the home page and
  link to both PyPI and the matching immutable GitHub release.
- **SITE-FR-006:** External links MUST remain usable without JavaScript and MUST
  not receive `window.opener` access when opened in a new context.
- **SITE-FR-007:** A custom 404 page MUST offer Home, Quickstart, Search, and
  GitHub routes.
- **SITE-FR-008:** The site MUST remain readable and navigable when optional
  JavaScript enhancements fail; search and copy controls may degrade.
- **SITE-FR-009:** Mermaid diagrams MUST have adjacent text that conveys the
  same material relationship.
- **SITE-FR-010:** No route may accept, store, or transmit visitor input at
  handoff.

## Content contract

### Voice

- Direct, technical, bounded, and testable.
- Prefer “evaluates” or “denies the evaluated proposal” over “prevents.”
- Prefer exact component names and versions over trend language.
- Avoid unsupported universality, autonomy, safety, and performance claims.

### Release truth

- Installation examples MUST name `archmage-ai`.
- Version-bearing claims MUST identify the exact release and evidence revision.
- Mutable workflow links MAY explain the latest pipeline; evidence claims MUST
  also link to an immutable release or artifact.
- A docs update that changes a security statement MUST update the claim matrix
  or explicitly state why evidence is unchanged.
- Latest-version documentation MUST display the stable version. Multi-version
  behavior is deferred until more than one major release is supported.

### Page ownership

| Content class | Accountable owner | Review trigger |
|---|---|---|
| Home, quickstart, concepts | Product maintainer | Stable release or public positioning change |
| Architecture, policy, adapters | Runtime maintainer | Boundary, interface, or integration change |
| Benchmarks and claims | Evidence owner | Case catalog, environment, result, or claim change |
| Threat model and limitations | Security owner | New surface, assumption, mitigation, or finding |
| Supply chain | Release owner | Workflow, publisher, artifact, or attestation change |
| Domain and operations | Repository administrator | Hosting, DNS, certificate, or availability change |

## Visual and interaction system

### Direction

Use “arcane control plane” as a restrained motif: deep indigo structure, cyan
signal, violet evidence, and a limited warm intervention accent. Technical
content and contrast take precedence over illustration.

| Token | Value | Intended use |
|---|---|---|
| Ink | `#111827` | Light-theme body text |
| Paper | `#F8FAFC` | Light-theme surface |
| Night | `#090E2A` | Dark-theme background |
| Arcane indigo | `#18206F` | Primary navigation and identity |
| Signal cyan | `#58C4DC` | Links, diagrams, allowed paths |
| Evidence violet | `#7C4DCC` | Evidence and provenance accents |
| Intervention vermilion | `#D93A1A` | Deny/error states only |
| Focus gold | `#F4C84A` | Focus indicator and escalation accent |

Implementers MUST verify text and interactive-state contrast against WCAG 2.2
AA; these values are direction tokens, not permission to use every foreground
and background pairing.

- Use a system sans-serif stack and a system monospace stack at handoff. Remote
  font requests are OUT.
- Support light, dark, and operating-system preference. Theme selection MUST be
  keyboard accessible and persist locally without transmitting data.
- Use the wizard artwork as optional brand media. Produce responsive derivatives,
  declare dimensions, avoid layout shift, and retain meaningful alt text when it
  communicates identity.
- Verdict colors MUST be reinforced with text and shape; color alone MUST NOT
  encode a decision.
- Motion MUST be non-essential and respect `prefers-reduced-motion`.

## Accessibility requirements

The implementation MUST target
[WCAG 2.2 Level AA](https://www.w3.org/TR/WCAG22/).

- Semantic landmarks, one descriptive `h1`, ordered headings, and a working skip
  link on every page.
- Complete keyboard operation with visible focus and no focus traps.
- 4.5:1 minimum contrast for normal text and 3:1 for large text and meaningful
  UI boundaries.
- Touch targets of at least 24 by 24 CSS pixels, with 44 by 44 preferred for
  primary mobile actions.
- Text zoom to 200% and reflow at 320 CSS pixels without loss of content or
  horizontal page scrolling; wide code/table regions may scroll independently.
- Descriptive link text, image alternatives, diagram equivalents, and status
  labels that do not depend on color.
- Copy, search, theme, and navigation controls MUST expose an accessible name,
  role, state, and focus order.
- Automated checks MUST be supplemented by keyboard and screen-reader smoke
  tests on Home, Quickstart, Architecture, Limitations, and Supply chain.

## Responsive and compatibility requirements

- Mobile-first layout from 320 CSS pixels upward.
- Primary navigation collapses without hiding search, Quickstart, or limitations.
- Code samples and tables use contained horizontal scrolling.
- Support the current and previous major versions of Chrome, Edge, Firefox, and
  Safari, plus current iOS Safari and Android Chrome.
- Core reading and navigation remain functional without optional JavaScript.

## Performance requirements

- At prelaunch, Lighthouse mobile scores SHOULD be at least 90 Performance and
  at least 95 Accessibility, Best Practices, and SEO on the five critical pages.
- Field targets, once traffic is sufficient, are the
  [Core Web Vitals “good” thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds):
  LCP at or below 2.5 seconds, INP at or below 200 milliseconds, and CLS at or
  below 0.1 at the 75th percentile.
- Initial transferred page weight SHOULD stay below 500 KB on critical pages,
  excluding an explicitly user-requested download.
- The primary hero image SHOULD remain below 200 KB per responsive variant.
- Declare image dimensions, defer below-the-fold media, and avoid third-party
  runtime dependencies.

## Search and metadata requirements

- Every page MUST have a unique descriptive title, summary, canonical HTTPS URL,
  and stable heading.
- Generate `sitemap.xml` from the canonical `site_url` and provide a
  `robots.txt` that permits public documentation crawling.
- The home page SHOULD expose accurate `WebSite` and `SoftwareApplication`
  JSON-LD, including ARCHMAGE, `DeveloperApplication`, Python support, Apache-2.0,
  current release, PyPI, and repository URLs.
- Structured data MUST describe visible content and pass the applicable
  validation tool; it MUST NOT invent ratings, reviews, users, or endorsements.
- Provide Open Graph and social-card metadata with a crawlable branded image.
- Use “ARCHMAGE” consistently as the site name and “archmage-ai” only for the
  Python distribution identity.

## Privacy and safety requirements

- No analytics, tracking pixels, fingerprinting, cookies, forms, chat widgets,
  or remote fonts at handoff.
- No secrets, private issue URLs, private repository history, unpublished
  vulnerability details, or machine-specific paths in source or built output.
- All first-party assets MUST use HTTPS after launch; mixed active content is a
  launch blocker.
- Public examples MUST use synthetic identifiers and immutable placeholder
  revisions.
- GitHub Pages is not an appropriate surface for credentials or sensitive
  transactions.

## Site acceptance

Product/site implementation is accepted when:

1. All `SITE-FR-*` requirements have evidence.
2. All critical journeys pass on mobile and desktop.
3. The home page states the runtime boundary before broad benefit language.
4. Installation and evidence links resolve to `v2.0.0` or the current approved
   successor.
5. Accessibility, performance, link, metadata, strict-build, and mixed-content
   checks pass.
6. The technical handoff and launch runbook pass without undocumented operator
   knowledge.
7. The acceptance matrix contains no `NOT IMPLEMENTED`, `READY TO VERIFY`, or
   `BLOCKED` launch-critical row.

## References

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [Core Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds)
- [Google site-name guidance](https://developers.google.com/search/docs/appearance/site-names)
- [Software application structured data](https://developers.google.com/search/docs/appearance/structured-data/software-app)
