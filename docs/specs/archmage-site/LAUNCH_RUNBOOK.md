<!--​‌​‌‌​​‌​‌​‌‌​​​​‌​‌‌​‌​​‌​‌‌​​‌​‌​‌​​‌‌ YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# WEB-ARCHMAGE-001 — Launch and domain runbook

| Field | Value |
|---|---|
| Status | READY TO EXECUTE |
| Launch state | NO-GO until certificate and HTTPS gates pass |
| Repository administrator | `YXZYSME` |
| DNS/domain owner | YXZYS |
| Last observed | 2026-08-25 |

## Purpose

Use this runbook to recover custom-domain certificate provisioning, enable
HTTPS, validate the deployed documentation, record evidence, and roll back
without confusing site content, GitHub Pages settings, and DNS ownership.

This runbook contains no provider credentials or private dashboard links.

## Observed starting state

| Check | Observation | State |
|---|---|---|
| Pages build type | `workflow` | PASS |
| Pages visibility | Public | PASS |
| Pages custom domain | `archmage.saengil.ai` | PASS |
| Protected domain state | Verified | PASS |
| Verification TXT | Present | PASS |
| CNAME | `archmage.saengil.ai → yxzysme.github.io` | PASS |
| CAA | No applicable record observed | PASS; not blocking Let's Encrypt |
| Pages certificate object | Absent | BLOCKED |
| HTTPS enforced | `false` | BLOCKED |
| HTTP home | 200 from GitHub Pages | PASS as diagnostic only |
| HTTPS home | Content responds only when certificate validation is bypassed | BLOCKED |
| Presented certificate | GitHub wildcard without the custom hostname | BLOCKED |
| Default project URL | Redirects to insecure custom-domain URL | BLOCKED |

Re-run every observation before acting. DNS and Pages state are external and may
change after this snapshot.

## Roles and authority

- **Site implementer:** may change documentation source through the repository
  workflow; does not change DNS or Pages settings.
- **Repository administrator:** may manage Pages custom domain, rerun the docs
  deployment, and enable HTTPS.
- **DNS owner:** may inspect and change the `saengil.ai` zone.
- **Launch approver:** evaluates the acceptance matrix and records go/no-go.

Do not combine an unreviewed site deployment and a DNS/certificate intervention
in the same maintenance step.

## Preflight guardrails

Before changing external state:

1. Confirm the latest public `main` documentation workflow succeeded.
2. Capture the current Pages API response.
3. Capture the relevant CNAME, TXT, CAA, and TTL values from authoritative DNS.
4. Confirm `saengil.ai` is verified in the `YXZYSME` Pages settings.
5. Confirm the DNS and GitHub account recovery owners are available.
6. Record the last known-good docs workflow run and source revision.
7. Announce a maintenance window if the domain is already advertised.

Read-only preflight:

```bash
gh api repos/YXZYSME/archmage/pages \
  --jq '{status,cname,html_url,build_type,public,protected_domain_state,https_enforced,https_certificate}'

dig +noall +answer archmage.saengil.ai CNAME
dig +noall +answer _github-pages-challenge-YXZYSME.saengil.ai TXT
dig +noall +answer saengil.ai CAA

curl --head --max-time 15 http://archmage.saengil.ai/

openssl s_client \
  -connect archmage.saengil.ai:443 \
  -servername archmage.saengil.ai \
  -verify_hostname archmage.saengil.ai \
  </dev/null
```

Do not use a TLS bypass flag as launch evidence.

## Phase 1 — Confirm DNS eligibility

The DNS owner MUST confirm:

- the `archmage` label has exactly one CNAME to `yxzysme.github.io.`;
- no conflicting address, alias, proxy, or forwarding record exists at that
  label;
- the GitHub domain-verification TXT remains present;
- no wildcard record creates an unintended Pages takeover surface;
- if any inherited CAA record exists, at least one `issue` authorization permits
  `letsencrypt.org`; and
- DNSSEC, if enabled, validates without a broken delegation.

