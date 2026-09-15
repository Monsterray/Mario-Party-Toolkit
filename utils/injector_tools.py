"""Locate platform-specific injector tools without assuming a working directory."""

from pathlib import Path
import os
import shutil
import sys


TOOL_ENV_NAMES = {
    "GSInject": "MPT_GSINJECT",
    "GeckoLoader": "MPT_GECKOLOADER",
    "wit": "MPT_WIT",
    "pyisotools": "MPT_PYISOTOOLS",
}


def resolve_tool(name, resource_loader):
    """Return argv for a tool, including a Python argv for GeckoLoader.py."""
    env_name = TOOL_ENV_NAMES.get(name)
    if env_name and os.environ.get(env_name):
        return [os.environ[env_name]]

    platform_name = "win32" if sys.platform == "win32" else "darwin"
    suffix = ".exe" if sys.platform == "win32" else ""
    bundled = Path(resource_loader(f"dependencies/{platform_name}/{name}{suffix}"))
    if bundled.is_file():
        return [str(bundled)]

    user_root = Path.home() / "Tools" / "mario-party-rom-lab"
    candidates = [user_root / "bin" / f"{name}{suffix}"]
    if sys.platform != "win32":
        system_tool = shutil.which(name)
        if system_tool:
            candidates.append(Path(system_tool))

    for candidate in candidates:
        if candidate.is_file():
            return [str(candidate)]

    if name == "GeckoLoader" and sys.platform != "win32":
        source_script = user_root / "source" / "GeckoLoader" / "GeckoLoader.py"
        if source_script.is_file():
            return [sys.executable, str(source_script)]

    raise FileNotFoundError(
        f"Required injector tool is not installed: {name}. "
        f"Set {env_name or 'the matching MPT_* variable'} or install it in "
        f"{user_root / 'bin'}."
    )
