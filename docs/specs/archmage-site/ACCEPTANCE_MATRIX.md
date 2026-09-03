<!--​‌​‌‌​​‌​‌​‌‌​​​​‌​‌‌​‌​​‌​‌‌​​‌​‌​‌​​‌‌ YXZYS | saeng-il ai [systems] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# WEB-ARCHMAGE-001 — Acceptance matrix

| Field | Value |
|---|---|
| Baseline | Public `v2.0.0` documentation and Pages configuration |
| Assessed | 2026-08-25 |
| TLS evidence refresh | 2026-09-03 |
| Site handoff | READY FOR IMPLEMENTATION |
| Production launch | NO-GO |

## Status model

| Status | Meaning |
|---|---|
| `PASS` | Requirement has current evidence |
| `PARTIAL` | Some required behavior exists; implementation or evidence is incomplete |
| `READY TO VERIFY` | Implementation likely exists but required acceptance evidence has not been captured |
| `NOT IMPLEMENTED` | Required behavior is absent |
| `BLOCKED` | Cannot pass until an external or upstream condition changes |
| `DEFERRED` | Explicitly outside public documentation v1 |

`Launch critical` means the site cannot be approved for the canonical custom
domain while the row is anything other than `PASS`.

## Handoff contract

| ID | Requirement | Owner | Evidence | Status | Launch critical |
|---|---|---|---|---|---|
| SITE-HO-001 | Product intent, audience, journeys, scope, and non-goals are explicit | Product owner | [Site specification](SITE_SPEC.md) | PASS | No |
| SITE-HO-002 | Information architecture and page outcomes are explicit | Product owner | [Target information architecture](SITE_SPEC.md#target-information-architecture) | PASS | No |
| SITE-HO-003 | Hosting, source ownership, security, and delivery boundaries are explicit | Repository administrator | [Technical handoff](TECHNICAL_HANDOFF.md) | PASS | No |
| SITE-HO-004 | DNS, certificate, verification, rollback, and evidence steps are executable | Domain and repository owners | [Launch runbook](LAUNCH_RUNBOOK.md) | PASS | Yes |
| SITE-HO-005 | Every launch requirement has an owner, evidence type, and current state | Launch approver | This matrix | PASS | Yes |

## Product and content

| ID | Requirement | Owner | Current evidence or gap | Status | Launch critical |
|---|---|---|---|---|---|
| SITE-PC-001 | Home follows the approved composition and exposes the three primary actions | Site implementer | Current `docs/index.md` is an orientation page but lacks the full home composition | NOT IMPLEMENTED | Yes |
| SITE-PC-002 | Home states the application-layer boundary before broad benefits | Product owner | Current home states the product wedge and exclusions | PASS | Yes |
| SITE-PC-003 | Home identifies the stable version and links matching PyPI and GitHub release records | Release owner | README has package/version context; site home does not | PARTIAL | Yes |
| SITE-PC-004 | Navigation groups Start, Understand, Integrate, Evidence, and Project routes | Site implementer | Current navigation is complete but flat | NOT IMPLEMENTED | No |
| SITE-PC-005 | Evaluate, quickstart, integrate, verify, and report journeys are reachable in at most two selections | Product owner | Technical pages are globally visible; home calls to action and project routes are incomplete | PARTIAL | Yes |
| SITE-PC-006 | Quickstart installs the stable `archmage-ai` distribution and shows expected output | Runtime maintainer | `docs/quickstart.md` | READY TO VERIFY | Yes |
| SITE-PC-007 | Architecture explains PEP/PDP, host bypass, and adapter convergence | Runtime maintainer | `docs/architecture.md` | PASS | Yes |
| SITE-PC-008 | Limitations stay adjacent to adoption, benchmark, and security claims | Security owner | Dedicated page exists; home and grouped evidence journey need implementation review | PARTIAL | Yes |
| SITE-PC-009 | Supply-chain page verifies the stable package, plugin, checksums, and attestations | Release owner | `docs/supply-chain.md` reflects `v2.0.0` release surfaces | READY TO VERIFY | Yes |
| SITE-PC-010 | Security reporting routes to private instructions and not public issues | Security owner | `SECURITY.md` exists; site-level Project route is absent | PARTIAL | Yes |
| SITE-PC-011 | Contribution route exposes the approval-first repository contract | Product owner | `CONTRIBUTING.md` exists; site-level Project route is absent | PARTIAL | No |
| SITE-PC-012 | Custom 404 offers Home, Quickstart, Search, and GitHub | Site implementer | No owned 404 content | NOT IMPLEMENTED | Yes |

## Visual and interaction

| ID | Requirement | Owner | Current evidence or gap | Status | Launch critical |
|---|---|---|---|---|---|
| SITE-VI-001 | Approved brand tokens are implemented with verified contrast | Site implementer | Tokens are specified; no site override exists | NOT IMPLEMENTED | No |
| SITE-VI-002 | Light, dark, and system-preference modes are supported | Site implementer | Current MkDocs configuration has no palette contract | NOT IMPLEMENTED | No |
| SITE-VI-003 | System fonts replace remote font requests | Site implementer | Current default theme behavior has not been overridden | NOT IMPLEMENTED | Yes |
| SITE-VI-004 | Verdict states use text/shape in addition to color | Site implementer | Component not yet implemented | NOT IMPLEMENTED | Yes |
| SITE-VI-005 | Wizard brand media is responsive, dimensioned, optimized, and accessible | Brand and site owners | Source JPEG exists; web derivatives and page placement are absent | NOT IMPLEMENTED | No |
| SITE-VI-006 | Primary content and navigation reflow at 320 CSS pixels | Site implementer | Material is responsive; customized journeys have not been tested | READY TO VERIFY | Yes |
| SITE-VI-007 | Motion is non-essential and respects reduced-motion preference | Site implementer | No custom motion exists; theme behavior needs validation | READY TO VERIFY | Yes |

## Accessibility and compatibility

| ID | Requirement | Owner | Current evidence or gap | Status | Launch critical |
|---|---|---|---|---|---|
| SITE-A11Y-001 | Critical pages meet WCAG 2.2 AA | Site implementer | No conformance evidence captured | READY TO VERIFY | Yes |
| SITE-A11Y-002 | Keyboard operation, visible focus, skip link, and focus order pass | Site implementer | Theme capability exists; manual pass absent | READY TO VERIFY | Yes |
| SITE-A11Y-003 | Screen-reader smoke tests pass on five critical pages | Accessibility reviewer | No manual evidence | NOT IMPLEMENTED | Yes |
| SITE-A11Y-004 | Text, UI boundary, state, and focus contrast pass | Accessibility reviewer | Custom tokens not implemented or audited | NOT IMPLEMENTED | Yes |
| SITE-A11Y-005 | Images and diagrams have alternatives or adjacent equivalents | Content owner | Architecture diagram has adjacent boundary text; all future media still needs a scan | PARTIAL | Yes |
| SITE-A11Y-006 | Search, copy, navigation, and theme controls expose accessible state | Site implementer | Search/copy theme defaults exist; complete control test absent | READY TO VERIFY | Yes |
| SITE-COMPAT-001 | Critical paths pass supported desktop and mobile browsers | Site implementer | No browser matrix evidence | NOT IMPLEMENTED | Yes |
| SITE-COMPAT-002 | Core reading and navigation work without optional JavaScript | Site implementer | Static content likely works; no deliberate degradation test | READY TO VERIFY | No |

## Performance, search, and metadata

| ID | Requirement | Owner | Current evidence or gap | Status | Launch critical |
|---|---|---|---|---|---|
| SITE-PERF-001 | Critical pages meet Lighthouse launch budgets | Site implementer | No captured Lighthouse evidence | NOT IMPLEMENTED | Yes |
| SITE-PERF-002 | Critical pages stay within page-weight and image budgets | Site implementer | No page-weight report or optimized hero | NOT IMPLEMENTED | No |
| SITE-PERF-003 | Layout declares media dimensions and avoids material shift | Site implementer | Current docs are mostly text; planned brand media unqualified | READY TO VERIFY | Yes |
| SITE-SEO-001 | Unique titles, summaries, and canonical HTTPS URLs exist | Content owner | Titles and `site_url` exist; summaries/canonical output need page audit | PARTIAL | Yes |
| SITE-SEO-002 | Sitemap and robots policy use the canonical host | Site implementer | Sitemap generation expected; owned `robots.txt` absent | PARTIAL | Yes |
| SITE-SEO-003 | Home exposes accurate `WebSite` and `SoftwareApplication` structured data | Site implementer | No owned JSON-LD implementation | NOT IMPLEMENTED | No |
| SITE-SEO-004 | Open Graph, social image, and favicon are complete | Brand and site owners | No implementation evidence | NOT IMPLEMENTED | No |
| SITE-SEO-005 | Structured data describes visible facts and passes validation | Content owner | Dependent on SITE-SEO-003 | NOT IMPLEMENTED | No |

## Build, deployment, domain, and TLS

| ID | Requirement | Owner | Current evidence or gap | Status | Launch critical |
|---|---|---|---|---|---|
| SITE-DEL-001 | A clean strict MkDocs build succeeds | Site implementer | Hosted CI passed on public `main`; re-run for implementation change | READY TO VERIFY | Yes |
| SITE-DEL-002 | Docs workflow actions remain SHA-pinned | Repository maintainer | `.github/workflows/docs.yml` | PASS | Yes |
| SITE-DEL-003 | Build/deploy permissions remain least-privilege | Repository administrator | Read-only build; Pages and OIDC only in deploy job | PASS | Yes |
| SITE-DEL-004 | Deployment is traceable to protected public `main` | Repository administrator | Current workflow trigger and repository protection | PASS | Yes |
| SITE-DEL-005 | Internal/external link validation passes | Site implementer | No dedicated complete link-check evidence | NOT IMPLEMENTED | Yes |
| SITE-DEL-006 | Built output contains no mixed content, private path, secret, or private-history reference | Security reviewer | Source controls exist; required output scans not captured | READY TO VERIFY | Yes |
| SITE-DEL-007 | Docs dependencies explicitly prevent unreviewed MkDocs 2.x resolver drift | Repository maintainer | Material warns about the incompatible major; `pyproject.toml` does not directly bound MkDocs | NOT IMPLEMENTED | Yes |
| SITE-DNS-001 | Explicit CNAME targets `yxzysme.github.io.` | DNS owner | Authoritative/public DNS observation | PASS | Yes |
| SITE-DNS-002 | `saengil.ai` remains verified and the challenge TXT is retained | Domain owner | Pages API says verified; TXT observed | PASS | Yes |
| SITE-DNS-003 | No conflicting record, DNS proxy, wildcard takeover, or restrictive CAA blocks issuance | DNS owner | CNAME and no CAA observed; authoritative provider review still required | READY TO VERIFY | Yes |
| SITE-TLS-001 | GitHub attaches a certificate covering `archmage.saengil.ai` | Repository administrator | Valid Let's Encrypt certificate covering `archmage.saengil.ai` observed at the edge on 2026-09-03 (issued 2026-09-03, Let's Encrypt YR2). Pages API certificate object not recaptured. | READY TO VERIFY | Yes |
| SITE-TLS-002 | Pages reports `https_enforced: true` | Repository administrator | Pages API `https_enforced` not recaptured. An HTTP 301 to HTTPS is not a substitute for the API field. | READY TO VERIFY | Yes |
| SITE-TLS-003 | HTTP redirects to the same HTTPS host | Repository administrator | `http://archmage.saengil.ai/` returned 301 to `https://archmage.saengil.ai/` from one public vantage point on 2026-09-03. Formal launch-evidence package not captured. | READY TO VERIFY | Yes |
| SITE-TLS-004 | Canonical HTTPS critical routes return 200 without bypass | Repository administrator | HTTPS home, `/quickstart/`, `/architecture/`, `/limitations/`, and `/supply-chain/` returned 200 with a hostname-valid certificate on 2026-09-03. Formal launch-evidence package not captured. | READY TO VERIFY | Yes |
| SITE-TLS-005 | Default GitHub Pages URL redirects to validated HTTPS custom host | Repository administrator | `https://yxzysme.github.io/archmage/` returned 301 to `https://archmage.saengil.ai/` on 2026-09-03. Formal launch-evidence package not captured. | READY TO VERIFY | Yes |

