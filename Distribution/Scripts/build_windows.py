#!/usr/bin/env python3
"""
Windows build script for Sperm Verification App
Can be run on Windows or via cross-compilation tools
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def run_command(cmd, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        print(f"✅ Success: {cmd}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False, e.stderr

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned {dir_name}")

def build_windows():
    """Build Windows executable"""
    print("🚀 Building Windows executable...")
    
    # Clean previous builds
    clean_build()
    
    # PyInstaller command for Windows
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--onedir',
        '--windowed',
        '--name', 'SpermVerificationApp',
        '--add-data', 'standalone_app/modern_theme.py;.',
        '--add-data', 'standalone_app/test_data;test_data',
        '--hidden-import', 'PySide6.QtCore',
        '--hidden-import', 'PySide6.QtGui', 
        '--hidden-import', 'PySide6.QtWidgets',
        '--hidden-import', 'PIL._tkinter_finder',
        '--hidden-import', 'numpy',
        '--hidden-import', 'pandas',
        '--hidden-import', 'openpyxl',
        'standalone_app/sperm_verification_app.py'
    ]
    
    # Adjust for current platform
    if platform.system() != 'Windows':
        # Cross-compilation adjustments
        print("⚠️  Cross-compiling for Windows from non-Windows platform")
        cmd[4] = '--add-data=standalone_app/modern_theme.py:.'
        cmd[5] = '--add-data=standalone_app/test_data:test_data'
    
    success, output = run_command(' '.join(cmd))
    
    if not success:
        print("❌ Windows build failed!")
        return False
    
    print("✅ Windows build completed successfully!")
    
    # Check if executable was created
    exe_path = Path('dist/SpermVerificationApp/SpermVerificationApp.exe')
    if exe_path.exists():
        print(f"📁 Windows executable created: {exe_path}")
        print(f"📊 Executable size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    else:
        print("❌ Executable not found!")
        return False
    
    return True

def create_installer():
    """Create Windows installer (requires NSIS)"""
    print("📦 Creating Windows installer...")
    
    nsi_script = """
; Sperm Verification App Installer
!include "MUI2.nsh"

Name "Sperm Verification App"
OutFile "SpermVerificationApp-Installer.exe"
InstallDir "$PROGRAMFILES\\SpermVerificationApp"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Main Application" SecMain
  SetOutPath "$INSTDIR"
  File /r "dist\\SpermVerificationApp\\*"
  
  CreateDirectory "$SMPROGRAMS\\Sperm Verification App"
  CreateShortCut "$SMPROGRAMS\\Sperm Verification App\\Sperm Verification App.lnk" "$INSTDIR\\SpermVerificationApp.exe"
  CreateShortCut "$DESKTOP\\Sperm Verification App.lnk" "$INSTDIR\\SpermVerificationApp.exe"
  
  WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\*"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\\Sperm Verification App\\*"
  RMDir "$SMPROGRAMS\\Sperm Verification App"
  Delete "$DESKTOP\\Sperm Verification App.lnk"
SectionEnd
"""
    
    # Write NSIS script
    with open('installer.nsi', 'w') as f:
        f.write(nsi_script)
    
    # Try to compile with NSIS
    nsis_cmd = 'makensis installer.nsi'
    success, _ = run_command(nsis_cmd)
    
    if success:
        print("✅ Windows installer created: SpermVerificationApp-Installer.exe")
    else:
        print("⚠️  NSIS not found. To create installer:")
        print("   1. Install NSIS (https://nsis.sourceforge.io/)")
        print("   2. Run: makensis installer.nsi")
    
    return success

def main():
    """Main Windows build process"""
    print("🔨 Sperm Verification App - Windows Build")
    print(f"🖥️  Platform: {platform.system()} {platform.machine()}")
    print("=" * 50)
    
    # Build Windows executable
    if not build_windows():
        sys.exit(1)
    
    # Create installer (optional)
    print("\n📦 Creating installer...")
    create_installer()
    
    print("\n🎉 Windows build process completed!")
    print("\n📁 Output files:")
    print("   📂 Folder: dist/SpermVerificationApp/")
    print("   🎯 Executable: dist/SpermVerificationApp/SpermVerificationApp.exe")
    
    if os.path.exists('SpermVerificationApp-Installer.exe'):
        print("   📦 Installer: SpermVerificationApp-Installer.exe")
    
    print("\n💡 Distribution tips:")
    print("   • ZIP the entire dist/SpermVerificationApp/ folder")
    print("   • Include README with system requirements")
    print("   • Consider code signing for trust")

if __name__ == '__main__':
    main()
