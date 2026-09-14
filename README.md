# Mario Party Toolkit

Mario Party Toolkit is a PyQt5 desktop application for generating gameplay-modification codes for Mario Party 1–9 and Mario Party DS.

## Features

- Coin, star, item, shop, minigame, handicap, and board-specific modifiers
- N64 GameShark-style and GameCube/Wii Gecko-style code generation
- Code injection interface for supported ROM and disc-image workflows
- Light and dark themes using PyQt-Fluent-Widgets
- Windows, macOS, and Linux application builds with PyInstaller

Use game images dumped from copies you own. Keep an unmodified backup and apply generated codes to a working copy.

## Requirements

- Python 3.10 or newer
- A working `python3` command
- macOS, Windows, or Linux

Python packages are listed in `requirements.txt` and should be installed inside a virtual environment.

## macOS setup

From Terminal, open the project directory and run:

```bash
cd /path/to/Mario-Party-Toolkit
./install_macos_deps.sh
./mariovenv/bin/python main.py
```

The setup script creates `mariovenv` and installs all Python dependencies into it. It does not modify the Homebrew or system Python installation.

To perform the same setup manually:

```bash
python3 -m venv mariovenv
./mariovenv/bin/python -m pip install --upgrade pip
./mariovenv/bin/python -m pip install -r requirements.txt
./mariovenv/bin/python main.py
```

If `python3` is unavailable, install a current Python release from [python.org](https://www.python.org/downloads/macos/) or Homebrew, then repeat the commands above.

## Windows and Linux setup

Create a virtual environment, activate it using the platform's normal command, and install the requirements:

```bash
python -m venv mariovenv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

When the environment is not activated, invoke its Python executable directly as shown in the macOS example.

## Building

### macOS

```bash
./build-macos.sh
```

The build outputs are:

- `dist/MarioPartyToolkit`
- `dist/MarioPartyToolkit.app`

The standalone executable can be launched from Terminal when diagnosing startup errors:

```bash
./dist/MarioPartyToolkit
```

### Any supported platform

Run the build using the virtual environment's Python:

```bash
python build.py
```

`build.py` resolves assets relative to the project directory, includes `assets/` and `dependencies/`, and uses the active Python interpreter's PyInstaller installation.

## macOS troubleshooting

### `ModuleNotFoundError: PyQt5`

Install the requirements with the same virtual-environment Python used for the build:

```bash
./mariovenv/bin/python -m pip install -r requirements.txt
```

### `ModuleNotFoundError: tkinter`

Current versions of the toolkit use Qt file dialogs and do not require Tk. Pull the latest source and rebuild; installing Tk should not be necessary.

### Missing icon or assets

Build from the current source using `build.py` or `build-macos.sh`. Both scripts resolve absolute asset paths and bundle the complete `assets/` directory.

### Inspecting a packaged startup failure

Run `./dist/MarioPartyToolkit` in Terminal and copy the complete traceback. Running the executable directly is more useful for diagnosis than double-clicking the `.app` bundle.

## Project structure

```text
codes/          Generated-code templates for each game
events/         UI event and conversion logic
pages/          Application pages and the injector interface
components/     Main window and navigation components
utils/          Resource, scaling, and randomization helpers
assets/         Icons, logos, and UI images
dependencies/   External injection helpers
build.py        Cross-platform PyInstaller build
```

## Contributing

1. Fork the repository.
2. Create a focused branch.
3. Run the application from a clean virtual environment.
4. Build and launch the packaged executable for your platform.
5. Submit a pull request describing the platform and Python version tested.

## License

Mario Party Toolkit is released under the [MIT License](LICENSE.md).
