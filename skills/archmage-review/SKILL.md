---
name: archmage-review
description: "Triggers on final policy aggregation and decision phase."
version: "1.0.0"
scope: "verdict-aggregation"
owned_laws: []
purpose: "Aggregate subskill findings, deduplicate, and resolve policy precedence."
explicit_exclusions:
  - "Direct policy definition"
inputs:
  - List[PolicyVerdict]
outputs:
  - PolicyVerdict
required_context:
  - ActionProposal
policies_invoked: []
allowed_tools: []
decision_authority: "Final Aggregation"
repair_behavior: "Delegate to specific subskills"
failure_behavior: "ESCALATE"
references:
  - "../../doctrine/laws.md"
evaluation_case_locations:
  - "../../evals/"
---

# archmage-review

## Responsibilities
- Aggregate subskill findings.
- Deduplicate findings.
- Resolve policy precedence.
- Produce concise review output.
- Never redefine or independently reinterpret another subskill’s policies.
