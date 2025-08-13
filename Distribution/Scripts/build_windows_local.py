#!/usr/bin/env python3
"""
Windows Build Script for Sperm Verification App
Run this script on a Windows machine to create the Windows executable
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def build_windows():
    """Build Windows executable using PyInstaller"""
    
    print("🔨 Building Windows executable...")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # PyInstaller command for Windows
    cmd = [
        "python", "-m", "PyInstaller",
        "--clean",
        "--onedir",
        "--windowed",
        "--name", "SpermVerificationApp",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui", 
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "numpy",
        "--hidden-import", "pandas",
        "--hidden-import", "openpyxl",
        "--hidden-import", "pathlib",
        "standalone_app/sperm_verification_app.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        print(result.stdout)
        
        # Copy to Distribution/Windows folder (exactly like Mac build process)
        dist_windows = Path("Distribution/Windows")
        dist_windows.mkdir(parents=True, exist_ok=True)
        
        # Remove any existing Windows build
        existing_builds = list(dist_windows.glob("SpermVerificationApp*"))
        for build in existing_builds:
            if build.is_dir():
                shutil.rmtree(build)
            else:
                build.unlink()
        
        # Copy the entire SpermVerificationApp folder to Distribution/Windows
        src_folder = Path("dist/SpermVerificationApp")
        dst_folder = dist_windows / "SpermVerificationApp"
        
        if dst_folder.exists():
            shutil.rmtree(dst_folder)
        
        shutil.copytree(src_folder, dst_folder)
        
        # Also create a direct executable copy for easier access
        exe_src = src_folder / "SpermVerificationApp.exe"
        exe_dst = dist_windows / "SpermVerificationApp.exe"
        
        if exe_src.exists():
            shutil.copy2(exe_src, exe_dst)
            print(f"✅ Direct executable copied to: {exe_dst}")
        
        print(f"✅ Complete Windows build copied to: {dst_folder}")
        print(f"✅ Main executable location: {dst_folder}/SpermVerificationApp.exe")
        print(f"✅ Quick access executable: {exe_dst}")
        
        # Create a simple launcher script
        launcher_script = dist_windows / "Run_SpermVerificationApp.bat"
        with open(launcher_script, 'w') as f:
            f.write('@echo off\n')
            f.write('cd /d "%~dp0"\n')
            f.write('SpermVerificationApp\\SpermVerificationApp.exe\n')
            f.write('pause\n')
        
        print(f"✅ Launcher script created: {launcher_script}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "PyInstaller",
        "PySide6", 
        "Pillow",
        "numpy",
        "pandas",
        "openpyxl",
        "pathlib"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies found!")
    return True

if __name__ == "__main__":
    print("🚀 Windows Build Script for Sperm Verification App")
    print("=" * 50)
    
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        sys.exit(1)
    
    if build_windows():
        print("\n🎉 Build completed successfully!")
        print("\n📁 Windows build saved to Distribution/Windows/:")
        print("Distribution/Windows/")
        print("├── SpermVerificationApp/")
        print("│   ├── SpermVerificationApp.exe      ← Main executable")
        print("│   └── _internal/                    ← Required libraries")
        print("├── SpermVerificationApp.exe          ← Quick access copy")
        print("└── Run_SpermVerificationApp.bat      ← Double-click launcher")
        
        print("\n📦 Complete Distribution structure:")
        print("Distribution/")
        print("├── Mac/           ← macOS app")
        print("├── Windows/       ← Windows exe (just built!)")
        print("├── Data/          ← Sample data")
        print("└── Scripts/       ← Source code")
        
        print("\n💡 Distribution options:")
        print("1. Share entire 'Distribution' folder (Mac + Windows + Data)")
        print("2. Share just 'Distribution/Windows' folder for Windows users")
        print("3. Users can double-click 'Run_SpermVerificationApp.bat' to start")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)
