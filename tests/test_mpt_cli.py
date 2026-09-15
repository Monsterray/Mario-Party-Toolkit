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

    def test_run_process_can_select_video_plugin(self):
        completed = type("Completed", (), {"stdout": "Core: Imagetype: .z64 (native)\nCore: Country: USA\n", "stderr": "", "returncode": 0})()
        with patch("tools.mpt_cli.subprocess.run", return_value=completed) as run:
            mpt_cli.run_process("mupen64plus", "game.z64", 1, gfx="mupen64plus-video-rice")
        self.assertIn("mupen64plus-video-rice", run.call_args.args[0])

    def test_run_process_defaults_to_working_glide_plugin_and_passes_settings(self):
        completed = type("Completed", (), {"stdout": "", "stderr": "", "returncode": 0})()
        with patch("tools.mpt_cli.subprocess.run", return_value=completed) as run:
            mpt_cli.run_process(
                "mupen64plus", "game.z64", 1,
                settings=["Audio-SDL[RESAMPLE]=src-linear", "Audio-SDL[AUDIO_SYNC]=False"],
            )
        command = run.call_args.args[0]
        self.assertIn("mupen64plus-video-glide64mk2", command)
        self.assertIn("Audio-SDL[RESAMPLE]=src-linear", command)
        self.assertIn("Audio-SDL[AUDIO_SYNC]=False", command)

    def test_main_reports_missing_rom_as_json_error(self):
        with patch("sys.stderr.write"):
            result = mpt_cli.main(["inspect-rom", "/missing.z64"])
        self.assertEqual(result, 1)

    def test_injector_environment_override_wins(self):
        with patch.dict(os.environ, {"MPT_GSINJECT": "/tmp/GSInject"}):
            self.assertEqual(mpt_cli.locate_injector(), Path("/tmp/GSInject"))

    def test_skip_mupen_reports_injection_only_success(self):
        completed = type("Completed", (), {"stdout": "saved", "stderr": "", "returncode": 0})()
        with tempfile.TemporaryDirectory() as directory:
            code = Path(directory) / "code.txt"
            code.write_text("MP3 - test\n81000000 0001\n", encoding="utf-8")
            with patch.dict(os.environ, {"MPT_GSINJECT": "/tmp/GSInject"}), patch(
                "tools.mpt_cli.locate_injector", return_value=Path("/tmp/GSInject")
            ), patch("tools.mpt_cli.inspect_n64") as inspect, patch(
                "tools.mpt_cli.inject_copy", return_value={"injected": True}
            ):
                inspect.return_value = type(
                    "Identity", (), {"path": Path("game.z64"), "size": 1, "md5": "x", "sha256": "y", "byte_order": "z64", "internal_name": "MarioParty3", "region": "E", "version": 0, "pp64_game": "mp3"}
                )()
                result = mpt_cli.main([
                    "test", "game.z64", "--game", "mp3", "--code", str(code),
                    "--output-dir", str(Path(directory) / "out"),
                    "--skip-mupen",
                ])
            self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
