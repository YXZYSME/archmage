import unittest

from archmage.adapters.antigravity import AntigravityAdapter
from archmage.runtime.evaluators import ScopeEnforcementEvaluator
from archmage.runtime.pdp import PolicyDecisionPoint, PolicyEnforcementPoint


class TestAntigravityAdapter(unittest.TestCase):
    def setUp(self):
        # Set up a real PEP with ScopeEnforcementEvaluator to test out-of-bounds interception
        pdp = PolicyDecisionPoint([ScopeEnforcementEvaluator()])
        pep = PolicyEnforcementPoint(pdp)
        self.adapter = AntigravityAdapter(pep)
        self.context_meta = {
            "task_id": "test-task",
            "actor_id": "antigravity-agent",
            "workspace": "/tmp/workspace",
            "git_sha": "a" * 40,
            "environment": "local",
        }

    def test_parse_write_to_file_in_bounds(self):
        # A valid write_to_file within the workspace
        args = {"TargetFile": "/tmp/workspace/src/main.py", "CodeContent": "print('hello')"}
        result = self.adapter.intercept_tool_call("write_to_file", args, self.context_meta)
        self.assertTrue(result)

    def test_parse_write_to_file_out_of_bounds(self):
        # An out-of-bounds write_to_file
        args = {"TargetFile": "/etc/passwd", "CodeContent": "hacked"}
        with self.assertRaises(PermissionError) as context:
            self.adapter.intercept_tool_call("write_to_file", args, self.context_meta)

        self.assertIn("Action write_to_file was denied", str(context.exception))
        self.assertIn("DENY", str(context.exception))

    def test_parse_run_command_in_bounds(self):
        args = {"CommandLine": "ls -la", "Cwd": "/tmp/workspace"}
        result = self.adapter.intercept_tool_call("run_command", args, self.context_meta)
        self.assertTrue(result)

    def test_parse_multi_replace_file_content(self):
        args = {"TargetFile": "/tmp/workspace/src/utils.py"}
        result = self.adapter.intercept_tool_call(
            "multi_replace_file_content", args, self.context_meta
        )
        self.assertTrue(result)

    def test_missing_context_is_rejected_before_evaluation(self):
        args = {"TargetFile": "/tmp/workspace/src/main.py"}
        context_meta = dict(self.context_meta)
        context_meta.pop("actor_id")

        with self.assertRaisesRegex(ValueError, "actor_id"):
            self.adapter.intercept_tool_call("write_to_file", args, context_meta)

    def test_oversized_payload_is_rejected_before_evaluation(self):
        args = {
            "TargetFile": "/tmp/workspace/src/main.py",
            "CodeContent": "x" * 1_048_577,
        }

        with self.assertRaisesRegex(ValueError, "1 MiB"):
            self.adapter.intercept_tool_call(
                "write_to_file",
                args,
                self.context_meta,
            )

    def test_unregistered_tool_is_rejected_before_evaluation(self):
        with self.assertRaisesRegex(ValueError, "unregistered tool"):
            self.adapter.intercept_tool_call(
                "delete_everything",
                {"TargetFile": "/tmp/workspace/src/main.py"},
                self.context_meta,
            )

    def test_registered_tool_requires_its_path_field(self):
        with self.assertRaisesRegex(ValueError, "TargetFile"):
            self.adapter.intercept_tool_call(
                "write_to_file",
                {"CodeContent": "value = 1"},
                self.context_meta,
            )


if __name__ == "__main__":
    unittest.main()
