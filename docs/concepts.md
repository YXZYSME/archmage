<!-- YXZYS | saeng-il ai [systems] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Core concepts

## Action proposal

`ActionProposal` is the normalized description of a tool action. It declares:

- the task and actor identities;
- the operation and native tool;
- arguments and target paths;
- expected side effects;
- an immutable repository revision;
- the execution environment.

The proposal is an evaluation input. It is not permission by itself.

## Policy context

`PolicyContext` declares the workspace boundary and environment used by
evaluators. Adapters require an absolute workspace path and reject undeclared
actor, task, or revision metadata.

## Action digest

`ActionDigest` is the SHA-256 digest of the normalized proposal. The canonical
form accepts only JSON primitives, arrays, and string-keyed objects; ambiguous
Python values such as bytes, sets, non-finite floats, or custom objects are
rejected. Verdicts and audit events use the digest to bind a decision to the
exact evaluated action.

## Approval record

An `explicit_approval` obligation requires a fresh `ApprovalRecord` whose
`action_digest` matches the current verdict. The embedding host must configure an
`approval_verifier` that authenticates the approver and approval identifier.
Approval records are single-use within a PEP instance. A raw acknowledged
obligation name can satisfy non-security workflow obligations, but it cannot
satisfy `explicit_approval`.

## Evaluator

An evaluator maps one proposal and context to one `PolicyVerdict`. Core
evaluators are deterministic and must fail closed when evaluation cannot
complete.

## Verdict

The decision is one of:

- `ALLOW`: the evaluated action is compliant.
- `ALLOW_WITH_OBLIGATIONS`: dispatch is conditional on named obligations.
- `REPAIR`: the proposal must change before dispatch.
- `DENY`: dispatch must not occur.
- `ESCALATE`: a human or external authority must decide.

## PEP and PDP

The Policy Decision Point (PDP) runs and aggregates evaluators. The Policy
Enforcement Point (PEP) turns the aggregate decision into executable behavior,
including typed exceptions for blocked, repairable, or conditional actions.
