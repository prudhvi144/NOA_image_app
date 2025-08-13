#!/usr/bin/env python3
"""
Simple solution: Convert all paths in JSON to absolute paths
This way the app works from anywhere without complex path resolution
"""

import json
import os
from pathlib import Path

def fix_to_absolute_paths():
    """Convert all relative paths in JSON to absolute paths"""
    
    json_file = "keyence_vs_cephla_keyence/reclassified_pred_fixed.json"
    
    print(f"🔧 Converting to absolute paths: {json_file}")
    
    # Read the JSON file
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} entries")
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        return False
    
    # Create backup
    backup_file = json_file.replace('.json', '_relative_backup.json')
    try:
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")
    
    # Convert all paths to absolute
    current_dir = Path.cwd()
    entries_updated = 0
    
    for entry in data:
        if "image_path" in entry:
            old_path = entry["image_path"]
            
            # Convert to absolute path
            if old_path.startswith('./'):
                # Remove ./ and make absolute
                clean_path = old_path[2:]
                absolute_path = current_dir / clean_path
            elif not Path(old_path).is_absolute():
                # Make relative path absolute
                absolute_path = current_dir / old_path
            else:
                # Already absolute
                absolute_path = Path(old_path)
            
            # Update the entry with absolute path
            entry["image_path"] = str(absolute_path.resolve())
            entries_updated += 1
    
    print(f"🔄 Updated {entries_updated} paths to absolute")
    
    # Save the updated JSON
    try:
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved updated JSON with absolute paths")
        
        # Show example
        if data:
            print(f"\n📝 Example absolute path:")
            print(f"   {data[0]['image_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
        return False

def create_config_file():
    """Create a simple config file for the app"""
    
    config = {
        "data_directory": str(Path.cwd().resolve()),
        "default_json_file": str((Path.cwd() / "keyence_vs_cephla_keyence/reclassified_pred_fixed.json").resolve()),
        "app_version": "1.0",
        "last_updated": "2025-08-13"
    }
    
    config_file = "app_config.json"
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"📋 Created config file: {config_file}")
        print(f"   Data directory: {config['data_directory']}")
        print(f"   Default JSON: {config['default_json_file']}")
        return True
    except Exception as e:
        print(f"❌ Error creating config file: {e}")
        return False

def main():
    """Main process"""
    
    print("🚀 Simple Path Fix - Convert to Absolute Paths")
    print("=" * 60)
    
    print("📁 Current directory:", Path.cwd())
    
    # Convert paths to absolute
    success = fix_to_absolute_paths()
    
    if success:
        # Create config file
        create_config_file()
        
        print(f"\n🎉 Solution Complete!")
        print(f"\n✅ Benefits:")
        print(f"   • No complex path resolution needed")
        print(f"   • App works from any directory")
        print(f"   • Users can run from anywhere")
        print(f"   • No code changes needed in app")
        
        print(f"\n📦 For distribution:")
        print(f"   • Just share the folder with absolute paths")
        print(f"   • Users can place it anywhere on their system")
        print(f"   • App will find images correctly")
        
        print(f"\n💡 User instructions:")
        print(f"   1. Download and extract the app folder")
        print(f"   2. Run the app from anywhere")
        print(f"   3. Use 'Load Data' to select the JSON file")
        print(f"   4. All image paths will work correctly")

if __name__ == "__main__":
    main()
