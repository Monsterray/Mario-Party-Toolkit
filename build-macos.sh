#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "$0")" && pwd)"
venv_python="$project_root/mariovenv/bin/python"

if [[ ! -x "$venv_python" ]]; then
    echo "Virtual environment not found. Run ./install_macos_deps.sh first."
    exit 1
fi

mkdir -p "$project_root/build/pyinstaller-config"
PYINSTALLER_CONFIG_DIR="$project_root/build/pyinstaller-config" "$venv_python" "$project_root/build.py"
