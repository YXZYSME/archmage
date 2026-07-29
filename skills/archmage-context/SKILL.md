---
name: archmage-context
description: "Triggers on environment setup, task admission, handoffs, and ambient-state reads."
version: "1.0.0"
scope: "execution-context"
owned_laws: [5, 6]
purpose: "Enforce explicit actor identity, declare dependencies, and enforce context budgets."
explicit_exclusions:
  - "Stateless local evaluations"
inputs:
  - ActionProposal
outputs:
  - PolicyVerdict
required_context:
  - ActorIdentity
policies_invoked:
  - POL-IDENTITY-01
allowed_tools: []
decision_authority: "Primary for Laws 5 and 6"
repair_behavior: "Inject required context headers"
failure_behavior: "DENY"
references:
  - "../../doctrine/laws.md"
evaluation_case_locations:
  - "../../evals/"
---

# archmage-context

## Responsibilities
- Explicit actor and execution identity.
- Declared dependencies.
- Allowed and prohibited scope.
- Ambient-state detection.
- Context budgets.
- Mixed-concern detection.
- Clean handoff context.
