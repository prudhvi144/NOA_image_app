@echo off
echo 🚀 INSTANT WINDOWS BUILD SCRIPT
echo ================================
echo.
echo This script will build the Windows .exe and place it in Distribution/Windows/
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found!
echo.

REM Install required packages
echo 📦 Installing build dependencies...
pip install PyInstaller PySide6 Pillow numpy pandas openpyxl

REM Clean previous builds
echo 🧹 Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Build the Windows executable  
echo 🔨 Building Windows executable...
python -m PyInstaller --clean --onedir --windowed --name SpermVerificationApp --hidden-import PySide6.QtCore --hidden-import PySide6.QtGui --hidden-import PySide6.QtWidgets --hidden-import PIL._tkinter_finder --hidden-import numpy --hidden-import pandas --hidden-import openpyxl --hidden-import pathlib standalone_app/sperm_verification_app.py

REM Create Distribution/Windows directory
echo 📁 Creating Distribution/Windows directory...
if not exist Distribution\Windows mkdir Distribution\Windows

REM Clean any existing Windows builds
if exist Distribution\Windows\SpermVerificationApp rmdir /s /q Distribution\Windows\SpermVerificationApp
if exist Distribution\Windows\SpermVerificationApp.exe del Distribution\Windows\SpermVerificationApp.exe
if exist Distribution\Windows\Run_SpermVerificationApp.bat del Distribution\Windows\Run_SpermVerificationApp.bat

REM Copy the build to Distribution/Windows
echo 📋 Copying build to Distribution/Windows/...
xcopy dist\SpermVerificationApp Distribution\Windows\SpermVerificationApp /E /I /Y

REM Create quick access executable
copy Distribution\Windows\SpermVerificationApp\SpermVerificationApp.exe Distribution\Windows\SpermVerificationApp.exe

REM Create launcher script
echo @echo off > Distribution\Windows\Run_SpermVerificationApp.bat
echo cd /d "%%~dp0" >> Distribution\Windows\Run_SpermVerificationApp.bat
echo SpermVerificationApp\SpermVerificationApp.exe >> Distribution\Windows\Run_SpermVerificationApp.bat
echo pause >> Distribution\Windows\Run_SpermVerificationApp.bat

echo.
echo 🎉 BUILD COMPLETED SUCCESSFULLY!
echo.
echo 📁 Windows build location:
echo    Distribution\Windows\SpermVerificationApp\SpermVerificationApp.exe
echo.
echo 🚀 Quick access:
echo    Distribution\Windows\SpermVerificationApp.exe
echo.
echo 🎯 Launcher:
echo    Distribution\Windows\Run_SpermVerificationApp.bat
echo.
echo ✅ Ready for distribution!
echo.
pause
