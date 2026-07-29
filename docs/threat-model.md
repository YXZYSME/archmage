<!-- YXZYS | saeng-il ai [research] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Threat Model

## Overview

ARCHMAGE is an in-process Python policy decision and enforcement library for
coding-agent tool proposals. Its primary runtime surfaces are the generic and
Antigravity adapters, `ActionProposal`, the policy enforcement point (PEP), the
policy decision point (PDP), and deterministic evaluators. It does not expose a
network service, persist credentials, execute tools, or provide an operating-
system sandbox.

The assets that matter are the host’s files and commands, the declared workspace
boundary, protected policy/runtime code, task and actor lineage, approval and
obligation state, audit events, and the integrity of published distributions.

## Threat Model, Trust Boundaries, and Assumptions

### Trust boundaries

1. **Untrusted agent to host adapter:** tool names, arguments, repository text,
   retrieved instructions, and proposed target paths may be adversarial.
2. **Host to ARCHMAGE context:** task identity, authenticated principal,
   workspace, revision, ownership, and approval evidence must be constructed by
   the host. Shape validation does not make those values authentic.
3. **Adapter to PEP/PDP:** the adapter must completely describe the proposed
   effects. Omitted paths or resources can make a structurally valid proposal
   incomplete.
4. **PEP to executor:** authorization must be authoritative. The executor must
   not be reachable through an alternate plugin, native shell, RPC, or direct
   filesystem API.
5. **PDP to custom evaluators:** evaluator code runs in process and is trusted
   code. A malicious evaluator can inspect proposal data or intentionally alter
   policy outcomes even though unexpected exceptions fail closed.
6. **PEP to audit/approval systems:** log durability, redaction, approval
   authentication, retention, and tamper resistance belong to the embedding host.
7. **Source to release artifact:** repository controls, pinned workflows, build
   dependencies, PyPI trusted publishing, attestations, and maintainer accounts
   form the release trust boundary.

### Security invariants

- Every privileged action is routed through one reviewed adapter and the PEP.
- Path-sensitive actions declare at least one target and are resolved canonically
  against an absolute workspace.
- Shipped adapters reject unknown tools and incomplete required path fields.
- Missing identity, mutable lineage labels, evaluator crashes, and unresolvable
  path inputs fail closed.
- Protected-policy changes cannot be approved merely by changing untrusted action
  metadata.
- Obligation acknowledgment, especially human approval, is supplied only by a
  trusted host authority.
- Audit records and released artifacts do not expose secrets from raw tool
  payloads.
- Public security and performance claims remain tied to reproducible evidence.

### Assumptions and exclusions

The embedding host is assumed to authenticate principals, choose the workspace,
derive accurate effect metadata, keep privileged executors private, authenticate
approvals, and apply operating-system isolation. ARCHMAGE does not claim to stop
an already-compromised host, malicious maintainer, arbitrary native process,
direct executor bypass, every command encoding, or every semantic form of prompt
injection.

## Attack Surface, Mitigations, and Attacker Stories

### Tool and proposal inputs

An attacker may place instructions in source, issues, comments, or retrieved
documents that cause an agent to propose an out-of-scope write, policy mutation,
or shell command. The shipped adapters require canonical JSON payloads, enforce a
size bound, require identity/scope/revision fields, use explicit tool registries,
and classify known effects. Scope and protected-mutation evaluators then issue
typed denials.

Remaining risk: arbitrary commands can encode undeclared filesystem, process,
network, or credential effects. The default policy obligates every
`run_command`, but the host still needs command policy, sandboxing, network
controls, and an effect inventory.

### Filesystem boundaries

An attacker may use `..`, absolute paths, prefix collisions, or symlinks to leave
the workspace. Canonical resolution and path-relative containment address those
forms, and tests cover prefix and existing-symlink escapes.

Remaining risk: authorization and execution occur in separate components, so a
host executor must address time-of-check/time-of-use changes and enforce its own
filesystem boundary.

### Identity, lineage, approvals, and audit

An attacker may omit metadata, use ambient values such as `HEAD`, forge an actor
identifier, replay an approval, self-acknowledge an obligation, or claim audit
support. ARCHMAGE rejects missing/ambient declarations, requires a hexadecimal
immutable revision label, derives audit-logger presence from the actual PEP
configuration, and requires explicit approval to be fresh, verifier-accepted,
single-use, and bound to the current action digest.

Remaining risk: the library does not verify Git object existence, authenticate
the actor, sign approvals, or provide tamper-evident log storage. Those facts must
come from trusted host services.

### Policy and extension integrity

An agent may try to weaken doctrine or evaluators before requesting a forbidden
action. Declared writes to bundled policy/runtime paths are denied. Unknown tools
are rejected by the shipped adapters, and evaluator exceptions return a
system-level denial.

Remaining risk: installing or loading a malicious custom evaluator is equivalent
to running malicious application code. Extension installation and evaluator
selection are operator-controlled supply-chain decisions.

### Packaging and release

An attacker may attempt dependency substitution, workflow drift, artifact
replacement, or publication with a stolen long-lived token. The project uses a
dependency-free runtime, SHA-pinned workflow actions, isolated package-content
verification, an SPDX SBOM, checksums, GitHub attestations, and PyPI OpenID
Connect trusted publishing.

Remaining risk: maintainer account compromise, compromised upstream build
packages, misconfigured GitHub environments, or skipped attestation verification
remain outside the library runtime.

## Severity Calibration (Critical, High, Medium, Low)

### Critical

A realistic unauthenticated or agent-controlled path that bypasses the PEP and
directly executes arbitrary commands or writes outside the workspace in a host
that represents itself as enforced. A release-pipeline compromise that publishes
attacker code under the trusted package identity may also be critical.

### High

A default-adapter or core-evaluator flaw that lets an untrusted proposal mutate
protected policy, escape scope, forge an authorization-relevant approval, or turn
an evaluator failure into `ALLOW` under documented integration assumptions.

### Medium

A bypass requiring a non-default custom adapter, an operator misconfiguration
that contradicts required setup, a denial-of-service through bounded but
expensive inputs, or sensitive operational metadata exposed without credentials
or arbitrary code execution.

### Low

Ambiguous error text, low-impact information disclosure, documentation that
could encourage insecure wiring without directly creating a bypass, or defense-
in-depth hardening where the documented boundary already excludes the behavior.

Severity must be reduced when the required attacker-controlled boundary does not
exist in the repository’s real usage, and raised only when code evidence shows a
reachable privileged sink and concrete impact.
