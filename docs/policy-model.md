<!-- YXZYS | saeng-il ai [systems] — © YXZYS @ saengil.ai -->
<!-- yxzys:sg:ai -->

# Policy model

## Core policy set

| Policy | Evaluator | Intervention |
|---|---|---|
| `POL-TERRITORY-01` | `ScopeEnforcementEvaluator` | Denies targets outside the resolved workspace |
| `POL-LINEAGE-01` | `LineageEvaluator` | Denies missing or mutable revision identities |
| `POL-STEWARDSHIP-01` | `StewardshipEvaluator` | Denies declared ownership mismatches |
| `POL-CONCORD-01` | `ConcordEvaluator` | Adds a glossary-review obligation |
| `POL-TRANSPARENCY-01` | `TransparencyEvaluator` | Denies declared side effects without audit configuration |
| `POL-CONSERVATISM-01` | `ConservatismEvaluator` | Requires approval for declared irreversible effects |
| `POL-VERIFICATION-01` | `VerificationEvaluator` | Requests repair when claims lack evidence |
| `POL-SOVEREIGNTY-01` | `SovereigntyEvaluator` | Denies actor-type scope mismatches |
| `POL-MUTATION-01` | `ProtectedPolicyMutationEvaluator` | Denies writes to protected runtime and doctrine paths |
| `POL-LABELING-01` | `GenericLabelsEvaluator` | Requests a precise artifact name |
| `POL-IDENTITY-01` | `IdentityDeclarationEvaluator` | Denies undeclared actor or task identity |

## Aggregation

The PDP uses the following precedence:

```text
DENY > ESCALATE > REPAIR > ALLOW_WITH_OBLIGATIONS > ALLOW
```

If an evaluator raises an exception, the PDP returns a `SYS-FAIL-CLOSED` denial.
If no evaluators run, the PDP also denies.

## Policy claims

Each policy claim should map to:

1. a concrete evaluator;
2. at least one intervention test;
3. at least one compliant-path test;
4. a gold case when the behavior is part of the public benchmark.

Text that describes a roadmap policy is not evidence that the runtime enforces
it.
