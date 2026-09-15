import unittest

from tools.research_loop import make_record


class ResearchLoopTests(unittest.TestCase):
    def test_record_has_stable_evidence_and_explicit_unknowns(self):
        record = make_record(
            "  Gecko controls ", "https://example.test/source", " Source ",
            " Quote or exact observation ", " concise summary ", "devstral-24b-int8",
            ["Needs manual emulator confirmation", ""],
        )
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(record["evidence_id"], make_record(
            "Gecko controls", "https://example.test/source", "Source",
            "Quote or exact observation", "concise summary", "devstral-24b-int8",
            ["Needs manual emulator confirmation"],
        )["evidence_id"])
        self.assertEqual(record["unknowns"], ["Needs manual emulator confirmation"])


if __name__ == "__main__":
    unittest.main()
