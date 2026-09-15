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

Original MD5: `76A8BBC81BC2060EC99C9645867237CC`.
Existing and regenerated blue-space SHA256:
`F60842F43FC20F86AF0917947BB64AB93C09F0587CA694F078A495C711CFED3D`.
Generated with `getBlueSpaceCodeThree 000A A 10 normal` and the locally built
Intel GSInject. Labels do not affect the injected binary.

## Conclusions and limits

The demonstrated failure follows the injected ROM. Its exact failing instruction
has not yet been identified. GSInject's boot loader/exception hook, code execution,
and emulator compatibility remain candidates. Successful injection and parsing a
ROM header do not establish a successful boot or correct gameplay.

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
is to trace the injected entry/loader and compare against a minimal injection
that preserves ordinary gameplay, using the working original as control.

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
