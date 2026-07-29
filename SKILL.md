---
name: archmage
description: "Core orchestration skill for ARCHMAGE v2 policy enforcement. Triggers on code creation, editing, refactoring, architecture work, interface design, agent design, configuration changes, tool-contract changes, technical review, destructive actions, and public API changes."
version: "2.0.0"
scope: "global"
owned_laws: []
purpose: "Accept task envelope, classify risk, select subskills, establish enforcement order, aggregate verdicts, return pipeline decision, and record evidence."
explicit_exclusions:
  - "Casual conversation"
  - "Nontechnical tasks"
  - "Pure research synthesis without a development action"
  - "General summaries that do not modify or approve technical artifacts"
inputs:
  - TaskEnvelope
outputs:
  - VerdictDecision
required_context:
  - WorkspacePath
  - ActorIdentity
policies_invoked: []
allowed_tools: []
decision_authority: "Aggregate"
repair_behavior: "Delegate to subskills"
failure_behavior: "ESCALATE"
references:
  - "src/archmage/doctrine/laws.md"
  - "src/archmage/doctrine/risk-model.yaml"
evaluation_case_locations:
  - "evals/"
---

# ARCHMAGE v2 Orchestration Skill

ARCHMAGE is a portable, progressively disclosed skill bundle and runtime policy-enforcement layer for autonomous development-agent pipelines. 
It preserves the philosophical intent of the YXZYS 8 Laws, translating them into deterministic, testable policies.

## Instructions

1. Normalize incoming tasks into a `TaskEnvelope`.
2. Classify the task type, affected artifacts, side effects, and risk.
3. Select applicable subskills based on task classification.
4. Establish enforcement order and delegate validation to subskills.
5. Aggregate policy verdicts using the `PolicyDecisionPoint`.
6. Return a final pipeline decision (`ALLOW`, `DENY`, `ESCALATE`, `REPAIR`, `ALLOW_WITH_OBLIGATIONS`).
7. Direct the runtime to record evidence and audit events.

> **Note**: This top-level skill is thin. It does not enforce policies directly. It orchestrates subskills (`archmage-contracts`, `archmage-boundaries`, etc.) which contain specific enforcement logic.

Do not load all subskills into context unless their specific task signals apply.
