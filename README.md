# Mario Party Toolkit

Mario Party Toolkit generates gameplay-modification codes for Mario Party 1–9 and Mario Party DS. It supports N64 GameShark-style codes, GameCube/Wii Gecko-style codes, and platform-specific packaging with PyInstaller.

Use images dumped from games you own. Keep the original image unchanged and test generated output on a copy.

## Setup

Requirements: Python 3.10 or newer on macOS, Windows, or Linux.

Create a virtual environment, install dependencies, and run the application with that environment’s Python:

```bash
python3 -m venv mariovenv
./mariovenv/bin/python -m pip install --upgrade pip
./mariovenv/bin/python -m pip install -r requirements.txt
./mariovenv/bin/python main.py
```

On Windows, use `python` and `mariovenv\Scripts\python.exe` instead. macOS users can run `./install_macos_deps.sh`, which performs the same setup without changing the system Python installation.

## Build

Run the build with the virtual environment’s Python:

```bash
./mariovenv/bin/python build.py
```

On macOS, `./build-macos.sh` is equivalent when `mariovenv` already exists. Builds are written to `dist/`; the macOS build also creates `dist/MarioPartyToolkit.app`.

For packaged-app diagnosis, run the standalone executable from Terminal:

```bash
./dist/MarioPartyToolkit
```

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

GitHub Actions runs unit tests, Python compilation, and a PyInstaller build on Ubuntu, macOS, and Windows. The workflow is [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Project structure

```text
codes/          Code templates
events/         UI and conversion logic
pages/          Application pages, including the injector
components/     Main window and navigation
utils/          Resource, scaling, validation, and injector helpers
assets/         Icons, logos, and UI images
dependencies/   External injection helpers
build.py        Cross-platform PyInstaller build
```

## Contributing

Use a focused branch, run the tests and packaged build on your platform, and describe the platform and Python version in the pull request.

## License

Mario Party Toolkit is released under the [MIT License](LICENSE.md).
