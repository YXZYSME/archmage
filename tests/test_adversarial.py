import os
import tempfile
import unittest

from archmage.runtime.domain import ActionProposal, ActorIdentity, PolicyContext, VerdictDecision
from archmage.runtime.evaluators import ScopeEnforcementEvaluator


class TestAdversarial(unittest.TestCase):
    def setUp(self):
        self.actor = ActorIdentity(actor_id="adv-agent", actor_type="agent")
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

    def test_adversarial_path_traversal(self):
        evaluator = ScopeEnforcementEvaluator()
        action = self.base_action
        action.target_paths = ["../../../etc/passwd"]
        verdict = evaluator.evaluate(action, self.context, "digest123")
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertIn("escapes", verdict.finding)

    def test_prefix_collision_does_not_escape_workspace(self):
        evaluator = ScopeEnforcementEvaluator()
        action = self.base_action
        action.target_paths = ["/tmp/workspace-escape/payload.py"]

        verdict = evaluator.evaluate(action, self.context, "digest123")

        self.assertEqual(verdict.decision, VerdictDecision.DENY)

    def test_symlink_escape_is_denied(self):
        evaluator = ScopeEnforcementEvaluator()
        with tempfile.TemporaryDirectory() as root:
            workspace = os.path.join(root, "workspace")
            outside = os.path.join(root, "outside")
            os.makedirs(workspace)
            os.makedirs(outside)
            os.symlink(outside, os.path.join(workspace, "linked"))
            action = self.base_action
            action.target_paths = ["linked/payload.py"]
            context = PolicyContext(workspace=workspace, environment="local")

            verdict = evaluator.evaluate(action, context, "digest123")

        self.assertEqual(verdict.decision, VerdictDecision.DENY)


if __name__ == "__main__":
    unittest.main()
