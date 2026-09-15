import inspect
import re
import unittest
from importlib import import_module

from utils.code_validation import code_targets


CODE_LINE = re.compile(r"[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{4}$")
SHORT_HEX = {
    "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "min", "itemHex1", "itemHex2", "hexUno", "hexDos",
}


class CodeGenerationTests(unittest.TestCase):
    def test_mp1_to_mp3_functions_emit_matching_codes(self):
        for module_name in ("codes.marioParty1", "codes.marioParty2", "codes.marioParty3"):
            module = import_module(module_name)
            target = "mp" + module_name[-1]
            for function_name, function in inspect.getmembers(module, inspect.isfunction):
                values = []
                for parameter in inspect.signature(function).parameters:
                    if parameter in SHORT_HEX or parameter == "switch":
                        values.append("0A" if parameter != "switch" else "0")
                    elif function_name.startswith("getStarReplaceTwo") and parameter == "amount":
                        values.append("0A")
                    elif parameter.lower().endswith("name") or parameter.startswith("game"):
                        values.append("Test")
                    elif parameter.lower().endswith("dec") or parameter.lower().endswith("price"):
                        values.append("10")
                    else:
                        values.append("000A")

                output = function(*values)
                self.assertEqual(code_targets(output), {target}, function_name)
                for line in output.splitlines():
                    line = line.strip()
                    if not line or line.startswith("MP") or line.startswith("#"):
                        continue
                    self.assertRegex(line, CODE_LINE, function_name)


if __name__ == "__main__":
    unittest.main()
