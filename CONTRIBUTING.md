<!-- YXZYS | saeng-il ai [development] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Contributing to ARCHMAGE

ARCHMAGE is open source for the agentic ecosystem, but contribution access is
approval-only. Anyone may use, study, discuss, and fork the project. A pull
request is eligible for merge only when its author has received a scoped,
time-limited approval from an ARCHMAGE maintainer.

Contributions may address policy enforcement, adapters, bug fixes, tests,
documentation, performance, research, security, and language integrations.
Changes that conflict with ARCHMAGE's design laws, deterministic control model,
or documented security boundary will not be accepted.

## Contribution path

1. Open a contribution proposal before implementation.
2. Wait for a maintainer to review the proposal.
3. Receive `status:approved-to-build` and one ARCHMAGE rank label.
4. Work only within the approved issue scope.
5. Open a pull request before the approval expires.
6. Satisfy every automated and manual evidence gate.

Approval applies to one named contributor, one issue, and its accepted scope. It
expires 30 calendar days after approval unless a maintainer renews it. Approval
does not guarantee review, acceptance, or merge.

An unapproved pull request remains open until a maintainer completes triage; the
automated policy check does not comment on or close it. After review, a
maintainer may approve the scope, request changes, decline it silently, or close
it. Only a maintainer can grant a rank, approve the proposal, or merge the
result. See [ARCHMAGE_RANKS.md](ARCHMAGE_RANKS.md) for the public rank model.

## Maintainer maintenance path

An SS-Rank Archmage may use the `Maintainer maintenance` issue form for a
bounded typo or wording correction, metadata correction, reviewed pinned-action
update, mechanical formatting or generated-file refresh, or similarly
non-behavioral repository housekeeping.

This is an abbreviated intake form, not an approval or evidence bypass. The
issue must still receive `status:approved-to-build`, the pull request must carry
the `SS-Rank Archmage` label, every commit must have DCO sign-off, and the full
pull-request contract and required checks still apply.

The maintenance path cannot be used for runtime behavior, public interfaces or
compatibility, security boundaries, repository permissions, release or
publishing behavior, workflow permissions, dependency resolution, package
identity, domain routing, licensing, governance, or work whose impact is
uncertain. If implementation discovers broader scope, stop the work and open a
full contribution proposal. B-Rank, A-Rank, and S-Rank contributors always
begin with the full contribution proposal.

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

## Pull request contract

Every pull request must provide:

- a linked, maintainer-approved issue or proposal;
- one applicable ARCHMAGE rank label;
- all required CI checks;
- regression tests for changed behavior;
- no reduction in measured coverage;
- reproducible benchmark evidence, or a reasoned `N/A` for a change that cannot
  affect runtime behavior or performance;
- a security-impact explanation;
- documentation updates or a reasoned `N/A`;
- a backward-compatibility analysis;
- Developer Certificate of Origin sign-off on every commit; and
- a sanitized agentic-tool prompt record.

The pull request template is part of the contract. Removing a section, leaving a
placeholder, or substituting an unsupported claim causes the contribution-policy
check to fail.

## Prompt disclosure

Agentic tools are permitted when their use is disclosed. Include:

- the source starter prompt;
- material follow-up prompts that changed the solution;
- the tools or models used, when known; and
- a short note describing human review and material corrections.

If no agentic tool was used, state `No agentic tools used`.

Sanitize prompt records before posting. Never disclose credentials, private
contact data, unpublished vulnerability details, private system instructions,
or third-party confidential information. Security reports use the private route
in `SECURITY.md`; public prompt disclosure is not required while a vulnerability
is embargoed.

## Evidence rules

The default evidence contract is:

- tests demonstrate the regression and the compliant behavior;
- coverage is compared with the pull request base and must not decrease;
- deterministic benchmark artifacts identify the revision and environment;
- performance claims include before-and-after measurements;
- security claims identify assumptions, attacker access, and the affected
  boundary;
- documentation and compatibility effects are explicit.

Documentation-only, metadata-only, and other changes that cannot affect runtime
behavior may mark benchmark evidence `N/A`. The reason must be specific enough
for a maintainer to verify. This exception is deliberately narrow and may change
as ARCHMAGE's benchmark system evolves.

## Design contract

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

## Developer Certificate of Origin

ARCHMAGE uses the [Developer Certificate of Origin 1.1](https://developercertificate.org/)
instead of a contributor license agreement for routine community contributions.
Sign every commit with:

```bash
git commit --signoff
```

The sign-off certifies that you have the right to submit the contribution under
the project's Apache-2.0 license. Maintainers may additionally require a
cryptographically verified commit signature for high-trust roles.

## Security reports

Do not open a public issue for a suspected vulnerability. Use the private
disclosure route in `SECURITY.md`.

## Conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
