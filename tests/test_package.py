import unittest


class TestPackageImports(unittest.TestCase):
    def test_package_exports(self):
        import archmage

        self.assertEqual(archmage.__version__, "2.0.0")

        from archmage.runtime import (
            ActionProposal,
            PolicyDecisionPoint,
            PolicyEnforcementPoint,
            PolicyViolationError,
        )

        self.assertIsNotNone(PolicyEnforcementPoint)
        self.assertIsNotNone(PolicyDecisionPoint)
        self.assertIsNotNone(ActionProposal)
        self.assertIsNotNone(PolicyViolationError)

        from archmage.runtime.pep import PolicyEnforcementPoint as PEP

        self.assertEqual(PEP, PolicyEnforcementPoint)

        from archmage.adapters import AntigravityAdapter, GenericAdapter

        self.assertIsNotNone(GenericAdapter)
        self.assertIsNotNone(AntigravityAdapter)

        from archmage.evaluators import ContractDepthEvaluator, ContractFirstEvaluator

        self.assertIsNotNone(ContractDepthEvaluator)
        self.assertIsNotNone(ContractFirstEvaluator)

        from archmage import ApprovalRecord, create_default_policy_decision_point

        self.assertIsNotNone(ApprovalRecord)
        self.assertEqual(len(create_default_policy_decision_point().evaluators), 11)


if __name__ == "__main__":
    unittest.main()
