#!/usr/bin/env python3
"""
Debug script to check path resolution issues
"""

import json
import os
from pathlib import Path

def debug_paths():
    """Debug path resolution for the JSON file"""
    
    print("🔍 Path Resolution Debug")
    print("=" * 50)
    
    # Show current working directory
    cwd = os.getcwd()
    print(f"📁 Current working directory: {cwd}")
    
    # Check JSON file
    json_file = "keyence_vs_cephla_keyence/reclassified_pred_fixed.json"
    json_path = Path(json_file)
    
    print(f"\n📋 JSON file: {json_file}")
    print(f"   Exists: {json_path.exists()}")
    print(f"   Absolute path: {json_path.absolute()}")
    
    if not json_path.exists():
        print("❌ JSON file not found from current directory!")
        print("💡 Try running from the NOA_image_app root directory")
        return
    
    # Load and check first few image paths
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        print(f"\n✅ JSON loaded: {len(data)} entries")
        
        # Check first 5 image paths
        print(f"\n🖼️  Checking first 5 image paths:")
        for i, entry in enumerate(data[:5]):
            if "image_path" in entry:
                img_path = entry["image_path"]
                img_path_obj = Path(img_path)
                
                print(f"\n   {i+1}. {img_path}")
                print(f"      Exists: {img_path_obj.exists()}")
                print(f"      Absolute: {img_path_obj.absolute()}")
                
                if not img_path_obj.exists():
                    # Try alternative paths
                    print(f"      🔍 Trying alternatives:")
                    
                    # Without ./
                    alt1 = Path(img_path.replace('./', ''))
                    print(f"         Without './': {alt1.exists()} - {alt1}")
                    
                    # From NOA_image_app root
                    alt2 = Path(f"../{img_path}")
                    print(f"         From parent: {alt2.exists()} - {alt2}")
                    
                    # Absolute construction
                    alt3 = Path(cwd) / img_path.replace('./', '')
                    print(f"         CWD + path: {alt3.exists()} - {alt3}")
        
        # Summary
        existing_count = 0
        for entry in data:
            if "image_path" in entry:
                if Path(entry["image_path"]).exists():
                    existing_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   Total entries: {len(data)}")
        print(f"   Existing images: {existing_count}")
        print(f"   Missing images: {len(data) - existing_count}")
        
        if existing_count == 0:
            print(f"\n❌ No images found!")
            print(f"💡 Possible solutions:")
            print(f"   1. Run app from NOA_image_app directory")
            print(f"   2. Update JSON paths to be relative to app location")
            print(f"   3. Use absolute paths in the app")
        else:
            print(f"\n✅ Images are accessible")
            
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")

def suggest_fixes():
    """Suggest path fixing solutions"""
    
    print(f"\n🛠️  Suggested Fixes:")
    print(f"=" * 50)
    
    cwd = os.getcwd()
    
    print(f"1. 📁 **Run from correct directory**:")
    print(f"   Current: {cwd}")
    if "standalone_app" in cwd:
        print(f"   Run from: {Path(cwd).parent}")
        print(f"   Command: cd .. && python standalone_app/sperm_verification_app.py")
    else:
        print(f"   Run from: {cwd}")
        print(f"   Command: python standalone_app/sperm_verification_app.py")
    
    print(f"\n2. 🔧 **Update app to handle relative paths better**")
    print(f"   - Add working directory management")
    print(f"   - Resolve paths relative to app location")
    
    print(f"\n3. 📋 **Alternative: Use absolute paths in JSON**")
    print(f"   - Convert back to absolute paths")
    print(f"   - But less portable across systems")

if __name__ == "__main__":
    debug_paths()
    suggest_fixes()
