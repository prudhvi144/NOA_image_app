#!/usr/bin/env python3
"""
Prepare the JSON file for distribution by converting absolute paths to relative
Run this before sharing with users
"""

import json
from pathlib import Path

def convert_for_distribution():
    """Convert absolute paths back to relative for distribution"""
    
    json_file = "keyence_vs_cephla_keyence/reclassified_pred_fixed.json"
    
    print("📦 Preparing for distribution...")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Convert absolute paths back to relative
    base_path = Path.cwd()
    
    for entry in data:
        if "image_path" in entry:
            abs_path = Path(entry["image_path"])
            try:
                # Make relative to current directory
                rel_path = abs_path.relative_to(base_path)
                entry["image_path"] = str(rel_path)
            except ValueError:
                # Path is not relative to base, keep as is
                pass
    
    # Save distribution version
    dist_file = json_file.replace('.json', '_distribution.json')
    with open(dist_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Created distribution file: {dist_file}")
    print("📤 Share this entire folder with users")
    print("🎯 They can place it anywhere and it will work!")

if __name__ == "__main__":
    convert_for_distribution()
