#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "$0")" && pwd)"
python_command="${PYTHON:-python3}"

"$python_command" -m venv "$project_root/mariovenv"
"$project_root/mariovenv/bin/python" -m pip install --upgrade pip
"$project_root/mariovenv/bin/python" -m pip install -r "$project_root/requirements.txt"

echo "Setup complete. Run: $project_root/mariovenv/bin/python $project_root/main.py"
