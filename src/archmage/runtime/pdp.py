from dataclasses import replace
from datetime import datetime, timezone
from threading import Lock
from typing import Callable, List, Optional, Protocol, Sequence

from .domain import (
    ActionDigest,
    ActionProposal,
    ApprovalRecord,
    AuditEvent,
    Obligation,
    PolicyContext,
    PolicyVerdict,
    RepairInstruction,
    VerdictDecision,
)
from .evaluators import BaseEvaluator
from .exceptions import (
    PolicyViolationError,
    RepairRequiredError,
    UnfulfilledObligationError,
)


class AuditLogger(Protocol):
    """Sink contract for structured policy audit events."""

    def log(self, event: AuditEvent) -> None:
        """Persist or forward one audit event."""


class PolicyDecisionPoint:
    def __init__(self, evaluators: List[BaseEvaluator]):
        self.evaluators = evaluators

    def evaluate(self, action: ActionProposal, context: PolicyContext) -> PolicyVerdict:
        try:
            digest = ActionDigest.compute(action)
        except (AttributeError, RecursionError, TypeError, ValueError):
            return self._default_deny(
                action,
                "invalid-action",
                "Action proposal could not be canonicalized.",
            )
        verdicts = []

        for evaluator in self.evaluators:
            try:
                verdict = evaluator.evaluate(action, context, digest.digest_hash)
            except Exception:
                return self._default_deny(
                    action,
                    digest.digest_hash,
                    f"Evaluator {type(evaluator).__name__} failed closed.",
                )
            verdicts.append(verdict)

        return self.aggregate_verdicts(verdicts, action, digest.digest_hash)

    def aggregate_verdicts(
        self, verdicts: List[PolicyVerdict], action: ActionProposal, digest: str
    ) -> PolicyVerdict:
        # Precedence: DENY > ESCALATE > REPAIR > ALLOW_WITH_OBLIGATIONS > ALLOW
        precedence = {
            VerdictDecision.DENY: 5,
            VerdictDecision.ESCALATE: 4,
            VerdictDecision.REPAIR: 3,
            VerdictDecision.ALLOW_WITH_OBLIGATIONS: 2,
            VerdictDecision.ALLOW: 1,
        }

        highest_verdict = None
        highest_score = 0

        obligations = []
        evidence_required = []

        for v in verdicts:
            score = precedence[v.decision]
            if score > highest_score:
                highest_score = score
                highest_verdict = v

            obligations.extend(v.obligations)
            evidence_required.extend(v.evidence_required)

        if not highest_verdict:
            return self._default_deny(action, digest, "No evaluators ran.")

        if highest_verdict.decision in (
            VerdictDecision.ALLOW,
            VerdictDecision.ALLOW_WITH_OBLIGATIONS,
        ):
            if obligations:
                highest_verdict.decision = VerdictDecision.ALLOW_WITH_OBLIGATIONS
                highest_verdict.obligations = obligations
            if evidence_required:
                highest_verdict.evidence_required = evidence_required

        return highest_verdict

    def _default_deny(self, action: ActionProposal, digest: str, reason: str) -> PolicyVerdict:
        actor_id = getattr(getattr(action, "actor", None), "actor_id", None) or "unknown"
        task_id = getattr(action, "task_id", None) or "unknown"
        target_paths = getattr(action, "target_paths", None)
        artifacts = list(target_paths) if isinstance(target_paths, list) else []
        return PolicyVerdict(
            decision=VerdictDecision.DENY,
            policy_id="SYS-FAIL-CLOSED",
            policy_version="1.0.0",
            law_ids=[],
            severity="critical",
            confidence=1.0,
            actor_id=actor_id,
            task_id=task_id,
            action_digest=digest,
            artifacts=artifacts,
            finding=reason,
        )


