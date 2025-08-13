#!/usr/bin/env python3
"""
Fix JSON file to only include images that actually exist
"""

import json
import os
from pathlib import Path

def fix_missing_images():
    """Remove entries from JSON for images that don't exist"""
    
    json_file = "keyence_vs_cephla_keyence/reclassified_pred_fixed.json"
    
    print("🔧 Fixing JSON to match available images")
    print("=" * 50)
    
    # Read the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"📋 Original entries: {len(data)}")
    
    # Check which entries have existing images
    valid_entries = []
    missing_count = 0
    
    for entry in data:
        image_path = entry.get("image_path", "")
        
        if Path(image_path).exists():
            valid_entries.append(entry)
        else:
            missing_count += 1
            if missing_count <= 5:  # Show first 5 missing files
                print(f"❌ Missing: {Path(image_path).name}")
    
    if missing_count > 5:
        print(f"❌ ... and {missing_count - 5} more missing files")
    
    print(f"✅ Valid entries: {len(valid_entries)}")
    print(f"❌ Missing entries: {missing_count}")
    
    # Create backup
    backup_file = json_file.replace('.json', '_with_missing_backup.json')
    with open(backup_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"💾 Backup created: {backup_file}")
    
    # Save cleaned JSON
    with open(json_file, 'w') as f:
        json.dump(valid_entries, f, indent=2)
    
    print(f"✅ Cleaned JSON saved with {len(valid_entries)} valid entries")
    
    return len(valid_entries) > 0

if __name__ == "__main__":
    success = fix_missing_images()
    
    if success:
        print(f"\n🎉 JSON file is now clean!")
        print(f"✅ All image paths in JSON now point to existing files")
        print(f"🚀 Your app should now work without errors")
    else:
        print(f"\n❌ No valid images found!")
