#!/usr/bin/env python3
"""Run an MP4-9 Gecko generator through Dolphin's native code manager."""

import argparse
import importlib
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True, choices=("mp4", "mp5", "mp6", "mp7", "mp8", "mp9"))
    parser.add_argument("--iso", required=True, type=Path)
    parser.add_argument("--function", required=True)
    parser.add_argument("arguments", nargs="*")
    parser.add_argument("--dolphin", required=True, type=Path)
    parser.add_argument("--fast", action="store_true", help="Run without Dolphin's speed limiter for board-load smoke tests")
    args = parser.parse_args()

    module = importlib.import_module(f"codes.marioParty{args.game[-1]}")
    try:
        code = getattr(module, args.function)(*args.arguments)
    except (AttributeError, TypeError) as error:
        parser.error(str(error))

    print("Native Dolphin test code:\n" + code.strip())
    with tempfile.TemporaryDirectory(prefix=f"mpt-dolphin-{args.game}-") as user_dir:
        config = Path(user_dir) / "Config"
        settings = config / "GameSettings"
        settings.mkdir(parents=True)
        core = "[Core]\nEnableCheats = True\n"
        if args.fast:
            core += "SpeedLimit = 0\nAudioStretch = False\n"
        (config / "Dolphin.ini").write_text(core, encoding="utf-8")
        settings_file = settings / {
            "mp4": "GMPE01.ini", "mp5": "GP5E01.ini", "mp6": "GP6E01.ini", "mp7": "GP7E01.ini",
            "mp8": "RM8E01.ini", "mp9": "SSQE01.ini",
        }[args.game]
        settings_file.write_text("[Gecko]\n$MPT generated test\n" + code.strip() + "\n", encoding="utf-8")
        command = [str(args.dolphin.expanduser().resolve(strict=True)), "--user", user_dir,
                   "--exec", str(args.iso.expanduser().resolve(strict=True))]
        process = subprocess.Popen(command)
        print(f"Dolphin launched (PID {process.pid}). Test the original ISO, then close Dolphin.")
        process.wait()


if __name__ == "__main__":
    main()
