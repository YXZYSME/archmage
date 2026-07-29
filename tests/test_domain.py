import unittest

from archmage.runtime.domain import ActionDigest, ActionProposal, ActorIdentity


class TestDomain(unittest.TestCase):
    def test_action_digest_stability(self):
        actor = ActorIdentity(actor_id="test-agent", actor_type="agent")
        action = ActionProposal(
            task_id="task-123",
            actor=actor,
            operation="write_file",
            tool="write_to_file",
            arguments={"TargetFile": "app.py"},
            target_paths=["app.py"],
            requested_side_effects=[],
            repository_revision="HEAD",
            environment="local",
        )

        digest1 = ActionDigest.compute(action)
        digest2 = ActionDigest.compute(action)
        self.assertEqual(digest1.digest_hash, digest2.digest_hash)

        # Mutate action
        action.target_paths = ["other.py"]
        digest3 = ActionDigest.compute(action)
        self.assertNotEqual(digest1.digest_hash, digest3.digest_hash)

    def test_action_digest_rejects_ambiguous_non_json_values(self):
        action = ActionProposal(
            task_id="task-123",
            actor=ActorIdentity(actor_id="test-agent", actor_type="agent"),
            operation="write_file",
            tool="write_to_file",
            arguments={"TargetFile": "artifact.bin", "content": b"secret"},
            target_paths=["artifact.bin"],
            requested_side_effects=[],
            repository_revision="a" * 40,
            environment="local",
        )

        with self.assertRaisesRegex(ValueError, "unsupported JSON value type"):
            ActionDigest.compute(action)

    def test_action_digest_is_stable_across_mapping_key_order(self):
        actor = ActorIdentity(actor_id="test-agent", actor_type="agent")
        first = ActionProposal(
            task_id="task-123",
            actor=actor,
            operation="write_file",
            tool="write_to_file",
            arguments={"TargetFile": "app.py", "content": {"a": 1, "b": 2}},
            target_paths=["app.py"],
            requested_side_effects=[],
            repository_revision="a" * 40,
            environment="local",
        )
        second = ActionProposal(
            task_id="task-123",
            actor=actor,
            operation="write_file",
            tool="write_to_file",
            arguments={"content": {"b": 2, "a": 1}, "TargetFile": "app.py"},
            target_paths=["app.py"],
            requested_side_effects=[],
            repository_revision="a" * 40,
            environment="local",
        )

        self.assertEqual(
            ActionDigest.compute(first).digest_hash,
            ActionDigest.compute(second).digest_hash,
        )


if __name__ == "__main__":
    unittest.main()
