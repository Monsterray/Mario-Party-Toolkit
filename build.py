# ============================================
# Mario Party Toolkit
# Author: Tabitha Hanegan (tabitha@tabs.gay)
# Date: 09/30/2025
# License: MIT
# ============================================

"""
Build script for Mario Party Toolkit
Creates standalone executables for different platforms
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def install_dependencies(project_root):
    """Install project dependencies if the build environment is incomplete"""
    try:
        for module in ("PyInstaller", "PyQt5", "qfluentwidgets", "PIL", "requests", "darkdetect", "pyperclip"):
            __import__(module)
        print("Project dependencies already installed")
    except ImportError:
        print("Installing project dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(project_root / "requirements.txt")
        ])

def build_executable():
    """Build the executable for the current platform"""
    system = platform.system().lower()
    project_root = Path(__file__).resolve().parent
    
    # Platform-specific settings
    if system == "windows":
        icon = project_root / "assets/icons/diceBlock.ico"
        output_name = "MarioPartyToolkit.exe"
    elif system == "darwin":  # macOS
        icon = project_root / "assets/icons/diceBlock.icns"
        output_name = "MarioPartyToolkit"
    else:  # Linux
        icon = project_root / "assets/icons/diceBlock.png"
        output_name = "MarioPartyToolkit"
    
    # Check if icon exists
    if not os.path.exists(icon):
        print(f"Warning: Icon file {icon} not found, building without icon")
        icon = ""
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", output_name,
        "--distpath", str(project_root / "dist"),
        "--workpath", str(project_root / "build"),
        "--specpath", str(project_root / "build"),
        "--add-data", f"{project_root / 'assets'}{os.pathsep}assets",
        "--add-data", f"{project_root / 'dependencies'}{os.pathsep}dependencies"
    ]
    
    if icon:
        cmd.extend(["--icon", str(icon)])
    
    cmd.append(str(project_root / "main.py"))
    
    print(f"Building for {system}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print(f"Build successful! Executable created in dist/{output_name}")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}")
        sys.exit(1)

def main():
    """Main build function"""
    print("Mario Party Toolkit - Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    project_root = Path(__file__).resolve().parent
    if not (project_root / "main.py").exists():
        print("Error: main.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Install PyInstaller if needed
    install_dependencies(project_root)
    
    # Build the executable
    build_executable()
    
    print("\nBuild completed successfully!")

if __name__ == "__main__":
    main()
