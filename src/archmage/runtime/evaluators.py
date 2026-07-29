import os
import re
from pathlib import PurePosixPath
from typing import List

from ._path_policy import resolve_workspace_target
from .domain import (
    ActionProposal,
    Obligation,
    PolicyContext,
    PolicyVerdict,
    RepairInstruction,
    VerdictDecision,
)


class BaseEvaluator:
    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        raise NotImplementedError

    def _allow(
        self, action: ActionProposal, digest: str, pid: str, laws: List[int]
    ) -> PolicyVerdict:
        return PolicyVerdict(
            decision=VerdictDecision.ALLOW,
            policy_id=pid,
            policy_version="1.0.0",
            law_ids=laws,
            severity="none",
            confidence=1.0,
            actor_id=action.actor.actor_id if action.actor else "unknown",
            task_id=action.task_id if action.task_id else "unknown",
            action_digest=digest,
            artifacts=action.target_paths,
            finding="Compliant",
        )


class ScopeEnforcementEvaluator(BaseEvaluator):
    _PATH_SENSITIVE_OPERATIONS = {
        "delete_file",
        "multi_replace_file_content",
        "read_file",
        "view_file",
        "write_file",
        "write_to_file",
    }
    _PATH_SENSITIVE_EFFECTS = {
        "file_deletion",
        "file_read",
        "file_write",
    }

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        # Law 1: Territory
        requires_path = (
            action.operation in self._PATH_SENSITIVE_OPERATIONS
            or action.tool in self._PATH_SENSITIVE_OPERATIONS
            or any(
                effect.effect_type in self._PATH_SENSITIVE_EFFECTS
                for effect in action.requested_side_effects
            )
        )
        if requires_path and not action.target_paths:
            return PolicyVerdict(
                decision=VerdictDecision.DENY,
                policy_id="POL-TERRITORY-01",
                policy_version="1.0.0",
                law_ids=[1],
                severity="critical",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id,
                action_digest=action_digest,
                artifacts=[],
                finding="Path-sensitive action omitted its declared target paths.",
            )

        for path in action.target_paths:
            try:
                resolved = resolve_workspace_target(context.workspace, path)
            except (OSError, RuntimeError, ValueError):
                return PolicyVerdict(
                    decision=VerdictDecision.DENY,
                    policy_id="POL-TERRITORY-01",
                    policy_version="1.0.0",
                    law_ids=[1],
                    severity="critical",
                    confidence=1.0,
                    actor_id=action.actor.actor_id if action.actor else "unknown",
                    task_id=action.task_id,
                    action_digest=action_digest,
                    artifacts=[path],
                    finding="Target path could not be resolved against the declared workspace.",
                )
            if not resolved.is_within_workspace:
                return PolicyVerdict(
                    decision=VerdictDecision.DENY,
                    policy_id="POL-TERRITORY-01",
                    policy_version="1.0.0",
                    law_ids=[1],
                    severity="critical",
                    confidence=1.0,
                    actor_id=action.actor.actor_id if action.actor else "unknown",
                    task_id=action.task_id,
                    action_digest=action_digest,
                    artifacts=[path],
                    finding=f"Target escapes the declared workspace: {path}",
                    repair=RepairInstruction(operation="redirect_to_tmp", required_fields=[]),
                )
        return self._allow(action, action_digest, "POL-TERRITORY-01", [1])


class ProtectedPolicyMutationEvaluator(BaseEvaluator):
    _PROTECTED_PATHS = (
        PurePosixPath("manifest.yaml"),
        PurePosixPath("SKILL.md"),
        PurePosixPath("src/archmage/doctrine"),
        PurePosixPath("src/archmage/evaluators"),
        PurePosixPath("src/archmage/runtime"),
    )

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        for path in action.target_paths:
            try:
                resolved = resolve_workspace_target(context.workspace, path)
            except (OSError, RuntimeError, ValueError):
                continue
            if resolved.relative_path is None:
                continue

            relative_path = PurePosixPath(resolved.relative_path.as_posix())
            for protected in self._PROTECTED_PATHS:
                if relative_path == protected or protected in relative_path.parents:
                    return PolicyVerdict(
                        decision=VerdictDecision.DENY,
                        policy_id="POL-MUTATION-01",
                        policy_version="1.0.0",
                        law_ids=[3, 5],
                        severity="high",
                        confidence=1.0,
                        actor_id=action.actor.actor_id if action.actor else "unknown",
                        task_id=action.task_id,
                        action_digest=action_digest,
                        artifacts=[path],
                        finding=f"Attempt to modify protected policy path: {relative_path}",
                    )
        return self._allow(action, action_digest, "POL-MUTATION-01", [3, 5])


