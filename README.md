# Mario Party Toolkit

Mario Party Toolkit generates gameplay-modification codes for Mario Party 1–9 and Mario Party DS. It supports N64 GameShark-style codes, GameCube/Wii Gecko-style codes, and platform-specific packaging with PyInstaller.

Use images dumped from games you own. Keep the original image unchanged and test generated output on a copy.

## Setup and build by operating system

Requirements: Python 3.10 or newer. Keep the virtual environment in the project directory; it is ignored by Git.

### macOS

```bash
./install_macos_deps.sh
./mariovenv/bin/python main.py
./build-macos.sh
```

The build creates `dist/MarioPartyToolkit` and `dist/MarioPartyToolkit.app`. The setup script does not modify the system Python installation.

### Windows

```powershell
python -m venv mariovenv
mariovenv\Scripts\python.exe -m pip install --upgrade pip
mariovenv\Scripts\python.exe -m pip install -r requirements.txt
mariovenv\Scripts\python.exe main.py
mariovenv\Scripts\python.exe build.py
```

The build creates the packaged executable in `dist/`.

### Linux

```bash
python3 -m venv mariovenv
./mariovenv/bin/python -m pip install --upgrade pip
./mariovenv/bin/python -m pip install -r requirements.txt
./mariovenv/bin/python main.py
./mariovenv/bin/python build.py
```

The build creates the packaged executable in `dist/`.

For packaged-app diagnosis, run the standalone executable from Terminal:

```bash
./dist/MarioPartyToolkit
```

### GUI inspection hooks

The GUI has opt-in hooks for deterministic local inspection. They select a
page and tab, capture the window, dump measured tab/switch geometry, and exit
automatically. Normal launches are unchanged:

```bash
./mariovenv/bin/python main.py \
  --mpt-test-game marioParty2 \
  --mpt-test-tab "Minigame Replacement" \
  --mpt-test-screenshot /private/tmp/mpt-ui.png \
  --mpt-test-dump /private/tmp/mpt-ui.json
```

The same flags work with `./dist/MarioPartyToolkit`. Use
`--mpt-test-quit-after 3000` to keep the window open for three seconds.
The JSON records each tab's rendered rectangle and each qfluent switch
indicator's rectangle, making clipping and alignment regressions measurable.

## Headless and emulator testing

The standalone CLI keeps repeatable checks outside the GUI. Run it from the project root:

```bash
./mariovenv/bin/python tools/mpt_cli.py inspect-rom /path/to/game.z64 --game mp1 --pretty
./mariovenv/bin/python tools/mpt_cli.py validate-code codes.txt --game mp1 --pretty
./mariovenv/bin/python tools/mpt_cli.py generate-code codes.marioParty1.getStarSpaceCodeOne 0A 00 10
```

`test` combines ROM inspection, code validation, a safe injection attempt, and a bounded Mupen64Plus launch. It never overwrites the input ROM. Use `-` as the code path to connect a generator directly to the test runner:

```bash
MUPEN=/path/to/mupen64plus
ROM=/path/to/mario-party-1.z64
./mariovenv/bin/python tools/mpt_cli.py generate-code \
  codes.marioParty1.getStarSpaceCodeOne 0A 00 10 |
./mariovenv/bin/python tools/mpt_cli.py test "$ROM" --game mp1 --code - \
  --mupen "$MUPEN" --output-dir test-results --pretty
```

The JSON report distinguishes ROM-header parsing from gameplay verification. Exit status `0` means the ROM was injected and Mupen parsed its header; `2` means code validation failed; `3` means Mupen did not parse a header; `4` means injection failed. Mupen may stop when its OpenGL context cannot be created; that is an emulator/display limitation, not proof that the ROM or code is wrong.
When Mupen stops before parsing the header, gameplay remains unverified.

For Mupen testing on macOS, `test-native-cheat` applies generated GameShark
lines through Mupen's native cheat engine while leaving the base ROM unchanged.
This is the preferred code-validation path while GSInject is being diagnosed:

```bash
./mariovenv/bin/python tools/mpt_cli.py generate-code \
  codes.marioParty3.getBlueSpaceCodeThree 000A A 10 normal |
./mariovenv/bin/python tools/mpt_cli.py test-native-cheat "$ROM" --game mp3 \
  --code - --mupen "$MUPEN" --pretty
```

The JSON reports `cheat_activated: true` only when Mupen matched the ROM and
activated code 0. It does not claim gameplay success; confirm the visible
behavior in the emulator.

Every headless run also emits a small observation record. `loaded` and
`booted` are runner facts; `visibly_changed` and `behavior_confirmed` require
manual inspection or a narrow oracle. Promote a saved report after checking
the baseline and modified runs:

