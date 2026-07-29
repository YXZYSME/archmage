---
name: archmage-evidence
description: "Triggers on performance, scaling, reliability, security, or compatibility claims, and testing."
version: "1.0.0"
scope: "verification"
owned_laws: [8]
purpose: "Enforce evidence and provenance for claims."
explicit_exclusions:
  - "Trivial stylistic changes"
inputs:
  - ActionProposal
outputs:
  - PolicyVerdict
required_context:
  - EvidenceRecord
policies_invoked:
  - POL-VERIFICATION-01
allowed_tools: []
decision_authority: "Primary for Law 8"
repair_behavior: "Require evidence attachment"
failure_behavior: "DENY"
references:
  - "../../doctrine/laws.md"
evaluation_case_locations:
  - "../../evals/"
---

# archmage-evidence

## Responsibilities
- Assumption, prediction, method, and result records.
- Test evidence.
- Benchmarks.
- Static-analysis evidence.
- Compatibility evidence.
- Provenance and integrity.
- Unsupported claim detection.