class GenericLabelsEvaluator(BaseEvaluator):
    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        # Law 2, 7: Canonical Glossary
        banned_labels = {"utils", "helpers", "misc", "common", "stuff", "temp"}

        for path in action.target_paths:
            basename = os.path.basename(path).split(".")[0].lower()
            if basename in banned_labels:
                return PolicyVerdict(
                    decision=VerdictDecision.REPAIR,
                    policy_id="POL-LABELING-01",
                    policy_version="1.0.0",
                    law_ids=[2, 7],
                    severity="medium",
                    confidence=1.0,
                    actor_id=action.actor.actor_id,
                    task_id=action.task_id,
                    action_digest=action_digest,
                    artifacts=[path],
                    finding=f"Generic artifact name detected: {basename}",
                    repair=RepairInstruction(
                        operation="rename_artifact", required_fields=["new_name"]
                    ),
                )
        return self._allow(action, action_digest, "POL-LABELING-01", [2, 7])


class IdentityDeclarationEvaluator(BaseEvaluator):
    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        undeclared = {"", "none", "unknown"}
        actor_id = action.actor.actor_id.strip().lower() if action.actor else ""
        task_id = action.task_id.strip().lower() if action.task_id else ""
        actor_type = action.actor.actor_type.strip().lower() if action.actor else ""
        if actor_id in undeclared or task_id in undeclared or actor_type not in {"agent", "human"}:
            return PolicyVerdict(
                decision=VerdictDecision.DENY,
                policy_id="POL-IDENTITY-01",
                policy_version="1.0.0",
                law_ids=[2, 6],
                severity="high",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id or "unknown",
                action_digest=action_digest,
                artifacts=[],
                finding="Missing actor identity, task identity, or execution scope.",
            )
        return self._allow(action, action_digest, "POL-IDENTITY-01", [2, 6])


class LineageEvaluator(BaseEvaluator):
    """Require target lineage to name an immutable repository revision."""

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        revision = action.repository_revision.strip() if action.repository_revision else ""
        if not re.fullmatch(r"[0-9a-fA-F]{7,64}", revision):
            return PolicyVerdict(
                decision=VerdictDecision.DENY,
                policy_id="POL-LINEAGE-01",
                policy_version="1.0.0",
                law_ids=[4],
                severity="high",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id,
                action_digest=action_digest,
                artifacts=action.target_paths,
                finding=(
                    "Missing or mutable repository_revision; artifact lineage cannot be validated."
                ),
            )

        tracked_files = action.arguments.get("tracked_files")
        if tracked_files is not None:
            for path in action.target_paths:
                if path not in tracked_files and os.path.basename(path) not in tracked_files:
                    return PolicyVerdict(
                        decision=VerdictDecision.DENY,
                        policy_id="POL-LINEAGE-01",
                        policy_version="1.0.0",
                        law_ids=[4],
                        severity="high",
                        confidence=1.0,
                        actor_id=action.actor.actor_id if action.actor else "unknown",
                        task_id=action.task_id,
                        action_digest=action_digest,
                        artifacts=[path],
                        finding=(
                            f"Target path '{path}' is not within known tracked files "
                            f"for revision {action.repository_revision}."
                        ),
                    )
        return self._allow(action, action_digest, "POL-LINEAGE-01", [4])


class StewardshipEvaluator(BaseEvaluator):
    """Prevent writes to files owned by a different declared actor scope."""

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        file_owners = action.arguments.get("file_owners") or {}
        target_owner = action.arguments.get("owner") or action.arguments.get("target_owner")

        for path in action.target_paths:
            owner = file_owners.get(path) or target_owner
            if owner and owner != action.actor.actor_id:
                return PolicyVerdict(
                    decision=VerdictDecision.DENY,
                    policy_id="POL-STEWARDSHIP-01",
                    policy_version="1.0.0",
                    law_ids=[5],
                    severity="high",
                    confidence=1.0,
                    actor_id=action.actor.actor_id if action.actor else "unknown",
                    task_id=action.task_id,
                    action_digest=action_digest,
                    artifacts=[path],
                    finding=(
                        f"Write denied for artifact '{path}' owned by actor "
                        f"'{owner}' (caller is '{action.actor.actor_id}')."
                    ),
                )
        return self._allow(action, action_digest, "POL-STEWARDSHIP-01", [5])


class ConcordEvaluator(BaseEvaluator):
    """Add an obligation when declared terms drift from the glossary."""

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        unapproved_terms = {"deprecated_term", "legacy_helper", "temp_utils", "unapproved_synonym"}
        flagged = []

        for path in action.target_paths:
            for term in unapproved_terms:
                if term in path:
                    flagged.append(term)

        for _key, val in action.arguments.items():
            if isinstance(val, str):
                for term in unapproved_terms:
                    if term in val:
                        flagged.append(term)

        if flagged:
            return PolicyVerdict(
                decision=VerdictDecision.ALLOW_WITH_OBLIGATIONS,
                policy_id="POL-CONCORD-01",
                policy_version="1.0.0",
                law_ids=[2, 7],
                severity="low",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id,
                action_digest=action_digest,
                artifacts=action.target_paths,
                finding=(
                    f"Non-concordant terms detected: {set(flagged)}. "
                    "Review against canonical glossary."
                ),
                obligations=[
                    Obligation(type="glossary_concordance_review", required_before="commit")
                ],
            )
        return self._allow(action, action_digest, "POL-CONCORD-01", [2, 7])