If DNS is wrong, correct DNS first, wait for authoritative answers and resolver
caches to converge, and repeat preflight. Do not restart GitHub certificate
provisioning against known-invalid DNS.

## Phase 2 — Restart stalled certificate provisioning

GitHub automatically begins a DNS check and certificate request when the custom
domain is set. The current configuration is verified but has no attached
certificate.

During the approved maintenance window:

1. Open repository **Settings → Pages**.
2. Capture the displayed custom-domain and HTTPS state.
3. If a certificate is still absent after DNS eligibility is confirmed, remove
   `archmage.saengil.ai` from the repository custom-domain field.
4. Immediately re-enter `archmage.saengil.ai` and save it.
5. Confirm GitHub reports the DNS check as successful.
6. Rerun the Documentation workflow if Pages does not deploy the current source
   after the setting change.
7. Keep the verified-domain TXT and intended CNAME in place throughout.

Removing and re-adding the custom domain is GitHub's documented restart
procedure for stalled provisioning. Minimize the interval. Do not delete account
domain verification.

## Phase 3 — Observe certificate state

Check at short intervals without changing configuration repeatedly:

```bash
gh api repos/YXZYSME/archmage/pages \
  --jq '{cname,protected_domain_state,https_enforced,https_certificate}'
```

Allow up to one hour after a correct configuration for HTTPS availability. If
the certificate remains absent:

1. Recheck authoritative CNAME and inherited CAA.
2. Confirm no DNS proxy or stale duplicate record exists.
3. Confirm the exact custom hostname is attached to only this Pages site.
4. Capture the Pages state and time.
5. Stop making repeated remove/re-add changes.
6. Escalate through GitHub support or schedule a second controlled attempt.

The site remains NO-GO while the certificate is absent or does not cover the
exact hostname.

## Phase 4 — Enable HTTPS

Once GitHub reports the certificate ready:

1. Select **Enforce HTTPS** in repository Pages settings.
2. Confirm the setting remains selected after refresh.
3. Confirm the Pages API reports `https_enforced: true`.
4. Wait for edge configuration to converge before final validation.

Do not advertise the custom domain between certificate issuance and HTTPS
enforcement.

## Phase 5 — Validate production

### Transport and certificate

```bash
curl --fail --silent --show-error --location \
  --output /dev/null \
  --write-out '%{url_effective} %{http_code}\n' \
  http://archmage.saengil.ai/

curl --fail --silent --show-error --head \
  https://archmage.saengil.ai/

openssl s_client \
  -connect archmage.saengil.ai:443 \
  -servername archmage.saengil.ai \
  -verify_hostname archmage.saengil.ai \
  </dev/null
```

Expected:

- the HTTP request ends at `https://archmage.saengil.ai/`;
- HTTPS returns 200 without a bypass flag;
- OpenSSL reports successful chain and hostname verification; and
- the certificate validity window is current.

### Critical routes

```bash
curl --fail --silent --show-error --output /dev/null https://archmage.saengil.ai/
curl --fail --silent --show-error --output /dev/null https://archmage.saengil.ai/quickstart/
curl --fail --silent --show-error --output /dev/null https://archmage.saengil.ai/architecture/
curl --fail --silent --show-error --output /dev/null https://archmage.saengil.ai/limitations/
curl --fail --silent --show-error --output /dev/null https://archmage.saengil.ai/supply-chain/
```

### Source and generated output

```bash
python -m pip install --editable ".[docs]"
python -m mkdocs build --strict

if rg '(src|href)="http://' site; then
  exit 1
fi

if rg '/(Users|home)/[[:alnum:]_.-]+/|archmage-private-history[.]git' site; then
  exit 1
fi
```

The two `rg` scans MUST return no matches. Review any match instead of blindly
suppressing it.

### Browser acceptance

On Home, Quickstart, Architecture, Limitations, and Supply chain:

- verify desktop and mobile navigation;
- use keyboard-only navigation and visible focus;
- check light, dark, and reduced-motion modes;
- exercise search and code copy controls;
- verify no mixed-content or console errors;
- inspect canonical, social, robots, sitemap, favicon, and structured metadata;
- run the approved accessibility scan and manual screen-reader smoke test; and
- capture the required Lighthouse evidence.

