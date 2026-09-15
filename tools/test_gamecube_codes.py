#!/usr/bin/env python3
"""Generate, inject, rebuild, and optionally launch MP4-9 Gecko codes."""

import argparse
import importlib
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


MODULES = {f"mp{number}": f"codes.marioParty{number}" for number in range(4, 10)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True, choices=tuple(MODULES))
    parser.add_argument("--iso", required=True, type=Path)
    parser.add_argument("--function", required=True, help="Generator function, e.g. getBlueSpaceCodeFour")
    parser.add_argument("arguments", nargs="*", help="Generator arguments, in function order")
    parser.add_argument("--geckoloader", required=True, type=Path)
    parser.add_argument("--wit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New patched ISO path")
    parser.add_argument("--optimize", action="store_true", help="Ask GeckoLoader to optimize direct RAM writes")
    parser.add_argument("--dolphin", type=Path, help="Optional Dolphin executable")
    parser.add_argument("--launch", action="store_true", help="Launch the rebuilt ISO in Dolphin")
    args = parser.parse_args()

    module = importlib.import_module(MODULES[args.game])
    try:
        code = getattr(module, args.function)(*args.arguments)
    except (AttributeError, TypeError) as error:
        parser.error(str(error))

    print("Generated code:\n" + code.strip() + "\n", flush=True)
    iso = args.iso.expanduser().resolve(strict=True)
    output = args.output.expanduser().resolve()
    if output.exists():
        parser.error(f"Output already exists: {output}")
    args.geckoloader = args.geckoloader.expanduser().resolve(strict=True)
    args.wit = args.wit.expanduser().resolve(strict=True)

    with tempfile.TemporaryDirectory(prefix=f"mpt-{args.game}-") as temp:
        root = Path(temp)
        extracted = root / "extracted"
        codes = root / "codes.txt"
        patched_dol = root / "patched-dol"
        codes.write_text(code, encoding="utf-8")
        subprocess.run([str(args.wit), "extract", str(iso), "--dest", str(extracted)], check=True)
        dol = next(extracted.rglob("main.dol"), None)
        if dol is None:
            raise RuntimeError("Extracted disc does not contain sys/main.dol")
        patched_dol.mkdir()
        command = [sys.executable, str(args.geckoloader), "--hooktype=GX"]
        if args.optimize:
            command.append("--optimize")
        command.extend([str(dol), str(codes), "--dest=" + str(patched_dol)])
        subprocess.run(command, check=True)
        built_dol = patched_dol / "main.dol"
        if not built_dol.is_file():
            raise RuntimeError("GeckoLoader did not produce main.dol")
        shutil.copy2(built_dol, dol)
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(args.wit), "copy", str(extracted), "--dest", str(output)], check=True)

    print(f"Built: {output}")
    if args.launch:
        if not args.dolphin:
            parser.error("--launch requires --dolphin")
        dolphin = args.dolphin.expanduser().resolve(strict=True)
        process = subprocess.Popen([str(dolphin), str(output)])
        print(f"Dolphin launched (PID {process.pid}). Test the code, then close Dolphin.")
        process.wait()


if __name__ == "__main__":
    main()
