<!-- YXZYS | saeng-il ai [systems] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Limitations

ARCHMAGE is an application-layer policy runtime. The following boundaries are
intentional and material.

## Not an operating-system sandbox

ARCHMAGE does not create containers, kernel namespaces, filesystem ACLs, network
firewalls, or process isolation. Host controls must prevent direct tool access
around the adapter.

## No universal interception

Only actions routed through a configured PEP or adapter are evaluated. Native
shells, alternate tool clients, plugins, subprocesses, and direct filesystem
APIs can bypass the runtime unless the host constrains them.

## Deterministic rules are not intent understanding

The core evaluators inspect declared structure and metadata. They do not prove
that arbitrary code is benign, detect every command encoding, or understand all
semantic equivalents of a dangerous intent.

The shipped adapters reject unknown tools and require the path field for each
registered tool. They cannot infer every path, network destination, credential,
or side effect embedded in an arbitrary shell command. The default policy places
all `run_command` calls behind an explicit obligation, but that is not a
substitute for a sandbox or host-derived effect inventory.

## Prompt injection is only indirectly constrained

ARCHMAGE can block a resulting tool proposal when it violates a known policy.
It does not sanitize retrieved text or guarantee that an injected instruction
will translate into a detectable proposal.

## Metadata depends on a trusted boundary

Actor, task, workspace, revision, ownership, and evidence metadata must be
supplied by a trusted host boundary. An integration that lets the governed agent
forge those fields weakens the policy result.

## Approval verification is host-supplied

The PEP binds an `ApprovalRecord` to the exact action digest, checks freshness,
requires a concrete approver, invokes the configured verifier, and consumes the
record once. The host still owns authentication, cryptographic or session
verification, approver authorization, revocation, and the decision to issue the
record. Without an `approval_verifier`, explicit approval fails closed.

## Auditing is integration-dependent

The PEP can emit audit events to a configured logger. Durable storage,
tamper-evident chaining, retention, redaction, and external monitoring are not
provided by the current package.

## Repair is advisory

A `REPAIR` verdict provides a repair contract. The runtime does not prove that a
repair handler changed the proposal correctly. The resulting proposal must be
resubmitted and evaluated.

## No stable plugin discovery API

Custom evaluators can be injected explicitly. Automatic third-party entry-point
discovery is deferred until evaluator contracts and trust semantics stabilize.
