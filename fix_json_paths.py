#!/usr/bin/env python3
"""
Script to fix image paths in the reclassified_pred.json file.
Changes paths from /nfs/tier3/projects/NOA_V2/data/keyence_vs_cephla_keyence/
to /Users/prudhvi/Desktop/NOA_image_app/keyence_vs_cephla_keyence/
"""

import json
import os
from pathlib import Path

def fix_json_paths():
    # Input and output paths
    input_json = "/Users/prudhvi/Desktop/NOA_image_app/keyence_vs_cephla_keyence/reclassified_pred.json"
    output_json = "/Users/prudhvi/Desktop/NOA_image_app/keyence_vs_cephla_keyence/reclassified_pred_fixed.json"
    
    # Path mappings
    old_base_path = "/nfs/tier3/projects/NOA_V2/data/keyence_vs_cephla_keyence/"
    new_base_path = "/Users/prudhvi/Desktop/NOA_image_app/keyence_vs_cephla_keyence/"
    
    print("🔧 Loading JSON file...")
    with open(input_json, 'r') as f:
        data = json.load(f)
    
    print(f"📊 Found {len(data)} entries in JSON file")
    
    # Count of processed entries
    fixed_count = 0
    missing_files = 0
    
    print("🔄 Fixing image paths...")
    for entry in data:
        old_path = entry['image_path']
        
        # Replace the base path
        if old_path.startswith(old_base_path):
            new_path = old_path.replace(old_base_path, new_base_path)
            entry['image_path'] = new_path
            
            # Check if the file actually exists
            if os.path.exists(new_path):
                fixed_count += 1
            else:
                missing_files += 1
                print(f"⚠️  Missing file: {os.path.basename(new_path)}")
        else:
            print(f"⚠️  Unexpected path format: {old_path}")
    
    print(f"✅ Fixed {fixed_count} paths")
    print(f"⚠️  {missing_files} files missing")
    
    print("💾 Saving fixed JSON file...")
    with open(output_json, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"🎉 Successfully saved fixed JSON to: {output_json}")
    
    # Also create a backup of the original and replace it
    backup_path = input_json + ".backup"
    if not os.path.exists(backup_path):
        print("💾 Creating backup of original JSON...")
        import shutil
        shutil.copy2(input_json, backup_path)
    
    print("🔄 Replacing original JSON with fixed version...")
    import shutil
    shutil.copy2(output_json, input_json)
    
    print("✅ All done! JSON file has been updated with correct paths.")
    return fixed_count, missing_files

if __name__ == "__main__":
    fixed, missing = fix_json_paths()
    print(f"\n📈 Summary:")
    print(f"   ✅ Fixed: {fixed} entries")
    print(f"   ⚠️  Missing: {missing} files")
