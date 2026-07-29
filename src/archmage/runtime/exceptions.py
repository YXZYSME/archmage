from typing import Optional

from .domain import Obligation, PolicyVerdict, RepairInstruction


class PolicyViolationError(Exception):
    """Raised when an action is blocked by a DENY or ESCALATE policy verdict."""

    def __init__(self, message: str, verdict: PolicyVerdict):
        super().__init__(message)
        self.verdict = verdict


class RepairRequiredError(Exception):
    """Raised when an action requires repair before it can proceed."""

    def __init__(
        self, message: str, verdict: PolicyVerdict, repair: Optional[RepairInstruction] = None
    ):
        super().__init__(message)
        self.verdict = verdict
        self.repair = repair


class UnfulfilledObligationError(Exception):
    """Raised when an action has unfulfilled obligations."""

    def __init__(self, message: str, verdict: PolicyVerdict, obligation: Obligation):
        super().__init__(message)
        self.verdict = verdict
        self.obligation = obligation