```bash
./mariovenv/bin/python tools/runner_result.py run.json \
  --confirm visibly_changed --confirm behavior_confirmed \
  --evidence "Observed the generated value change" \
  --output verified-run.json
```

Reusable baseline/scenario descriptions are in `data/test-scenarios.json`.
They intentionally contain no local ROM paths.

### Intel macOS GSInject

The bundled macOS GSInject is arm64. On an Intel Mac, install an x86_64 build in the shared ROM-lab tools directory and select it explicitly:

```bash
file ~/Tools/mario-party-rom-lab/bin/GSInject
export MPT_GSINJECT=~/Tools/mario-party-rom-lab/bin/GSInject
```

The override is also honored by the GUI injector. Keep patched ROMs in a separate results directory; the CLI never overwrites its input ROM.

### MP3 smoke-test example

This tests a verified NTSC-U MP3 base ROM and writes the patched copy to `test-results/mp3-stars`:

```bash
ROM="$HOME/Tools/mario-party-rom-lab/roms/Mario Party 3/Mario Party 3 (U) [!].z64"
MUPEN="$HOME/Tools/mario-party-rom-lab/source/mupen64plus-2.6.0/mupen64plus.app/Contents/MacOS/mupen64plus"
./mariovenv/bin/python tools/mpt_cli.py generate-code \
  codes.marioParty3.getStarSpaceCodeThree 0A 00 10 |
./mariovenv/bin/python tools/mpt_cli.py test "$ROM" --game mp3 --code - \
  --mupen "$MUPEN" --output-dir test-results/mp3-stars --pretty
```

The MP3 generator expects `switch` as one hexadecimal digit. For example, use `A`, not `00`; the CLI rejects malformed generated lines before injection.

For a fast injection-only matrix, omit `--mupen` and add `--skip-mupen`; this returns success after validation and injection without launching an emulator.

For the bundled Mupen build on this Intel Mac, use Glide64mk2. It renders MP3 correctly on the tested Intel/Radeon system; Rice can open a black window. The CLI now selects Glide64mk2 by default:

```bash
./mariovenv/bin/python tools/mpt_cli.py run-mupen /path/to/test.z64 \
  --mupen "$MUPEN" --timeout 30 --pretty
```

For the fastest board-load smoke test, add `--fast`. This selects dummy audio
and disables the speed limiter; sound is intentionally unavailable. Normal
testing should omit it and use Mupen's `F` key for temporary fast-forward.
`F10`/`F11` adjust speed by 5%, and `/` advances one frame while paused.
Add `--testshots 300 --screenshot-dir /private/tmp/mpt-shots` to capture a
deterministic startup frame and exit automatically.

The tested Mupen keyboard layout is: analog stick `WASD`, A `Right Ctrl`, B
`Right Alt`, Z `Z`, Start `Enter`, C buttons `I/J/K/L`, and triggers `X/C`.

### GameCube/Wii Gecko-code testing (MP4–9)

GameCube codes use GeckoLoader and a rebuilt ISO. The reusable helper prints the
exact code, extracts `main.dol`, patches it, rebuilds a separate ISO, and can
launch Dolphin for manual testing:

```bash
./mariovenv/bin/python tools/test_gamecube_codes.py \
  --game mp4 \
  --iso "$HOME/Tools/mario-party-rom-lab/roms/Mario Party 4 [GMPE01]/game.iso" \
  --function getBlueSpaceCodeFour 000A 10 \
  --geckoloader "$HOME/Tools/mario-party-rom-lab/source/GeckoLoader/GeckoLoader.py" \
  --wit "$HOME/Tools/mario-party-rom-lab/bin/wit" \
  --output /private/tmp/mp4-blue.iso \
  --dolphin "$HOME/Tools/mario-party-rom-lab/Dolphin-2606a.app/Contents/MacOS/Dolphin" \
  --launch
```

Use the matching `marioParty5` through `marioParty9` generator and
`--game` value for the other discs. Keep rebuilt images outside the repository.

For Dolphin validation, use the native Gecko path instead of the rebuilt ISO:

```bash
./mariovenv/bin/python tools/test_dolphin_gecko.py \
  --game mp4 \
  --iso "$HOME/Tools/mario-party-rom-lab/roms/Mario Party 4 [GMPE01]/game.iso" \
  --function getBlueSpaceCodeFour 000A 10 \
  --dolphin "$HOME/Tools/mario-party-rom-lab/Dolphin-2606a.app/Contents/MacOS/Dolphin"
```

On the tested Dolphin build, the GeckoLoader-patched image crashes in its
embedded handler at `0x81200D60`, while the same code works through Dolphin's
native Gecko manager.

