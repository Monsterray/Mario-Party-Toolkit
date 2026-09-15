import tempfile
import unittest
from pathlib import Path

from utils.code_validation import validate_code_target
from utils.rom_identity import inspect_n64


class RomIdentityTests(unittest.TestCase):
    def test_inspects_big_endian_header(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.z64"
            data = bytearray(0x40)
            data[:4] = b"\x80\x37\x12\x40"
            data[0x20:0x2A] = b"MARIO PARTY"
            data[0x3E] = ord("E")
            path.write_bytes(data)
            identity = inspect_n64(path)
            self.assertEqual(identity.byte_order, "z64")
            self.assertEqual(identity.region, "E")

    def test_rejects_mixed_game_labels(self):
        valid, message = validate_code_target("MP1: 12345678 00000001\nMP2: 12345678 00000001", "mp1")
        self.assertFalse(valid)
        self.assertIn("mp2", message)


if __name__ == "__main__":
    unittest.main()
