---
name: archmage-change-control
description: "Triggers on deletions, schema migrations, public-contract changes, and high-risk actions."
version: "1.0.0"
scope: "irreversible-actions"
owned_laws: [3, 4, 8]
purpose: "Govern policy modifications, dependency removals, and high-risk permission changes."
explicit_exclusions:
  - "Stateless local evaluations"
inputs:
  - ActionProposal
outputs:
  - PolicyVerdict
required_context:
  - ApprovalRecord
policies_invoked:
  - POL-SOVEREIGNTY-01
allowed_tools: []
decision_authority: "Primary for high-risk Laws 3, 4, and 8"
repair_behavior: "Require explicit human approval record"
failure_behavior: "ESCALATE"
references:
  - "../../doctrine/laws.md"
evaluation_case_locations:
  - "../../evals/"
---

# archmage-change-control

## Responsibilities
- Deletions.
- Schema migrations.
- Public-contract changes.
- Dependency removal.
- Permission changes.
- Protected-path writes.
- Policy modifications.
- Irreversible or partially reversible actions.
- Human approval and exception records.
