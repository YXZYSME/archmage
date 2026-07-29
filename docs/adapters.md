<!-- YXZYS | saeng-il ai [integration] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Adapters

## Compatibility matrix

| Integration | Status | Evidence |
|---|---|---|
| Generic tool-call adapter | Available | Unit and adversarial tests |
| Antigravity adapter | Reference implementation | Unit and boundary tests |
| LangGraph | Roadmap | No shipped adapter |
| AutoGen / CrewAI | Roadmap | No shipped adapter |
| LlamaIndex | Roadmap | No shipped adapter |
| MCP server | Roadmap | No shipped adapter |

## Required execution context

Both shipped adapters require:

| Field | Contract |
|---|---|
| `task_id` | Non-empty concrete task identity |
| `actor_id` | Non-empty concrete actor identity |
| `workspace` | Absolute workspace path |
| `git_sha` | Immutable 7–64 character hexadecimal revision |
| `environment` | Optional label; defaults to `local` |

Missing or ambient defaults are rejected before policy evaluation. In
particular, adapters do not fall back to `/`, `unknown`, or `HEAD`.

Tool arguments must contain only canonical JSON values: null, booleans, finite
numbers, strings, arrays, and string-keyed objects. Bytes, sets, tuples, custom
objects, non-finite floats, cycles, and non-string mapping keys are rejected.

The default adapters are fail-closed registries, not universal tool decoders.
The generic adapter currently accepts `write_to_file` and `run_command`.
The Antigravity reference accepts `write_to_file`, `run_command`,
`multi_replace_file_content`, and `view_file`. An unregistered tool or a
registered tool missing its required path field is rejected before evaluation.

## Generic adapter

```python
from archmage import PolicyEnforcementPoint, create_default_policy_decision_point
from archmage.adapters import GenericAdapter


class AuditCollector:
    def __init__(self):
        self.events = []

    def log(self, event):
        self.events.append(event)


adapter = GenericAdapter(
    PolicyEnforcementPoint(
        create_default_policy_decision_point(),
        audit_logger=AuditCollector(),
    )
)

allowed = adapter.intercept_tool_call(
    "write_to_file",
    {"TargetFile": "src/feature.py", "CodeContent": "value = 1\n"},
    {
        "task_id": "task-42",
        "actor_id": "coding-agent",
        "workspace": "/workspace/project",
        "git_sha": "0123456789abcdef0123456789abcdef01234567",
        "environment": "local",
    },
)
```

The boolean is `True` only for `ALLOW` or fulfilled
`ALLOW_WITH_OBLIGATIONS`. A handled `REPAIR` still returns `False`; the repaired
proposal must be resubmitted.

`run_command` is declared as a `shell_command` side effect, so the default policy
requires an `explicit_approval` obligation before dispatch. On the first attempt,
capture the `UnfulfilledObligationError.verdict.action_digest`, obtain a fresh
approval from a trusted host authority, and retry with an `ApprovalRecord` passed
through the adapter's `approval_records` parameter. The PEP must have an
`approval_verifier`; raw obligation-name strings never satisfy explicit approval.

ARCHMAGE does not parse a command into a complete set of filesystem or network
effects; run commands inside a sandbox and supply any affected resources through
a host-specific validated adapter.
