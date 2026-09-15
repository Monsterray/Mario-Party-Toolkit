import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from utils.injector_tools import resolve_tool


class InjectorToolTests(unittest.TestCase):
    def test_env_override_returns_argv(self):
        with patch.dict(os.environ, {"MPT_WIT": "/tmp/wit"}):
            self.assertEqual(resolve_tool("wit", Path), ["/tmp/wit"])

    def test_gecko_source_returns_python_argv(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home) / "Tools" / "mario-party-rom-lab" / "source" / "GeckoLoader"
            root.mkdir(parents=True)
            script = root / "GeckoLoader.py"
            script.write_text("# fixture")
            with patch("utils.injector_tools.Path.home", return_value=Path(home)):
                with patch("utils.injector_tools.sys.platform", "darwin"):
                    argv = resolve_tool("GeckoLoader", Path)
            self.assertEqual(argv[0], os.sys.executable)
            self.assertEqual(Path(argv[1]), script)


if __name__ == "__main__":
    unittest.main()
