"""Public ARCHMAGE package interface."""

from .runtime import (
    ActionProposal,
    ActorIdentity,
    ApprovalRecord,
    PolicyContext,
    PolicyDecisionPoint,
    PolicyEnforcementPoint,
    PolicyVerdict,
    ProposedEffect,
    VerdictDecision,
    create_default_policy_decision_point,
)

__version__ = "2.0.0"

__all__ = [
    "ActionProposal",
    "ActorIdentity",
    "ApprovalRecord",
    "PolicyContext",
    "PolicyDecisionPoint",
    "PolicyEnforcementPoint",
    "PolicyVerdict",
    "ProposedEffect",
    "VerdictDecision",
    "create_default_policy_decision_point",
]
