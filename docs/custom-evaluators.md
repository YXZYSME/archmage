<!-- YXZYS | saeng-il ai [development] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Writing custom evaluators

The third-party entry-point API is not stable in the first package release.
Inject custom evaluators explicitly so upgrades cannot silently discover and
execute an installed package.

```python
from archmage import PolicyDecisionPoint
from archmage.evaluators import BaseEvaluator


class RepositoryRuleEvaluator(BaseEvaluator):
    def evaluate(self, action, context, action_digest):
        # Return a complete PolicyVerdict for every path.
        ...


pdp = PolicyDecisionPoint([RepositoryRuleEvaluator()])
```

A production evaluator should:

- have one documented policy identifier and responsibility;
- validate untrusted arguments before use;
- avoid filesystem, network, or process side effects;
- return a complete typed verdict for compliant and noncompliant paths;
- raise on unexpected internal failure so the PDP can fail closed;
- include intervention, compliant-path, malformed-input, and regression tests.

Do not return `ALLOW` when parsing or external evaluation fails.
