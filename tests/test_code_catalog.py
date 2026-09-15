import unittest

from tools.code_catalog import build_catalog


class CodeCatalogTests(unittest.TestCase):
    def test_all_n64_and_disc_generators_are_discoverable(self):
        catalog = build_catalog()
        games = {entry["game"] for entry in catalog}
        self.assertEqual(games, {f"mp{number}" for number in range(1, 10)})
        self.assertGreaterEqual(len(catalog), 70)

    def test_runner_metadata_matches_platform(self):
        for entry in build_catalog():
            if entry["game"] in {"mp1", "mp2", "mp3"}:
                self.assertEqual(entry["platform"], "n64")
                self.assertEqual(entry["code_family"], "gameshark")
                self.assertEqual(entry["test_runner"], "mupen-native-cheat")
            else:
                self.assertIn(entry["platform"], {"gamecube", "wii"})
                self.assertEqual(entry["code_family"], "gecko")
                self.assertEqual(entry["test_runner"], "dolphin-native-gecko")

    def test_entries_have_stable_identity_fields(self):
        for entry in build_catalog():
            self.assertTrue(entry["module"].startswith("codes."))
            self.assertTrue(entry["generator"])
            self.assertIsInstance(entry["parameters"], list)


if __name__ == "__main__":
    unittest.main()