### External truth

- PyPI link opens `archmage-ai` and the current stable version.
- Release link opens the matching immutable GitHub release.
- Checksum, SBOM, provenance, and benchmark links identify the same release.
- Security routes point to private reporting instructions, not a public issue.
- Limitations remain adjacent to security and benchmark claims.

## Evidence record

Attach or link these items to the launch approval:

| Evidence | Required content |
|---|---|
| Source | Public `main` revision and reviewed pull request |
| Build | Strict local build and hosted docs workflow |
| Deploy | Successful GitHub Pages deployment run |
| DNS | Authoritative CNAME, retained verification TXT, relevant CAA result |
| Pages | Custom domain, verified state, certificate state, HTTPS enforcement |
| TLS | Exact hostname, issuer, validity, successful verification |
| HTTP | HTTP-to-HTTPS redirect and final 200 |
| Routes | 200 results for all critical routes |
| UX | Desktop/mobile, keyboard, theme, search, copy, 404 |
| Accessibility | Automated and manual results with exceptions resolved |
| Performance | Lighthouse and page-weight results |
| Metadata | Canonical, sitemap, robots, social, structured-data validation |
| Security | Mixed-content and public-output scans |
| Rollback | Known-good revision and DNS snapshot |

Evidence MUST exclude credentials, private recovery information, and private
dashboard URLs.

## Go/no-go

### GO

GO requires:

- every launch-critical acceptance row is `PASS`;
- the custom certificate covers the exact hostname;
- HTTPS is enforced;
- critical routes and external truth checks pass;
- no unresolved critical accessibility, mixed-content, or content-claim issue;
- a rollback target and owners are present; and
- YXZYS records explicit approval.

### NO-GO

Any of these is an automatic NO-GO:

- invalid, absent, expired, or hostname-mismatched certificate;
- HTTPS enforcement off or redirect loop;
- critical route unavailable;
- Pages deployment not traceable to protected `main`;
- public secret/private-data exposure;
- a security claim beyond the evidence boundary;
- keyboard-inaccessible primary journey; or
- no coordinated rollback authority.

## Rollback

### Content or styling regression

1. Keep DNS and the validated custom domain unchanged.
2. Revert the offending commit through the normal protected-branch workflow.
3. Redeploy the last known-good tree.
4. Re-run transport, routes, mixed-content, and critical browser checks.

### Deployment failure

1. Do not force-push `main`.
2. Inspect the failed docs workflow and artifact boundary.
3. Redeploy a known-good revision through an approved revert.
4. Keep the last successful Pages deployment serving where possible.

### DNS regression

1. Restore the pre-change authoritative record set.
2. Wait for the recorded TTL.
3. Validate authoritative and public resolver answers.
4. Re-run Pages and TLS checks before advertising recovery.

### Certificate failure after launch

1. Treat hostname mismatch, expiry, or failed TLS verification as a public site
   incident.
2. Stop advertising the custom domain in new communications.
3. Preserve evidence and check Pages/DNS before making repeated changes.
4. If the domain must be detached, the domain owner and repository administrator
   MUST coordinate removal of both the Pages binding and the DNS route. Do not
   leave a Pages-pointing abandoned record.
5. Use immutable GitHub documentation links as the temporary public route.

## Post-launch

After seven stable days:

- record the custom-domain certificate and HTTPS gate as complete in
  `RELEASE_CHECKLIST.md`;
- confirm README, PyPI metadata in the next release, and release templates use
  the canonical HTTPS domain;
- retain the GitHub verification TXT;
- normalize DNS TTL if it was reduced;
- run one fresh accessibility, metadata, link, and Lighthouse check;
- confirm the weekly certificate/domain check has an owner; and
- close the launch record with final evidence.

## References

- [GitHub: Secure a Pages site with HTTPS](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)
- [GitHub: Troubleshoot custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/troubleshooting-custom-domains-and-github-pages)
- [GitHub: Manage a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
