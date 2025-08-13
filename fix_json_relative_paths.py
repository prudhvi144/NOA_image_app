#!/usr/bin/env python3
"""
Convert absolute paths to relative paths in reclassified_pred_fixed.json
"""

import json
import os
from pathlib import Path

def fix_json_paths():
    """Convert absolute paths to relative paths in the JSON file"""
    
    json_file = "keyence_vs_cephla_keyence/reclassified_pred_fixed.json"
    
    print(f"🔧 Processing {json_file}...")
    
    # Read the JSON file
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} entries")
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        return False
    
    # Create backup
    backup_file = json_file.replace('.json', '_backup.json')
    try:
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")
    
    # Convert paths
    absolute_prefix = "/Users/prudhvi/Desktop/NOA_image_app/"
    entries_updated = 0
    
    for entry in data:
        if "image_path" in entry:
            old_path = entry["image_path"]
            if old_path.startswith(absolute_prefix):
                # Convert to relative path
                relative_path = old_path.replace(absolute_prefix, "")
                entry["image_path"] = relative_path
                entries_updated += 1
    
    print(f"🔄 Updated {entries_updated} image paths")
    
    # Save the updated JSON
    try:
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved updated JSON to {json_file}")
        
        # Show example of change
        if data:
            print(f"\n📝 Example path change:")
            print(f"   Before: {absolute_prefix}keyence_vs_cephla_keyence/...")
            print(f"   After:  {data[0]['image_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Converting absolute paths to relative paths")
    print("=" * 50)
    
    success = fix_json_paths()
    
    if success:
        print("\n🎉 Path conversion completed successfully!")
        print("\n💡 The JSON file now uses relative paths starting from the app root directory")
        print("   Example: keyence_vs_cephla_keyence/Patient_2/images/...")
    else:
        print("\n❌ Path conversion failed!")
