import unittest

from tools.normalize_codes import normalize_records


class NormalizeCodeTests(unittest.TestCase):
    def candidate(self, **changes):
        value = {
            "game": "MP3", "region": "ntsc-u", "revision": "1.0",
            "code_family": "GameShark", "name": "  Blue   space  ",
            "codes": "MP3 - label\n810fe284    3408\n# note",
            "source_url": "https://example.test/code", "source_name": " Example ",
            "evidence": "source line 10", "confidence": 0.8,
        }
        value.update(changes)
        return value

    def test_normalizes_code_and_metadata(self):
        result = normalize_records([self.candidate()])
        record = result["records"][0]
        self.assertEqual(record["game"], "mp3")
        self.assertEqual(record["region"], "NTSC-U")
        self.assertEqual(record["name"], "Blue space")
        self.assertEqual(record["code_lines"], ["810FE284 3408"])
        self.assertEqual(record["ignored_lines"], ["MP3 - label"])
        self.assertFalse(result["errors"])

    def test_deduplicates_same_code_with_provenance(self):
        result = normalize_records([self.candidate(), self.candidate(source_name="Other")])
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["duplicates"][0]["duplicate_of"], result["records"][0]["id"])

    def test_rejects_missing_evidence_and_bad_url(self):
        result = normalize_records([self.candidate(evidence=""), self.candidate(source_url="file:///tmp/x")])
        self.assertEqual(len(result["errors"]), 2)


if __name__ == "__main__":
    unittest.main()
