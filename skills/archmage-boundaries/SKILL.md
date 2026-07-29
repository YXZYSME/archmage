---
name: archmage-boundaries
description: "Triggers on module ownership, cross-unit access, or dependency direction changes."
version: "1.0.0"
scope: "internal-boundaries"
owned_laws: [4, 5]
purpose: "Enforce module ownership, internal-versus-public boundaries, cross-unit access, dependency direction, and agent isolation."
explicit_exclusions:
  - "Intra-module refactoring"
inputs:
  - ActionProposal
outputs:
  - PolicyVerdict
required_context:
  - WorkspacePath
policies_invoked:
  - POL-BOUNDARY-01
allowed_tools: []
decision_authority: "Primary for Laws 4 and 5"
repair_behavior: "Block cross-unit access to internals"
failure_behavior: "ESCALATE"
references:
  - "../../doctrine/laws.md"
evaluation_case_locations:
  - "../../evals/"
---

# archmage-boundaries

## Responsibilities
- Module ownership.
- Internal-versus-public boundaries.
- Cross-unit access.
- Dependency direction.
- Volatile implementation details.
- Agent isolation.
- Contract-only handoffs.
