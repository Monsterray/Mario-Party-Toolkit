import json
import unittest
from pathlib import Path


class WebCodeDatabaseTests(unittest.TestCase):
    def test_normalized_web_database_is_sourced_and_versioned(self):
        root = Path(__file__).parents[1]
        data = json.loads((root / "data/normalized-web-codes.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["errors"], [])
        self.assertGreaterEqual(len(data["records"]), 30)
        for record in data["records"]:
            self.assertTrue(record["description"])
            self.assertTrue(record["source_url"].startswith("https://"))
            self.assertTrue(record["revision"])
            self.assertTrue(record["code_lines"])


if __name__ == "__main__":
    unittest.main()
