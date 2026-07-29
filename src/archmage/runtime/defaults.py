# ──────────────────────────────────────────────────────
# YXZYS | saeng-il ai [development]
# © YXZYS @ saengil.ai — All rights reserved.
# ──────────────────────────────────────────────────────
"""Factory for the documented built-in ARCHMAGE policy set."""

from .evaluators import (
    ConcordEvaluator,
    ConservatismEvaluator,
    GenericLabelsEvaluator,
    IdentityDeclarationEvaluator,
    LineageEvaluator,
    ProtectedPolicyMutationEvaluator,
    ScopeEnforcementEvaluator,
    SovereigntyEvaluator,
    StewardshipEvaluator,
    TransparencyEvaluator,
    VerificationEvaluator,
)
from .pdp import PolicyDecisionPoint


def create_default_policy_decision_point() -> PolicyDecisionPoint:
    """Create a decision point containing the eleven documented core evaluators."""

    return PolicyDecisionPoint(
        [
            ScopeEnforcementEvaluator(),
            LineageEvaluator(),
            StewardshipEvaluator(),
            ConcordEvaluator(),
            TransparencyEvaluator(),
            ConservatismEvaluator(),
            VerificationEvaluator(),
            SovereigntyEvaluator(),
            ProtectedPolicyMutationEvaluator(),
            GenericLabelsEvaluator(),
            IdentityDeclarationEvaluator(),
        ]
    )
