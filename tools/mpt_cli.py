#!/usr/bin/env python3
"""Headless helpers for repeatable Mario Party Toolkit tests."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Allow `python tools/mpt_cli.py` from the repository root without packaging.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.code_validation import validate_code_target
from utils.rom_identity import inspect_n64, pp64_target_status


CODE_LINE = re.compile(r"^[0-9A-Fa-f]{8}\s+(?:[0-9A-Fa-f]{2}|[0-9A-Fa-f]{4})$")


def output(data, pretty=False):
    print(json.dumps(data, indent=2 if pretty else None, sort_keys=True, default=str))


def identity_data(identity):
    return {
        "path": str(identity.path),
        "size": identity.size,
        "md5": identity.md5,
        "sha256": identity.sha256,
        "byte_order": identity.byte_order,
        "internal_name": identity.internal_name,
        "region": identity.region,
        "version": identity.version,
        "pp64_game": identity.pp64_game,
    }


def inspect_command(args):
    identity = inspect_n64(args.rom)
    result = identity_data(identity)
    if args.game:
        _, status = pp64_target_status(args.rom, args.game)
        result["requested_game"] = args.game
        result["target_status"] = status
    output(result, args.pretty)
    return 0


def read_code(path):
    if str(path) == "-":
        return sys.stdin.read()
    return Path(path).expanduser().read_text(encoding="utf-8")


def validate_code_text(text, game):
    valid, message = validate_code_target(text, game)
    malformed = []
    for line_number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith(("#", "$", "MP")):
            continue
        if not CODE_LINE.fullmatch(line):
            malformed.append(line_number)
    return valid and not malformed, message, malformed


def validate_command(args):
    valid, message, malformed = validate_code_text(read_code(args.code), args.game)
    output({"valid": valid, "message": message, "malformed_lines": malformed}, args.pretty)
    return 0 if valid else 2


def generate_command(args):
    module_name, separator, function_name = args.function.rpartition(".")
    if not separator:
        raise ValueError("Function must be written as codes.marioParty1.function_name")
    function = getattr(importlib.import_module(module_name), function_name)
    result = function(*args.arguments)
    print(result, end="" if result.endswith("\n") else "\n")
    return 0


def mupen_workdir(executable):
    """Return the bundled Mupen source directory needed for relative assets."""
    path = Path(executable).expanduser()
    if path.parent.name == "MacOS" and path.parent.parent.parent.name == "mupen64plus.app":
        return path.parents[3]
    return None


def run_process(executable, rom, timeout, log_path=None, gfx=None, settings=()):
    command = [str(executable)]
    command.extend(["--gfx", gfx or "mupen64plus-video-glide64mk2"])
    for setting in settings:
        command.extend(["--set", setting])
    command.extend(["--windowed", "--noosd", "--nosaveoptions", str(rom)])
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=mupen_workdir(executable),
        )
        timed_out = False
    except subprocess.TimeoutExpired as error:
        completed = error
        timed_out = True

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    combined = stdout + stderr
    if log_path:
        Path(log_path).expanduser().write_text(combined, encoding="utf-8")
    return {
        "command": command,
        "returncode": None if timed_out else completed.returncode,
        "timed_out": timed_out,
        "header_parsed": "Core: Imagetype:" in combined and "Core: Country:" in combined,
        "open_gl_attempted": "Initializing OpenGL" in combined,
        "log": str(Path(log_path).expanduser()) if log_path else None,
        "output": combined[-4000:],
    }


def run_mupen_command(args):
    result = run_process(args.mupen, args.rom, args.timeout, args.log, args.gfx, args.setting)
    output(result, args.pretty)
    return 0 if result["header_parsed"] else 3


def locate_injector():
    override = os.environ.get("MPT_GSINJECT")
    if override:
        return Path(override).expanduser()
    candidates = [
        Path(__file__).resolve().parents[1] / "dependencies/macOS/GSInject",
        Path.home() / "Tools/mario-party-rom-lab/bin/GSInject",
    ]
    return next((path for path in candidates if path.is_file()), None)


def inject_copy(injector, code_text, rom, destination):
    with tempfile.TemporaryDirectory(prefix="mpt-cli-") as temp_dir:
        code_path = Path(temp_dir) / "codes.txt"
        code_path.write_text("$MPToolkit\n" + code_text, encoding="utf-8")
        command = [str(injector), str(code_path), str(rom), str(destination)]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=60)
        except OSError as error:
            return {"injected": False, "command": command, "error": str(error)}
    return {
        "injected": completed.returncode == 0 and destination.is_file(),
        "command": command,
        "returncode": completed.returncode,
        "output": (completed.stdout + completed.stderr)[-2000:],
    }


def test_command(args):
    if not args.skip_mupen and not args.mupen:
        raise ValueError("--mupen is required unless --skip-mupen is used")
    rom = Path(args.rom).expanduser().resolve()
    code_text = read_code(args.code)
    valid, message, malformed = validate_code_text(code_text, args.game)
    identity = inspect_n64(rom)
    if identity.pp64_game and identity.pp64_game != args.game:
        valid = False
        message = f"ROM hash identifies {identity.pp64_game.upper()}, but the selected game is {args.game.upper()}."
    result = {
        "rom": identity_data(identity),
        "code": {"valid": valid, "message": message, "malformed_lines": malformed},
        "injection": {"injected": False, "skipped": True},
        "mupen": None,
    }
    if not valid:
        output(result, args.pretty)
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    patched = output_dir / f"{rom.stem} (MPT test){rom.suffix}"
    injector = locate_injector()
    if injector:
        result["injection"] = inject_copy(injector, code_text, rom, patched)
        if not result["injection"]["injected"]:
            result["injection"]["note"] = "Injector unavailable or incompatible; original ROM was preserved."
    else:
        result["injection"]["note"] = "GSInject was not found; original ROM was preserved."

    boot_rom = patched if result["injection"].get("injected") else rom
    if args.skip_mupen:
        result["mupen"] = {"skipped": True, "gameplay_verified": False}
    else:
        result["mupen"] = run_process(args.mupen, boot_rom, args.timeout, args.log, args.gfx, args.setting)
        result["mupen"]["gameplay_verified"] = False
    output(result, args.pretty)
    if args.skip_mupen:
        return 0
    if not result["injection"].get("injected"):
        return 4
    return 0 if result["mupen"]["header_parsed"] else 3


def parser():
    parser = argparse.ArgumentParser(prog="mpt-cli", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect-rom")
    inspect.add_argument("rom", type=Path)
    inspect.add_argument("--game", choices=("mp1", "mp2", "mp3"))
    inspect.add_argument("--pretty", action="store_true")
    inspect.set_defaults(handler=inspect_command)

    validate = sub.add_parser("validate-code")
    validate.add_argument("code", type=Path)
    validate.add_argument("--game", required=True, choices=("mp1", "mp2", "mp3"))
    validate.add_argument("--pretty", action="store_true")
    validate.set_defaults(handler=validate_command)

    generate = sub.add_parser("generate-code")
    generate.add_argument("function", help="module.function, for example codes.marioParty1.getInfiniteCoins")
    generate.add_argument("arguments", nargs="*")
    generate.set_defaults(handler=generate_command)

    mupen = sub.add_parser("run-mupen")
    mupen.add_argument("rom", type=Path)
    mupen.add_argument("--mupen", required=True, type=Path)
    mupen.add_argument("--timeout", type=float, default=8)
    mupen.add_argument("--log", type=Path)
    mupen.add_argument("--gfx", help="Mupen video plugin (default: mupen64plus-video-glide64mk2)")
    mupen.add_argument("--set", dest="setting", action="append", default=[], help="Mupen setting, repeatable; e.g. Audio-SDL[RESAMPLE]=src-linear")
    mupen.add_argument("--pretty", action="store_true")
    mupen.set_defaults(handler=run_mupen_command)

    test = sub.add_parser("test")
    test.add_argument("rom", type=Path)
    test.add_argument("--game", required=True, choices=("mp1", "mp2", "mp3"))
    test.add_argument("--code", required=True, type=Path)
    test.add_argument("--mupen", type=Path)
    test.add_argument("--output-dir", default="test-results", type=Path)
    test.add_argument("--timeout", type=float, default=8)
    test.add_argument("--log", type=Path)
    test.add_argument("--gfx", help="Mupen video plugin (default: mupen64plus-video-glide64mk2)")
    test.add_argument("--set", dest="setting", action="append", default=[], help="Mupen setting, repeatable; e.g. Audio-SDL[RESAMPLE]=src-linear")
    test.add_argument("--skip-mupen", action="store_true")
    test.add_argument("--pretty", action="store_true")
    test.set_defaults(handler=test_command)
    return parser


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        return args.handler(args)
    except (FileNotFoundError, ImportError, AttributeError, ValueError, OSError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
