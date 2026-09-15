#!/usr/bin/env python3
"""Generate diagnostic MP3 copies from trusted, recovered Python 3.12 GSInject modules.

This executes bytecode: use only the previously inspected GSInject recovery files.
It does not modify the installed injector. Run with the recovery's Python 3.12.
"""
import argparse
import copy
import dis
import marshal
import sys
import types
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recovery', required=True, type=Path, help='Directory of raw marshal .pyc files')
    parser.add_argument('--rom', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--variant', action='append', choices=('empty', 'normal-blue', 'old-blue', 'boot-only', 'expanded-control'))
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        parser.error('Recovered modules require Python 3.12')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from codes.marioParty3 import getBlueSpaceCodeThree
    from utils.rom_identity import inspect_n64
    if inspect_n64(args.rom).md5.upper() != '76A8BBC81BC2060EC99C9645867237CC':
        parser.error('Requires verified original MP3 NTSC-U ROM')
    for name in ('n64crc', 'injector_lib'):
        module = types.ModuleType(name)
        sys.modules[name] = module
        exec(marshal.loads((args.recovery / (name + '.pyc')).read_bytes()), module.__dict__)
    lib = sys.modules['injector_lib']
    cli = marshal.loads((args.recovery / 'injector_cli.pyc').read_bytes())
    code = next(c for c in cli.co_consts if isinstance(c, types.CodeType) and c.co_name == 'patch_rom')
    instructions = list(dis.get_instructions(code))
    if not (instructions[1].opname == 'LOAD_CONST' and instructions[1].argval is False
            and instructions[2].opname == 'STORE_FAST' and instructions[2].argval == 'old_emulator'):
        parser.error('Unrecognized injector bytecode; compatibility toggle was not changed')
    true_index = next(i for i, c in enumerate(code.co_consts) if c is True)
    if true_index > 255:
        parser.error('Unsupported constant table')
    raw = bytearray(code.co_code)
    raw[instructions[1].offset + 1] = true_index
    compatibility = code.replace(co_code=bytes(raw))
    env = {'copy': copy, 'injector_lib': lib, 'rom_object': lib.rom(str(args.rom))}
    args.output.mkdir(parents=True, exist_ok=False)
    blue = getBlueSpaceCodeThree('000A', 'A', '10', 'normal')
    for name, variant, codes in [('empty', code, ''), ('normal-blue', code, blue),
                                 ('old-blue', compatibility, blue), ('boot-only', code, ''),
                                 ('expanded-control', code, '')]:
        if args.variant and name not in args.variant:
            continue
        patched = types.FunctionType(variant, env)(codes)
        patched.data = bytearray(patched.data)
        if name in ('boot-only', 'expanded-control'):
            # MP3 NTSC-U-specific probe: remove the discovered exception hook.
            patched.data[0x80710:0x80720] = env['rom_object'].data[0x80710:0x80720]
        if name == 'expanded-control':
            # Original entry + original hook; only unused appended bytes remain.
            patched.data[0x1000:0x1010] = env['rom_object'].data[0x1000:0x1010]
        target = args.output / (name + '.z64')
        patched.save(str(target), checksum=True)
        print(target, flush=True)


if __name__ == '__main__':
    main()
