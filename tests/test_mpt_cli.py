import json
import tempfile
import unittest
import os
from pathlib import Path
from unittest.mock import patch

from tools import mpt_cli


class MptCliTests(unittest.TestCase):
    def test_validate_code_rejects_wrong_target_and_bad_lines(self):
        valid, message, malformed = mpt_cli.validate_code_text("MP2 - test\n80000000 0001\nnot code\n", "mp1")
        self.assertFalse(valid)
        self.assertIn("mp2", message)
        self.assertEqual(malformed, [3])

    def test_run_process_reports_header_without_claiming_gameplay(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "mupen.log"
            completed = type("Completed", (), {"stdout": "Core: Imagetype: .z64 (native)\nCore: Country: USA\n", "stderr": "", "returncode": 0})()
            with patch("tools.mpt_cli.subprocess.run", return_value=completed):
                result = mpt_cli.run_process("mupen64plus", "game.z64", 1, log)
            self.assertTrue(result["header_parsed"])
            self.assertTrue(log.is_file())

    def test_main_reports_missing_rom_as_json_error(self):
        with patch("sys.stderr.write"):
            result = mpt_cli.main(["inspect-rom", "/missing.z64"])
        self.assertEqual(result, 1)

    def test_injector_environment_override_wins(self):
        with patch.dict(os.environ, {"MPT_GSINJECT": "/tmp/GSInject"}):
            self.assertEqual(mpt_cli.locate_injector(), Path("/tmp/GSInject"))


if __name__ == "__main__":
    unittest.main()
