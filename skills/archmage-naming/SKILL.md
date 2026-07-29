---
name: archmage-naming
description: "Triggers on file creation, class/function renaming, and commit or task labeling."
version: "1.0.0"
scope: "naming-conventions"
owned_laws: [2, 7]
purpose: "Enforce canonical glossary, prevent synonym drift, and reject generic artifact names."
explicit_exclusions:
  - "Unlabeled temporary artifacts in approved /tmp directories"
inputs:
  - ActionProposal
outputs:
  - PolicyVerdict
required_context:
  - WorkspacePath
policies_invoked:
  - POL-LABELING-01
allowed_tools: []
decision_authority: "Primary for Laws 2 and 7"
repair_behavior: "Rename artifact to adhere to glossary"
failure_behavior: "WARN"
references:
  - "../../doctrine/glossary.yaml"
evaluation_case_locations:
  - "../../evals/"
---

# archmage-naming

## Responsibilities
- Canonical glossary enforcement.
- Synonym drift.
- Generic or unlabeled artifacts.
- Rename migrations.
- Commit, task, function, class, file, config, and agent labels.
