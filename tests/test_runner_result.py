import unittest

from tools.runner_result import confirm_result, observation, status_for, validate_observation


class RunnerResultTests(unittest.TestCase):
    def test_facts_are_monotonic(self):
        facts = observation(loaded=True, booted=True)
        self.assertEqual(status_for({"schema_version": 1, "observation": facts}), "booted")

    def test_invalid_promotion_is_rejected(self):
        self.assertIn("visibly_changed requires booted", validate_observation({
            "loaded": True, "booted": False, "visibly_changed": True,
            "behavior_confirmed": False,
        }))

    def test_confirmation_keeps_evidence_separate(self):
        result = {"schema_version": 1, "observation": observation(loaded=True, booted=True)}
        result = confirm_result(result, ["visibly_changed", "behavior_confirmed"], "Observed target value in gameplay")
        self.assertEqual(result["status"], "behavior_confirmed")
        self.assertEqual(result["semantic_evidence"], "Observed target value in gameplay")


if __name__ == "__main__":
    unittest.main()
