<!-- YXZYS | saeng-il ai [development] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Quickstart

## Install

Before the first package release, install from a reviewed checkout:

```bash
python -m pip install .
```

After the first package release:

```bash
python -m pip install archmage-ai
```

The distribution name is `archmage-ai`; the Python import is `archmage`.

## Evaluate an action

```python
from archmage import (
    ActionProposal,
    ActorIdentity,
    PolicyContext,
    create_default_policy_decision_point,
)

proposal = ActionProposal(
    task_id="task-42",
    actor=ActorIdentity(actor_id="coding-agent", actor_type="agent"),
    operation="write_file",
    tool="write_to_file",
    arguments={"TargetFile": "src/feature.py"},
    target_paths=["src/feature.py"],
    requested_side_effects=[],
    repository_revision="0123456789abcdef0123456789abcdef01234567",
    environment="local",
)
context = PolicyContext(
    workspace="/workspace/project",
    environment="local",
    audit_logger_configured=True,
)

verdict = create_default_policy_decision_point().evaluate(proposal, context)
print(verdict.decision)
```

For direct PDP use, `audit_logger_configured=True` is an operator assertion. A
PEP ignores that assertion and derives the effective value from its actual
configured `audit_logger`.

## Make the verdict authoritative

Evaluation alone does not block a tool. Route the action through a
`PolicyEnforcementPoint` or an adapter, and dispatch only after an allowed
decision:

```python
from archmage import PolicyEnforcementPoint, create_default_policy_decision_point


class AuditCollector:
    def __init__(self):
        self.events = []

    def log(self, event):
        self.events.append(event)


pep = PolicyEnforcementPoint(
    create_default_policy_decision_point(),
    audit_logger=AuditCollector(),
)
decision = pep.intercept(proposal, context)
```

`DENY` and `ESCALATE` raise `PolicyViolationError`. `REPAIR` raises
`RepairRequiredError` unless a repair handler is configured.
`ALLOW_WITH_OBLIGATIONS` raises `UnfulfilledObligationError` until the required
obligations are acknowledged.

## Next

- Review the [adapter context contract](adapters.md).
- Learn the [verdict precedence model](policy-model.md).
- Run the [gold cases](benchmarks.md).
