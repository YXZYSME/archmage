---
name: archmage-contracts
description: "Triggers on public API, schema, agent-card, tool-contract, or public-interface changes."
version: "1.0.0"
scope: "public-interfaces"
owned_laws: [1, 3]
purpose: "Enforce public interface shape, contract-first development, input/output schemas, and API depth."
explicit_exclusions:
  - "Internal refactoring without public signature changes"
inputs:
  - ActionProposal
outputs:
  - PolicyVerdict
required_context:
  - WorkspacePath
policies_invoked:
  - POL-CONTRACT-01
allowed_tools: []
decision_authority: "Primary for Laws 1 and 3"
repair_behavior: "Require contract definition before execution"
failure_behavior: "ESCALATE"
references:
  - "../../doctrine/laws.md"
evaluation_case_locations:
  - "../../evals/"
implementation:
  - "../../src/archmage/evaluators/contracts.py"
---

# archmage-contracts

## Responsibilities
- Public interface shape.
- Contract-first development.
- Input/output schemas.
- Error contracts.
- Compatibility expectations.
- API depth.
- Public-surface changes.
- Contract tests.
