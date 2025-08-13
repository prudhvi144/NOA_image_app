#!/usr/bin/env python3
"""
Debug script to test path resolution in built app
"""

import os
import sys
from pathlib import Path

def debug_paths():
    print("=== PATH DEBUGGING ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {__file__}")
    print(f"sys.argv[0]: {sys.argv[0]}")
    print(f"sys.executable: {sys.executable}")
    
    # Check if we're in a PyInstaller bundle
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        print(f"PyInstaller bundle detected!")
        print(f"sys._MEIPASS: {sys._MEIPASS}")
        print(f"sys.frozen: {sys.frozen}")
    
    # Check for keyence folder
    keyence_path = Path("keyence_vs_cephla_keyence")
    print(f"Looking for: {keyence_path.absolute()}")
    print(f"Exists: {keyence_path.exists()}")
    
    if keyence_path.exists():
        print(f"Contents: {list(keyence_path.iterdir())}")
    
    # Check different potential locations
    potential_paths = [
        Path("keyence_vs_cephla_keyence"),
        Path("../keyence_vs_cephla_keyence"),
        Path("../../keyence_vs_cephla_keyence"),
        Path(sys.executable).parent / "keyence_vs_cephla_keyence",
    ]
    
    if hasattr(sys, '_MEIPASS'):
        potential_paths.append(Path(sys._MEIPASS) / "keyence_vs_cephla_keyence")
    
    print("\n=== CHECKING POTENTIAL PATHS ===")
    for path in potential_paths:
        print(f"{path.absolute()}: {path.exists()}")

if __name__ == "__main__":
    debug_paths()
