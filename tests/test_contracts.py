import unittest
from unittest.mock import patch

from archmage.evaluators import ContractDepthEvaluator, ContractFirstEvaluator
from archmage.runtime.domain import ActionProposal, ActorIdentity, PolicyContext, VerdictDecision


class TestArchmageContracts(unittest.TestCase):
    def setUp(self):
        self.actor = ActorIdentity(actor_id="test-agent", actor_type="agent")
        self.context = PolicyContext(workspace="/tmp", environment="local")
        self.base_action = ActionProposal(
            task_id="task-contract",
            actor=self.actor,
            operation="write_file",
            tool="write_to_file",
            arguments={},
            target_paths=["module.py"],
            requested_side_effects=[],
            repository_revision="HEAD",
            environment="local",
        )

    def test_contract_depth_allow(self):
        evaluator = ContractDepthEvaluator(max_public_methods=5, max_params_per_method=3)
        action = self.base_action
        action.arguments = {
            "CodeContent": (
                "def foo(a: int, b: int) -> int:\n    '''Docstring.'''\n    return a + b\n"
            )
        }
        verdict = evaluator.evaluate(action, self.context, "digest1")
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW)

    def test_contract_depth_repair(self):
        evaluator = ContractDepthEvaluator(max_public_methods=2, max_params_per_method=2)
        code = "def foo(a, b, c, d, e):\n    pass\ndef bar():\n    pass\ndef baz():\n    pass\n"
        action = self.base_action
        action.arguments = {"CodeContent": code}
        verdict = evaluator.evaluate(action, self.context, "digest2")
        self.assertEqual(verdict.decision, VerdictDecision.REPAIR)
        self.assertEqual(verdict.policy_id, "POL-CONTRACT-DEPTH-01")

    def test_contract_first_allow(self):
        evaluator = ContractFirstEvaluator()
        code = "def foo(a: int) -> int:\n    '''A docstring.'''\n    return a\n"
        action = self.base_action
        action.arguments = {"CodeContent": code}
        verdict = evaluator.evaluate(action, self.context, "digest3")
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW)

    def test_contract_first_obligations(self):
        evaluator = ContractFirstEvaluator()
        code = "def foo(a):\n    return a\n"
        action = self.base_action
        action.arguments = {"CodeContent": code}
        verdict = evaluator.evaluate(action, self.context, "digest4")
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW_WITH_OBLIGATIONS)
        self.assertEqual(verdict.policy_id, "POL-CONTRACT-FIRST-01")

    def test_contract_depth_does_not_read_target_paths(self):
        evaluator = ContractDepthEvaluator()
        action = self.base_action
        action.arguments = {}
        action.target_paths = ["/outside/secrets.py"]

        with patch("builtins.open") as open_mock:
            verdict = evaluator.evaluate(action, self.context, "digest5")

        open_mock.assert_not_called()
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW)

    def test_contract_first_does_not_read_target_paths(self):
        evaluator = ContractFirstEvaluator()
        action = self.base_action
        action.arguments = {}
        action.target_paths = ["../../outside/secrets.py"]

        with patch("builtins.open") as open_mock:
            verdict = evaluator.evaluate(action, self.context, "digest6")

        open_mock.assert_not_called()
        self.assertEqual(verdict.decision, VerdictDecision.ALLOW)


if __name__ == "__main__":
    unittest.main()
