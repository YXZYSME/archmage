import unittest

from archmage.runtime.domain import (
    ActionProposal,
    ActorIdentity,
    PolicyContext,
    PolicyVerdict,
    VerdictDecision,
)
from archmage.runtime.evaluators import BaseEvaluator
from archmage.runtime.pdp import PolicyDecisionPoint


class MockDenyEvaluator(BaseEvaluator):
    def evaluate(self, action, context, digest):
        return PolicyVerdict(
            decision=VerdictDecision.DENY,
            policy_id="MOCK-01",
            policy_version="1.0",
            law_ids=[],
            severity="high",
            confidence=1.0,
            actor_id="a",
            task_id="t",
            action_digest=digest,
            artifacts=[],
            finding="Mock Deny",
        )


class MockAllowEvaluator(BaseEvaluator):
    def evaluate(self, action, context, digest):
        return PolicyVerdict(
            decision=VerdictDecision.ALLOW,
            policy_id="MOCK-02",
            policy_version="1.0",
            law_ids=[],
            severity="none",
            confidence=1.0,
            actor_id="a",
            task_id="t",
            action_digest=digest,
            artifacts=[],
            finding="Mock Allow",
        )


class CrashingEvaluator(BaseEvaluator):
    def evaluate(self, action, context, digest):
        raise RuntimeError("simulated evaluator failure")


class TestIntegration(unittest.TestCase):
    def test_pdp_aggregation_deny_precedence(self):
        pdp = PolicyDecisionPoint([MockAllowEvaluator(), MockDenyEvaluator()])

        actor = ActorIdentity(actor_id="test-agent", actor_type="agent")
        action = ActionProposal(
            task_id="t",
            actor=actor,
            operation="op",
            tool="tool",
            arguments={},
            target_paths=[],
            requested_side_effects=[],
            repository_revision="HEAD",
            environment="local",
        )
        context = PolicyContext(workspace="/tmp", environment="local")

        verdict = pdp.evaluate(action, context)
        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertEqual(verdict.policy_id, "MOCK-01")

    def test_pdp_fails_closed_when_evaluator_crashes(self):
        actor = ActorIdentity(actor_id="test-agent", actor_type="agent")
        action = ActionProposal(
            task_id="t",
            actor=actor,
            operation="op",
            tool="tool",
            arguments={},
            target_paths=[],
            requested_side_effects=[],
            repository_revision="a" * 40,
            environment="local",
        )
        context = PolicyContext(workspace="/tmp", environment="local")

        verdict = PolicyDecisionPoint([CrashingEvaluator()]).evaluate(action, context)

        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertEqual(verdict.policy_id, "SYS-FAIL-CLOSED")
        self.assertIn("failed closed", verdict.finding)

    def test_pdp_fails_closed_when_action_cannot_be_canonicalized(self):
        action = ActionProposal(
            task_id="t",
            actor=ActorIdentity(actor_id="test-agent", actor_type="agent"),
            operation="op",
            tool="tool",
            arguments={"payload": b"not-json"},
            target_paths=[],
            requested_side_effects=[],
            repository_revision="a" * 40,
            environment="local",
        )
        context = PolicyContext(workspace="/tmp", environment="local")

        verdict = PolicyDecisionPoint([MockAllowEvaluator()]).evaluate(action, context)

        self.assertEqual(verdict.decision, VerdictDecision.DENY)
        self.assertEqual(verdict.policy_id, "SYS-FAIL-CLOSED")
        self.assertIn("canonicalized", verdict.finding)


if __name__ == "__main__":
    unittest.main()
