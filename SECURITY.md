<!-- YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Security Policy

## Supported Versions

Security fixes are provided for the latest published minor release.

| Version | Supported |
|---|:---:|
| 2.0.x | Yes |
| Earlier versions | No |

Before the first published package release, development snapshots are not a
supported security release. Reports against pre-release commits on `main` are
still welcome.

## Report a Vulnerability

Do not open a public issue for a suspected vulnerability.

Use [GitHub private vulnerability reporting](https://github.com/YXZYSME/archmage/security/advisories/new).
If that route is unavailable, email [yxzys@proton.me](mailto:yxzys@proton.me)
with the subject `ARCHMAGE security report`.

Include:

- the affected version or commit;
- the impacted component and configuration;
- reproduction steps or a minimal proof of concept;
- the expected and observed security boundary;
- the practical impact and required attacker access;
- any suggested remediation or disclosure deadline.

Do not include real credentials, private user data, or destructive production
payloads. Encrypt sensitive supporting material before sending it and request a
key through the private reporting route.

## Response Targets

The maintainers aim to:

- acknowledge a report within three business days;
- provide an initial triage decision within seven business days;
- send a status update at least every 14 days while remediation is active;
- coordinate a disclosure date after a fix or mitigation is available.

These are response targets, not a service-level agreement.

## Scope

Security reports are especially useful when they demonstrate:

- a bypass of adapter, PEP, or PDP enforcement under documented assumptions;
- a scope-containment or protected-policy mutation bypass;
- an authorization-relevant fail-open condition;
- forged or incorrectly trusted identity, lineage, approval, or audit state;
- unsafe package contents, release workflow behavior, or artifact provenance;
- exposure of secrets or sensitive proposal data.

ARCHMAGE is not an operating-system sandbox, caller-authentication service,
malware scanner, credential vault, or complete prompt-injection defense. A host
that bypasses the adapter or supplies forged trusted metadata is outside the
library guarantee, but reports showing that the documentation or defaults make
such a bypass likely are welcome.

## Coordinated Disclosure

Please allow a reasonable remediation window before public disclosure. The
maintainers normally target disclosure within 90 days, but may coordinate a
shorter or longer period based on exploitability, downstream impact, and fix
availability. Credit is offered unless anonymity is requested.

## Safe Harbor

Good-faith research is welcome when it:

- stays within systems and data you own or are authorized to test;
- avoids privacy violations, service degradation, persistence, and lateral movement;
- uses the minimum access needed to demonstrate impact;
- stops and reports promptly after confirming the issue;
- follows applicable law and coordinated-disclosure terms.

The maintainers will not pursue legal action for research that follows this
policy. This safe-harbor statement does not bind third parties.
