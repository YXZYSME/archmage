import unittest

from archmage.runtime.domain import (
    ActionProposal,
    ActorIdentity,
    PolicyContext,
    ProposedEffect,
    VerdictDecision,
)
from archmage.runtime.evaluators import (
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


class TestEvaluators(unittest.TestCase):
    def setUp(self):
        self.actor = ActorIdentity(actor_id="test-agent", actor_type="agent")
        self.context = PolicyContext(workspace="/tmp/workspace", environment="local")

        self.base_action = ActionProposal(
            task_id="task-123",
            actor=self.actor,
            operation="write_file",
            tool="write_to_file",
            arguments={"TargetFile": "app.py"},
            target_paths=["app.py"],
            requested_side_effects=[],
            repository_revision="HEAD",
            environment="local",
        )

    def test_scope_enforcement_allow(self):
        evaluator = ScopeEnforcementEvaluator()
        verdict = evaluator.evaluate(self.base_action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW)

    def test_scope_enforcement_deny(self):
        evaluator = ScopeEnforcementEvaluator()
        action = self.base_action
        action.target_paths = ["../outside.py"]
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertIn("escapes", verdict.finding)

    def test_protected_policy_mutation_deny(self):
        evaluator = ProtectedPolicyMutationEvaluator()
        action = self.base_action
        action.target_paths = ["src/archmage/runtime/evaluators.py"]
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertEqual(verdict.policy_id, "POL-MUTATION-01")

    def test_generic_labels_repair(self):
        evaluator = GenericLabelsEvaluator()
        action = self.base_action
        action.target_paths = ["src/utils.py"]
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.REPAIR)
        self.assertEqual(verdict.policy_id, "POL-LABELING-01")
        self.assertIsNotNone(verdict.repair)

    def test_identity_declaration_deny(self):
        evaluator = IdentityDeclarationEvaluator()
        action = self.base_action
        action.actor = None
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertEqual(verdict.policy_id, "POL-IDENTITY-01")

    def test_lineage_evaluator_deny_untracked(self):
        evaluator = LineageEvaluator()
        action = self.base_action
        action.repository_revision = "untracked"
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertEqual(verdict.policy_id, "POL-LINEAGE-01")

    def test_lineage_evaluator_allow(self):
        evaluator = LineageEvaluator()
        action = self.base_action
        action.repository_revision = "a" * 40
        action.arguments = {"tracked_files": ["app.py"]}
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW)

    def test_stewardship_evaluator_deny_owner_mismatch(self):
        evaluator = StewardshipEvaluator()
        action = self.base_action
        action.arguments = {"owner": "other-agent"}
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertEqual(verdict.policy_id, "POL-STEWARDSHIP-01")

    def test_concord_evaluator_warn_obligations(self):
        evaluator = ConcordEvaluator()
        action = self.base_action
        action.arguments = {"note": "using deprecated_term in code"}
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW_WITH_OBLIGATIONS)
        self.assertEqual(verdict.policy_id, "POL-CONCORD-01")

    def test_transparency_evaluator_deny_no_audit(self):
        evaluator = TransparencyEvaluator()
        action = self.base_action
        action.requested_side_effects = [ProposedEffect("file_write", "app.py", {})]
        context = PolicyContext(
            workspace="/tmp/workspace",
            environment="local",
            audit_logger_configured=False,
        )
        verdict = evaluator.evaluate(action, context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertEqual(verdict.policy_id, "POL-TRANSPARENCY-01")

    def test_transparency_evaluator_uses_context_not_action_claim(self):
        evaluator = TransparencyEvaluator()
        action = self.base_action
        action.requested_side_effects = [ProposedEffect("file_write", "app.py", {})]
        action.arguments = {"audit_logger_configured": True}
        context = PolicyContext(
            workspace="/tmp/workspace",
            environment="local",
            audit_logger_configured=False,
        )

        verdict = evaluator.evaluate(action, context, "digest123")

        self.assertEqual(verdict.decision, VerdictDecision.DENY)

    def test_conservatism_evaluator_obligations_irreversible(self):
        evaluator = ConservatismEvaluator()
        action = self.base_action
        action.requested_side_effects = [ProposedEffect("file_deletion", "app.py", {})]
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW_WITH_OBLIGATIONS)
        self.assertEqual(verdict.policy_id, "POL-CONSERVATISM-01")

    def test_conservatism_evaluator_obligates_arbitrary_shell(self):
        evaluator = ConservatismEvaluator()
        action = self.base_action
        action.requested_side_effects = [ProposedEffect("shell_command", "run_command", {})]
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW_WITH_OBLIGATIONS)

    def test_scope_evaluator_denies_missing_path_declaration(self):
        evaluator = ScopeEnforcementEvaluator()
        action = self.base_action
        action.target_paths = []
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertIn("omitted", verdict.finding)

    def test_verification_evaluator_repair_missing_evidence(self):
        evaluator = VerificationEvaluator()
        action = self.base_action
        action.arguments = {"claim_type": "performance"}
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.REPAIR)
        self.assertEqual(verdict.policy_id, "POL-VERIFICATION-01")

    def test_sovereignty_evaluator_deny_actor_mismatch(self):
        evaluator = SovereigntyEvaluator()
        action = self.base_action
        action.arguments = {"allowed_actor_type": "human"}
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertEqual(verdict.policy_id, "POL-SOVEREIGNTY-01")


if __name__ == "__main__":
    unittest.main()
