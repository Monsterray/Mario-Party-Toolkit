#!/usr/bin/env python3
"""Build a deterministic catalog of Mario Party 1–9 code generators."""

import argparse
import importlib
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def build_catalog():
    catalog = []
    for game_number in range(1, 10):
        game = f"mp{game_number}"
        module_name = f"codes.marioParty{game_number}"
        module = importlib.import_module(module_name)
        platform = "n64" if game_number <= 3 else ("gamecube" if game_number <= 7 else "wii")
        runner = "mupen-native-cheat" if game_number <= 3 else "dolphin-native-gecko"
        for name, function in inspect.getmembers(module, inspect.isfunction):
            if function.__module__ != module_name:
                continue
            parameters = [
                parameter.name
                for parameter in inspect.signature(function).parameters.values()
            ]
            catalog.append({
                "game": game,
                "module": module_name,
                "generator": name,
                "parameters": parameters,
                "platform": platform,
                "code_family": "gameshark" if game_number <= 3 else "gecko",
                "test_runner": runner,
            })
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build_catalog(), indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