Dolphin's default fast-forward/turbo hotkey is `Tab` (hold it). `Space` is
frame advance when paused. The current keyboard GameCube layout is: analog
stick arrow keys, A `X`, B `Z`, X `C`, Y `S`, Z `D`, Start `Enter`, L `Q`, R
`W`, C-stick `I/J/K/L`, and D-pad `T/F/G/H`. A physical GameCube controller is
recommended for play; configure it under Controllers if the keyboard map is
not active. The Dolphin runner also accepts `--fast`, which disables its speed
limiter and audio stretching for short board-load smoke tests.

Mupen settings are passed with repeatable `--set` options. If gameplay or sound runs below real time, first try the lower-CPU audio resampler:

```bash
./mariovenv/bin/python tools/mpt_cli.py run-mupen /path/to/test.z64 \
  --mupen "$MUPEN" \
  --set 'Audio-SDL[RESAMPLE]=src-linear' \
  --timeout 30 --pretty
```

If that does not restore normal speed, use this as a diagnostic; it may allow video to run at full speed while audio crackles or drifts:

```bash
./mariovenv/bin/python tools/mpt_cli.py run-mupen /path/to/test.z64 \
  --mupen "$MUPEN" \
  --set 'Audio-SDL[RESAMPLE]=src-linear' \
  --set 'Audio-SDL[AUDIO_SYNC]=False' \
  --timeout 30 --pretty
```

## Injector backends

The injector uses these tools:

| Input | Backend | Current status |
|---|---|---|
| N64 `.z64` | `GSInject` | Windows binary bundled; Intel macOS requires an x86_64 build selected with `MPT_GSINJECT` |
| ISO/WBFS | `wit` | Supported when a native executable is installed |
| GameCube/Wii DOL | GeckoLoader | Windows binary bundled; official Python CLI supported on macOS/Linux |

On macOS/Linux, tools are searched in this order:

1. The matching `MPT_GSINJECT`, `MPT_GECKOLOADER`, or `MPT_WIT` environment variable.
2. Bundled platform dependencies.
3. `~/Tools/mario-party-rom-lab/bin/`.
4. `PATH` (Unix only).
5. `~/Tools/mario-party-rom-lab/source/GeckoLoader/GeckoLoader.py` for GeckoLoader on Unix.

Install GeckoLoader’s optional runtime packages when using its source checkout:

```bash
./mariovenv/bin/python -m pip install -r requirements-injector.txt
```

WIT handles both ISO and WBFS extraction/rebuilds. Do not copy Windows `.exe` files into a Unix dependency directory. If a required tool is missing, the injector reports the tool name and expected configuration.

## ROM validation

N64 injection accepts big-endian `.z64` files and checks explicit `MP1`, `MP2`, or `MP3` labels in generated codes. For PartyPlanner64-supported NTSC-U base ROMs, MPT also recognizes these published MD5 identities:

| Game | MD5 |
|---|---|
| Mario Party | `8BC2712139FBF0C56C8EA835802C52DC` |
| Mario Party 2 | `04840612A35ECE222AFDB2DFBF926409` |
| Mario Party 3 | `76A8BBC81BC2060EC99C9645867237CC` |

Edited PP64 ROMs will not retain the base hash. They are treated as derivatives and must be tested in an emulator before distribution.

## PartyPlanner64 workflow

[PartyPlanner64](https://github.com/PartyPlanner64/PartyPlanner64) edits boards for NTSC-U Mario Party 1–3. Use PP64 to create the board, save the user-owned ROM, then use MPT to validate the target, generate compatible codes, and test a copy in an N64 emulator. PP64 requires Expansion Pak-equivalent 8 MB RAM; see the [integration research note](docs/research/partyplanner64-integration.md) for identities, symbols, events, and interoperability boundaries.

MPT does not bundle ROMs, extracted game assets, or PP64’s private editor data.

## CI

GitHub Actions runs unit tests, Python compilation, and a PyInstaller build on Ubuntu, macOS, and Windows. It uses Node.js 24-based official actions to avoid the deprecated Node.js 20 runtime. The workflow is [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Project structure

```text
codes/          Code templates
events/         UI and conversion logic
pages/          Application pages, including the injector
components/     Main window and navigation
utils/          Resource, scaling, validation, and injector helpers
assets/         Icons, logos, and UI images
dependencies/   External injection helpers
tools/          Headless CLI and test harnesses
build.py        Cross-platform PyInstaller build
```

## Contributing

Use a focused branch, run the tests and packaged build on your platform, and describe the platform and Python version in the pull request.

## License

Mario Party Toolkit is released under the [MIT License](LICENSE.md).
