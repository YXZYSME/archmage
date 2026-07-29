import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from ._serialization import canonical_json_bytes


class VerdictDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_OBLIGATIONS = "ALLOW_WITH_OBLIGATIONS"
    REPAIR = "REPAIR"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


@dataclass
class ActorIdentity:
    actor_id: str
    actor_type: str  # "human" or "agent"
    credentials: Optional[Dict[str, str]] = field(default_factory=dict)


@dataclass
class ArtifactScope:
    allowed_paths: List[str]
    allowed_operations: List[str]


@dataclass
class ProposedEffect:
    effect_type: str  # "file_write", "shell_command", "api_call"
    target: str
    payload: Dict[str, Any]


@dataclass
class ActionProposal:
    task_id: str
    actor: ActorIdentity
    operation: str
    tool: str
    arguments: Dict[str, Any]
    target_paths: List[str]
    requested_side_effects: List[ProposedEffect]
    repository_revision: str
    environment: str


@dataclass
class ActionDigest:
    digest_hash: str
    action_ref: ActionProposal

    @staticmethod
    def compute(action: ActionProposal) -> "ActionDigest":
        canonical_action = {
            "task_id": action.task_id,
            "actor": {
                "actor_id": action.actor.actor_id,
                "actor_type": action.actor.actor_type,
                "credentials": action.actor.credentials,
            },
            "operation": action.operation,
            "tool": action.tool,
            "arguments": action.arguments,
            "target_paths": action.target_paths,
            "requested_side_effects": [
                {
                    "effect_type": effect.effect_type,
                    "target": effect.target,
                    "payload": effect.payload,
                }
                for effect in action.requested_side_effects
            ],
            "repository_revision": action.repository_revision,
            "environment": action.environment,
        }
        digest = hashlib.sha256(canonical_json_bytes(canonical_action)).hexdigest()
        return ActionDigest(digest_hash=digest, action_ref=action)


@dataclass
class Policy:
    policy_id: str
    law_ids: List[int]
    name: str
    description: str


@dataclass
class PolicyContext:
    workspace: str
    environment: str
    audit_logger_configured: bool = False


@dataclass
class PolicyFinding:
    finding: str
    severity: str


@dataclass
class RepairInstruction:
    operation: str
    required_fields: List[str]


@dataclass
class Obligation:
    type: str
    required_before: str


@dataclass
class PolicyVerdict:
    decision: VerdictDecision
    policy_id: str
    policy_version: str
    law_ids: List[int]
    severity: str
    confidence: float
    actor_id: str
    task_id: str
    action_digest: str
    artifacts: List[str]
    finding: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    repair: Optional[RepairInstruction] = None
    obligations: List[Obligation] = field(default_factory=list)
    evidence_required: List[str] = field(default_factory=list)


@dataclass
class EvidenceReference:
    reference_type: str
    uri: str


@dataclass
class EvidenceRecord:
    evidence_id: str
    task_id: str
    actor: str
    claim_type: str
    statement: str
    assumption: str
    prediction: str
    verification_method: str
    command_used: str
    execution_environment: str
    repository_revision: str
    policy_version: str
    result: str
    artifact_reference: EvidenceReference
    integrity_hash: str
    timestamp: str


@dataclass
class ExceptionRecord:
    exception_id: str
    policy_id: str
    actor_id: str
    reason: str
    expires_at: str


@dataclass
class ApprovalRecord:
    approval_id: str
    action_digest: str
    approver_id: str
    timestamp: str
    obligation_type: str = "explicit_approval"


@dataclass
class AuditEvent:
    event_id: str
    action_digest: str
    verdicts: List[PolicyVerdict]
    final_decision: VerdictDecision
    timestamp: str


@dataclass
class PolicyBundleVersion:
    bundle_name: str
    bundle_version: str
    doctrine_version: str


@dataclass
class HandoffContract:
    handoff_id: str
    from_actor: str
    to_actor: str
    context_passed: Dict[str, Any]


@dataclass
class TaskEnvelope:
    task_id: str
    actor: ActorIdentity
    scope: ArtifactScope
    metadata: Dict[str, Any]
