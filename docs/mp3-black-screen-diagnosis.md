# MP3 black-screen diagnosis

## Observed results — 2026-09-14

Intel macOS 13.7.8; bundled Mupen64Plus 2.6.0, Glide64mk2.
Tests ran sequentially with desktop access. Screenshots were inspected directly.

| Test | Result |
| --- | --- |
| Original NTSC-U MP3, direct Mupen | Opening animation and story text rendered after an initially black capture |
| Existing blue-space patched ROM, identical direct command | Remained black through repeated captures; video and CPU initialized |
| Full CLI: generate blue-space code, inject, launch | Fresh output matched existing patch SHA256; black screen; 60-second timeout |
| Existing patch with pure interpreter | Black at observation time |
| Existing patch with original game's CountPerOp=1 | Black at observation time |
| Original ROM with generated code through Mupen native cheats | ROM matched and cheat code 0 activated; no patched ROM involved |

Original MD5: `76A8BBC81BC2060EC99C9645867237CC`.
Existing and regenerated blue-space SHA256:
`F60842F43FC20F86AF0917947BB64AB93C09F0587CA694F078A495C711CFED3D`.
Generated with `getBlueSpaceCodeThree 000A A 10 normal` and the locally built
Intel GSInject. Labels do not affect the injected binary.

## Conclusions and limits

The demonstrated failure follows the injected ROM. An empty injection also
fails, while Mupen activates the same generated GameShark lines on the original
ROM. The code generator and base ROM are therefore not the cause. The remaining
failure is GSInject's injected boot/exception-hook loader under this Mupen path;
the exact failing instruction is still unknown. Successful injection and parsing
a ROM header do not establish a successful boot or correct gameplay.

Earlier claims that `--windowed` caused this failure were incorrect: the original
ROM rendered with that option enabled. Both successful and unsuccessful runs log
`Using video capture backend: dummy`; the config identifies this as Game Boy
Camera capture, so that message does not diagnose the display renderer.

Earlier restricted runs aborted in Cocoa_RegisterApp. Desktop-authorized runs
initialize video successfully. Those startup aborts must be distinguished from
the patched ROM's persistent black display.

The full CLI run returned exit 3, timed_out=true, header_parsed=false and empty
captured emulator output after 60 seconds. This is consistent with child stdout
buffering through a pipe. Separately, the CLI currently accepts header_parsed as
success even when the emulator exits with an error; that is an unreliable boot
criterion. Its default eight-second observation period is also inadequate for
establishing visible startup on this system.

Binary comparison found changes in the ROM checksum, entry code near 0x1000,
and hook near 0x80718, plus 416 appended bytes. The next targeted investigation
is to trace the injected entry/loader against the working original. Until that
loader is ported or proven compatible, use Mupen's native-cheat mode for code
verification instead of treating a black injected ROM as a code failure.

## Reproduce the direct comparison

From the directory containing mupen64plus.app, run:

```bash
./mupen64plus.app/Contents/MacOS/mupen64plus \
  --gfx mupen64plus-video-glide64mk2 \
  --windowed --resolution 640x480 --nosaveoptions \
  '/absolute/path/to/ROM.z64'
```

Use the original first, then the existing blue-space ROM with exactly the same
options. Allow at least 60 seconds and capture multiple frames. Close each
process before the next run. A black early frame alone is inconclusive.

CPU modes are documented in the official
[console usage guide](https://mupen64plus.org/wiki/index.php/UIConsoleUsage).
The bundle's Readme.txt explicitly requires a Terminal launch and warns against
opening the app through Finder.

Diagnostic screenshots remain outside the repository in `/private/tmp`:
`mpt-original-later.png`, `mpt-patched-later.png`, `mpt-full-cli-screen.png`,
`mpt-patched-interpreter.png`, and `mpt-patched-timing.png`.
All emulator processes started for this diagnosis were stopped.

## Reusable probes

`tools/diagnose_mupen.py` runs cases sequentially, captures the macOS desktop at
10 and 45 seconds by default, saves stdout/stderr to files, and stops each child
with SIGINT. `report.json` records hashes, commands, timing and exit status.
Screenshots need visual review: a running emulator is not proof of a boot.
Use a new output directory on every run. macOS screen-recording permission and
desktop access are required; screenshots can include other visible applications.

```bash
LAB="$HOME/Tools/mario-party-rom-lab"
./mariovenv/bin/python tools/diagnose_mupen.py \
  --mupen "$LAB/source/mupen64plus-2.6.0/mupen64plus.app/Contents/MacOS/mupen64plus" \
  --cwd "$LAB/source/mupen64plus-2.6.0" \
  --output /private/tmp/mp3-comparison-01 \
  --case "original=$LAB/roms/Mario Party 3/Mario Party 3 (U) [!].z64" \
  --case "blue=$LAB/test-results/mp3-code-matrix/blue-space.z64"
```

`tools/probe_gsinject.py` generates isolated injection variants from the trusted
recovered GSInject modules. It requires Python 3.12 and raw marshal modules from
the existing recovery. These are executable modules, not untrusted input data.
The probe validates the original MP3 hash and the compatibility-toggle bytecode
before changing it in memory. Installed binaries and original ROM are unchanged.

```bash
/private/tmp/gsinject-decompiler-venv/bin/python tools/probe_gsinject.py \
  --recovery /private/tmp/gsinject-build.nlidT8 \
  --rom "$LAB/roms/Mario Party 3/Mario Party 3 (U) [!].z64" \
  --output /private/tmp/mp3-variants-01
```

Recovery paths above are local temporary artifacts; replace them if moved.
Variants: empty injection, normal blue-space injection, built-in old-emulator
mode, boot-loader-only (exception hook restored), and expanded original control
(both entry and exception hook restored). Select individual variants with
repeatable `--variant` options. Feed their paths to `diagnose_mupen.py --case`.

## Safe generated-code check in Mupen

The reusable CLI writes a temporary Mupen cheat database, runs the verified
original ROM, and deletes the database afterward:

```bash
./mariovenv/bin/python tools/mpt_cli.py generate-code \
  codes.marioParty3.getBlueSpaceCodeThree 000A A 10 normal |
./mariovenv/bin/python tools/mpt_cli.py test-native-cheat \
  "$LAB/roms/Mario Party 3/Mario Party 3 (U) [!].z64" --game mp3 --code - \
  --mupen "$LAB/source/mupen64plus-2.6.0/mupen64plus.app/Contents/MacOS/mupen64plus" \
  --pretty
```

`cheat_activated: true` proves Mupen matched the ROM CRC/CIC and loaded the
code list. It is a loader/application check, not a substitute for playing the
board and confirming the visible behavior.

## Local-model efficiency findings

Small structured completions avoided the empty answers previously seen when
web-summary calls spent their entire budget thinking. They still introduced
unsupported claims (including calling CountPerOp instruction monitoring, inventing
blue-screen errors, and recommending preservation of registers without showing
that the loader changed them). Treat these outputs as hypotheses.

Backend improvements worth testing:

- Expose `enable_thinking` and `max_tokens` consistently on fetch/summarize tools.
- Require evidence IDs for factual claims and explicit unknowns; evaluate claim
  fidelity, not merely valid JSON. Include these failures as regression examples.
- Return compact structured content once, avoiding duplicate JSON in both text
  and structured response fields when the client supports structured content.
- Cache page extraction and deterministic disassembly; send only changed facts
  and selected instruction ranges to models on subsequent probes.
- Add optional screenshot comparison with artifact references; keep visible-boot
  judgments separate from process/log heuristics and verify on known black frames.
