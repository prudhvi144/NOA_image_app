#!/usr/bin/env python3
"""
Add ./ prefix to relative paths in reclassified_pred_fixed.json
This ensures paths work correctly on any user's system
"""

import json
import os
from pathlib import Path

def fix_json_paths():
    """Add ./ prefix to relative paths in the JSON file"""
    
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
    backup_file = json_file.replace('.json', '_before_dotslash.json')
    try:
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")
    
    # Add ./ prefix to paths
    entries_updated = 0
    
    for entry in data:
        if "image_path" in entry:
            old_path = entry["image_path"]
            # Only add ./ if it doesn't already start with ./ or /
            if not old_path.startswith('./') and not old_path.startswith('/'):
                # Add ./ prefix
                new_path = "./" + old_path
                entry["image_path"] = new_path
                entries_updated += 1
    
    print(f"🔄 Updated {entries_updated} image paths with ./ prefix")
    
    # Save the updated JSON
    try:
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved updated JSON to {json_file}")
        
        # Show example of change
        if data:
            print(f"\n📝 Example path change:")
            print(f"   Before: keyence_vs_cephla_keyence/...")
            print(f"   After:  {data[0]['image_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding ./ prefix to relative paths")
    print("=" * 50)
    
    success = fix_json_paths()
    
    if success:
        print("\n🎉 Path conversion completed successfully!")
        print("\n💡 The JSON file now uses proper relative paths with ./ prefix")
        print("   Example: ./keyence_vs_cephla_keyence/Patient_2/images/...")
        print("\n🚀 This ensures compatibility across different user systems!")
    else:
        print("\n❌ Path conversion failed!")