class PolicyEnforcementPoint:
    def __init__(
        self,
        pdp: PolicyDecisionPoint,
        audit_logger: Optional[AuditLogger] = None,
        repair_handler: Optional[Callable[[Optional[RepairInstruction]], None]] = None,
        acknowledged_obligations: Optional[Sequence[str]] = None,
        approval_records: Optional[Sequence[ApprovalRecord]] = None,
        approval_verifier: Optional[
            Callable[[ApprovalRecord, PolicyVerdict, Obligation], bool]
        ] = None,
        approval_max_age_seconds: int = 300,
    ) -> None:
        if approval_max_age_seconds <= 0:
            raise ValueError("approval_max_age_seconds must be positive")
        self.pdp = pdp
        self.audit_logger = audit_logger
        self.repair_handler = repair_handler
        self.acknowledged_obligations = list(acknowledged_obligations or ())
        self.approval_records = list(approval_records or ())
        self.approval_verifier = approval_verifier
        self.approval_max_age_seconds = approval_max_age_seconds
        self._consumed_approval_ids: set[str] = set()
        self._approval_lock = Lock()

    def intercept(
        self,
        action: ActionProposal,
        context: PolicyContext,
        acknowledged_obligations: Optional[List[str]] = None,
        approval_records: Optional[Sequence[ApprovalRecord]] = None,
    ) -> VerdictDecision:
        return self.evaluate_and_enforce(
            action,
            context,
            acknowledged_obligations=acknowledged_obligations,
            approval_records=approval_records,
        ).decision

    def evaluate_and_enforce(
        self,
        action: ActionProposal,
        context: PolicyContext,
        acknowledged_obligations: Optional[List[str]] = None,
        approval_records: Optional[Sequence[ApprovalRecord]] = None,
    ) -> PolicyVerdict:
        """Return the verdict only after audit and enforcement have completed."""

        effective_context = replace(
            context,
            audit_logger_configured=self.audit_logger is not None,
        )
        verdict = self.pdp.evaluate(action, effective_context)

        self.record_audit(action, verdict)

        if verdict.decision in (VerdictDecision.DENY, VerdictDecision.ESCALATE):
            self.enforce_block(verdict)
        elif verdict.decision == VerdictDecision.REPAIR:
            self.enforce_repair(verdict)
        elif verdict.decision == VerdictDecision.ALLOW_WITH_OBLIGATIONS:
            self.enforce_obligations(
                verdict,
                acknowledged_obligations=acknowledged_obligations,
                approval_records=approval_records,
            )

        return verdict

    def record_audit(self, action: ActionProposal, verdict: PolicyVerdict) -> None:
        event = AuditEvent(
            event_id="evt-" + verdict.action_digest[:8],
            action_digest=verdict.action_digest,
            verdicts=[verdict],
            final_decision=verdict.decision,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        if self.audit_logger:
            self.audit_logger.log(event)

    def enforce_block(self, verdict: PolicyVerdict) -> None:
        raise PolicyViolationError(
            f"Action blocked by policy {verdict.policy_id} "
            f"(Laws: {verdict.law_ids}): {verdict.finding}",
            verdict=verdict,
        )

    def enforce_repair(self, verdict: PolicyVerdict) -> None:
        if self.repair_handler:
            self.repair_handler(verdict.repair)
        else:
            raise RepairRequiredError(
                f"Action requires repair under policy {verdict.policy_id}: {verdict.finding}",
                verdict=verdict,
                repair=verdict.repair,
            )

    def enforce_obligations(
        self,
        verdict: PolicyVerdict,
        acknowledged_obligations: Optional[List[str]] = None,
        approval_records: Optional[Sequence[ApprovalRecord]] = None,
    ) -> None:
        ack_list = (acknowledged_obligations or []) + (self.acknowledged_obligations or [])
        ack_set = set(ack_list)
        available_records = list(approval_records or ()) + self.approval_records
        consumed_now: set[str] = set()
        satisfied_approval_types: set[str] = set()

        with self._approval_lock:
            for obligation in verdict.obligations:
                if obligation.type == "explicit_approval":
                    if obligation.type in satisfied_approval_types:
                        continue
                    approval = self._matching_approval(
                        available_records,
                        verdict,
                        obligation,
                        consumed_now,
                    )
                    if approval is None:
                        self._raise_unfulfilled(verdict, obligation)
                    assert approval is not None
                    consumed_now.add(approval.approval_id)
                    satisfied_approval_types.add(obligation.type)
                elif obligation.type not in ack_set:
                    self._raise_unfulfilled(verdict, obligation)
            self._consumed_approval_ids.update(consumed_now)

    def _matching_approval(
        self,
        records: Sequence[ApprovalRecord],
        verdict: PolicyVerdict,
        obligation: Obligation,
        consumed_now: set[str],
    ) -> Optional[ApprovalRecord]:
        for record in records:
            if (
                not isinstance(record, ApprovalRecord)
                or not isinstance(record.approval_id, str)
                or not record.approval_id.strip()
                or record.approval_id in self._consumed_approval_ids
                or record.approval_id in consumed_now
                or record.action_digest != verdict.action_digest
                or record.obligation_type != obligation.type
                or not isinstance(record.approver_id, str)
                or record.approver_id.strip().lower() in {"", "none", "unknown"}
                or not self._approval_is_fresh(record)
                or self.approval_verifier is None
            ):
                continue
            try:
                if self.approval_verifier(record, verdict, obligation):
                    return record
            except Exception:
                continue
        return None

    def _approval_is_fresh(self, record: ApprovalRecord) -> bool:
        if not isinstance(record.timestamp, str):
            return False
        try:
            timestamp = datetime.fromisoformat(record.timestamp.replace("Z", "+00:00"))
        except ValueError:
            return False
        if timestamp.tzinfo is None:
            return False
        age_seconds = (
            datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)
        ).total_seconds()
        return -30 <= age_seconds <= self.approval_max_age_seconds

    @staticmethod
    def _raise_unfulfilled(verdict: PolicyVerdict, obligation: Obligation) -> None:
        raise UnfulfilledObligationError(
            f"Unfulfilled obligation '{obligation.type}' required before "
            f"{obligation.required_before} under policy {verdict.policy_id}",
            verdict=verdict,
            obligation=obligation,
        )