## Operations and launch

| ID | Requirement | Owner | Current evidence or gap | Status | Launch critical |
|---|---|---|---|---|---|
| SITE-OPS-001 | Content, deployment, DNS, and certificate rollback paths are documented | Repository and domain owners | [Rollback runbook](LAUNCH_RUNBOOK.md#rollback) | PASS | Yes |
| SITE-OPS-002 | Last known-good revision and DNS snapshot are captured before intervention | Repository and DNS owners | Procedure exists; launch-time evidence pending | READY TO VERIFY | Yes |
| SITE-OPS-003 | Post-deploy route and certificate checks have an owner | Repository administrator | Responsibility defined; recurring check not yet established | PARTIAL | Yes |
| SITE-OPS-004 | Launch evidence excludes credentials and private dashboard routes | Launch approver | Evidence contract defined | READY TO VERIFY | Yes |
| SITE-OPS-005 | Public communications avoid the custom host until TLS acceptance | Product owner | Release notes use immutable GitHub links; README/PyPI metadata still name the custom site | PARTIAL | Yes |
| SITE-OPS-006 | Launch approval is recorded only after every critical row passes | YXZYS | No approval; current state is NO-GO | BLOCKED | Yes |
| SITE-OPS-007 | Seven-day post-launch review and ownership check are completed | Launch approver | Post-launch task | DEFERRED | No |

## Launch decision

The spec package is ready for implementation handoff. The site is not ready to
be advertised as the canonical production documentation surface.

Certificate issuance is no longer the unique external blocker. A hostname-valid
Let's Encrypt certificate was observed at the edge on 2026-09-03, and HTTP and
default-host redirects to HTTPS were observed from one vantage point. Those
rows are `READY TO VERIFY` until Pages API `https_enforced` and a formal
launch-evidence package are captured. Do not treat the custom host as
canonical while those gates, or any other launch-critical non-`PASS` row,
remain open.

The immediate critical path is:

1. implement the content, theme, accessibility, metadata, and validation gaps;
2. rerun the build and deployment evidence;
3. recapture Pages API `https_enforced` and the formal TLS launch-evidence
   package;
4. close every launch-critical non-`PASS` row; and
5. record explicit go/no-go approval.
