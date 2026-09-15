#!/usr/bin/env python3
"""Interactively test representative Mario Party 3 generators in Mupen."""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from codes import marioParty1 as mp1
from codes import marioParty2 as mp2
from codes import marioParty3 as mp3
from tools.mpt_cli import native_cheat_file, mupen_workdir


CASES = {
    "blue": ("getBlueSpaceCodeThree", ("000A", "A", "10", "normal")),
    "red": ("getRedSpaceCodeThree", ("000A", "A", "10", "normal")),
    "star": ("getStarSpaceCodeThree", ("0064", "FF9C", "100")),
    "koopa": ("getKoopaBankCodeThree", ("0064", "FF9C", "100")),
    "minigame": ("getMinigameReplacement3", ("01", "02", "Game 1", "Game 2")),
    "items": ("getItems3", ("0A",) * 16 + ("01",)),
    "handicap": ("getStarHandicap", ("01", "01", "01", "01")),
    "boo_star": ("getBooStarPrice", ("0064", "FF9C", "100")),
    "boo_coins": ("getBooCoinsPrice", ("000A", "FFF6", "10")),
    "item_replace": ("getItemReplaceThree", ("01", "02", "Mushroom", "Star")),
}

GAME_CASES = {
    "mp1": {
        "blue": ("getBlueSpaceCodeOne", ("000A", "A", "10", "normal")),
        "red": ("getRedSpaceCodeOne", ("000A", "A", "10", "normal")),
        "minigame": ("getMinigameReplacement1", ("01", "02", "Game 1", "Game 2")),
        "handicap": ("getStarHandicapP1", ("01", "01", "01", "01")),
        "items": ("getBlockWeights", ("01", "02", "03", "04", "05", "06")),
        "star": ("getStarSpaceCodeOne", ("0064", "FF9C", "100")),
    },
    "mp2": {
        "blue": ("getBlueSpaceCodeTwo", ("000A", "A", "10", "normal")),
        "red": ("getRedSpaceCodeTwo", ("000A", "A", "10", "normal")),
        "minigame": ("getMinigameReplacement2", ("01", "02", "Game 1", "Game 2")),
        "handicap": ("getStarHandicapP1", ("01", "01", "01", "01")),
        "items": ("getItems2", ("01", "02", "03", "05", "06", "09", "0A")),
        "star": ("getStarSpaceCodeTwo", ("0064", "FF9C", "100")),
        "koopa": ("getKoopaBankCodeTwo", ("0064", "FF9C", "100")),
    },
    "mp3": CASES,
}

MODULES = {"mp1": mp1, "mp2": mp2, "mp3": mp3}


def main():
    parser = argparse.ArgumentParser(description=__doc__.replace("Mario Party 3", "Mario Party 1/2/3"))
    parser.add_argument("--game", required=True, choices=tuple(GAME_CASES))
    parser.add_argument("--rom", required=True, type=Path)
    parser.add_argument("--mupen", required=True, type=Path)
    parser.add_argument("--only")
    args = parser.parse_args()

    cases = GAME_CASES[args.game]
    if args.only and args.only not in cases:
        parser.error(f"unknown {args.game} code: {args.only}")
    names = [args.only] if args.only else list(cases)
    for name in names:
        function_name, values = cases[name]
        code = getattr(MODULES[args.game], function_name)(*values)
        print("\n" + "=" * 72)
        print(f"Testing {name}: {function_name}{values}")
        print(code.strip())
        input("Press Enter to launch Mupen. Close it, then press Enter here to continue...")

        with tempfile.TemporaryDirectory(prefix=f"mpt-{name}-") as data_dir:
            native_cheat_file(args.rom, code, data_dir, args.game)
            command = [str(args.mupen), "--gfx", "mupen64plus-video-glide64mk2",
                       "--datadir", data_dir, "--cheats", "0", "--noosd",
                       "--nosaveoptions", str(args.rom)]
            process = subprocess.Popen(command, cwd=mupen_workdir(args.mupen),
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True)
            print(f"Launched PID {process.pid}. Test the behavior, then close Mupen.")
            input("Press Enter after Mupen is closed...")
            if process.poll() is None:
                process.terminate()
            output, _ = process.communicate(timeout=5)
            loaded = "activated cheat code 0" in output
            print(f"{name}: {'LOADED' if loaded else 'NOT CONFIRMED'}")


if __name__ == "__main__":
    main()
