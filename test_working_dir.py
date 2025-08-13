#!/usr/bin/env python3
"""
Test the working directory fix
"""

import os
import sys
from pathlib import Path

def test_working_dir_fix():
    """Test that the working directory fix works"""
    
    print("🧪 Testing Working Directory Fix")
    print("=" * 40)
    
    # Simulate the fix logic
    print(f"📁 Current directory: {Path.cwd()}")
    
    # This mimics what happens in the app
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        application_path = Path(sys.executable).parent
        print(f"📦 Running as bundled app from: {application_path}")
    else:
        # Running as script
        script_dir = Path(__file__).parent.absolute()  # NOA_image_app directory
        project_root = script_dir  # We're already in NOA_image_app
        
        # Change to project root if we're not already there
        current_dir = Path.cwd()
        if current_dir != project_root:
            print(f"📁 Would change working directory from {current_dir} to {project_root}")
            os.chdir(project_root)
            print(f"✅ Now running from: {Path.cwd()}")
        else:
            print(f"✅ Already in correct directory: {current_dir}")
    
    # Test if JSON file exists
    json_file = "keyence_vs_cephla_keyence/reclassified_pred_fixed.json"
    json_path = Path(json_file)
    
    print(f"\n📋 Testing JSON file access:")
    print(f"   File: {json_file}")
    print(f"   Exists: {json_path.exists()}")
    print(f"   Absolute path: {json_path.absolute()}")

if __name__ == "__main__":
    test_working_dir_fix()
