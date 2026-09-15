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

The JSON report distinguishes ROM-header parsing from gameplay verification. Mupen may still stop when its OpenGL context cannot be created; that is an emulator/display limitation, not proof that the ROM or code is wrong. On an Intel Mac, verify native tool architecture with `file`; the bundled macOS `GSInject` currently requires an arm64 injector or an Intel-compatible replacement configured with `MPT_GSINJECT`.

## Injector backends

The injector uses these tools:

| Input | Backend | Current status |
|---|---|---|
| N64 `.z64` | `GSInject` | Windows binary bundled; no verified macOS/Linux port yet |
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