class TransparencyEvaluator(BaseEvaluator):
    """POL-TRANSPARENCY-01 (Law 8): Require audit logger configured when action has side effects."""

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        has_side_effects = bool(action.requested_side_effects) or action.operation in (
            "write_file",
            "run_command",
            "delete_file",
        )
        if has_side_effects and not context.audit_logger_configured:
            return PolicyVerdict(
                decision=VerdictDecision.DENY,
                policy_id="POL-TRANSPARENCY-01",
                policy_version="1.0.0",
                law_ids=[8],
                severity="critical",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id,
                action_digest=action_digest,
                artifacts=action.target_paths,
                finding="Side effect requested without active audit logger configuration.",
            )
        return self._allow(action, action_digest, "POL-TRANSPARENCY-01", [8])


class ConservatismEvaluator(BaseEvaluator):
    """Require approval for declared irreversible side effects."""

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        irreversible_types = {
            "file_deletion",
            "schema_migration",
            "drop_table",
            "destructive_shell",
            "force_push",
            "shell_command",
        }

        flagged = []
        for effect in action.requested_side_effects:
            if effect.effect_type in irreversible_types:
                flagged.append(effect.effect_type)
        if action.operation in irreversible_types or action.arguments.get("is_irreversible"):
            flagged.append(action.operation)

        if flagged:
            return PolicyVerdict(
                decision=VerdictDecision.ALLOW_WITH_OBLIGATIONS,
                policy_id="POL-CONSERVATISM-01",
                policy_version="1.0.0",
                law_ids=[4],
                severity="high",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id,
                action_digest=action_digest,
                artifacts=action.target_paths,
                finding=(
                    "Irreversible side effect detected "
                    f"({', '.join(set(flagged))}). Approval required."
                ),
                obligations=[Obligation(type="explicit_approval", required_before="execution")],
            )
        return self._allow(action, action_digest, "POL-CONSERVATISM-01", [4])


class VerificationEvaluator(BaseEvaluator):
    """Require evidence for declared performance or reliability claims."""

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        claim_type = action.arguments.get("claim_type")
        has_claim = (
            claim_type in ("performance", "reliability", "benchmark", "scaling")
            or action.arguments.get("has_performance_claim")
            or action.arguments.get("has_reliability_claim")
        )

        evidence_present = bool(
            action.arguments.get("evidence_record") or action.arguments.get("evidence_id")
        )

        if has_claim and not evidence_present:
            return PolicyVerdict(
                decision=VerdictDecision.REPAIR,
                policy_id="POL-VERIFICATION-01",
                policy_version="1.0.0",
                law_ids=[8],
                severity="high",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id,
                action_digest=action_digest,
                artifacts=action.target_paths,
                finding=(
                    f"Performance/reliability claim ('{claim_type}') lacks "
                    "an attached EvidenceRecord."
                ),
                repair=RepairInstruction(
                    operation="attach_evidence_record",
                    required_fields=["evidence_id", "verification_method"],
                ),
            )
        return self._allow(action, action_digest, "POL-VERIFICATION-01", [8])


class SovereigntyEvaluator(BaseEvaluator):
    """POL-SOVEREIGNTY-01 (Laws 5, 6): Verify actor_type matches declared context scope."""

    def evaluate(
        self, action: ActionProposal, context: PolicyContext, action_digest: str
    ) -> PolicyVerdict:
        allowed_actor_type = action.arguments.get("allowed_actor_type") or action.arguments.get(
            "declared_scope_actor_type"
        )
        if allowed_actor_type and action.actor and action.actor.actor_type != allowed_actor_type:
            return PolicyVerdict(
                decision=VerdictDecision.DENY,
                policy_id="POL-SOVEREIGNTY-01",
                policy_version="1.0.0",
                law_ids=[5, 6],
                severity="high",
                confidence=1.0,
                actor_id=action.actor.actor_id if action.actor else "unknown",
                task_id=action.task_id,
                action_digest=action_digest,
                artifacts=action.target_paths,
                finding=(
                    f"Actor type '{action.actor.actor_type}' mismatches declared "
                    f"context scope actor type '{allowed_actor_type}'."
                ),
            )
        return self._allow(action, action_digest, "POL-SOVEREIGNTY-01", [5, 6])
