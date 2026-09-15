import json
import unittest
from pathlib import Path


class ScenarioMetadataTests(unittest.TestCase):
    def test_scenarios_have_manual_observables_and_no_machine_paths(self):
        path = Path(__file__).parents[1] / "data/test-scenarios.json"
        scenarios = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(scenarios), 3)
        for scenario in scenarios:
            self.assertTrue(scenario["id"])
            self.assertTrue(scenario["expected_observables"])
            self.assertTrue(scenario["manual_required"])
            self.assertNotIn("/Users/", json.dumps(scenario))


if __name__ == "__main__":
    unittest.main()
