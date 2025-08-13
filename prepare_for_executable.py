#!/usr/bin/env python3
"""
Prepare JSON file for executable distribution
Convert absolute paths to be relative to where the executable will be placed
"""

import json
import os
from pathlib import Path

def prepare_json_for_executable():
    """Convert JSON paths to be relative to executable location"""
    
    json_file = "keyence_vs_cephla_keyence/reclassified_pred_fixed.json"
    
    print("🚀 Preparing JSON for Executable Distribution")
    print("=" * 60)
    
    # Read the JSON file
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} entries")
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        return False
    
    # Create backup
    backup_file = json_file.replace('.json', '_absolute_backup.json')
    try:
        with open(backup_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️  Could not create backup: {e}")
    
    # Convert absolute paths to relative to app directory
    current_dir = Path.cwd()
    entries_updated = 0
    
    for entry in data:
        if "image_path" in entry:
            old_path = Path(entry["image_path"])
            
            try:
                # Make path relative to current directory (app root)
                relative_path = old_path.relative_to(current_dir)
                entry["image_path"] = str(relative_path)
                entries_updated += 1
            except ValueError:
                # Path is not within current directory, keep as absolute
                print(f"⚠️  Keeping absolute path: {old_path}")
    
    print(f"🔄 Updated {entries_updated} paths to relative")
    
    # Save the updated JSON
    try:
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved JSON with relative paths")
        
        # Show example
        if data:
            print(f"\n📝 Example relative path:")
            print(f"   {data[0]['image_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
        return False

def create_distribution_instructions():
    """Create instructions for users"""
    
    instructions = """# 🚀 Sperm Verification App - Distribution Instructions

## 📦 For Users - How to Use

### 🔽 What You'll Receive:
```
📁 SpermVerificationApp-Package/
├── 🖥️  SpermVerificationApp.exe (or .app)     # The main application
├── 📁 keyence_vs_cephla_keyence/              # Data folder with images
│   ├── 📁 Patient_2/images/                   # Image files
│   └── 📋 reclassified_pred_fixed.json        # Annotations file
└── 📖 README.md                               # This file
```

### 🎯 Installation (Super Simple):
1. **Download** the SpermVerificationApp-Package folder
2. **Place it anywhere** on your computer (Desktop, Documents, etc.)
3. **Double-click** the SpermVerificationApp executable
4. **Done!** The app automatically finds the data folder

### 🎮 How to Use:
1. **Start the app** by double-clicking the executable
2. **Load data** by clicking "🔬 Load Data"
3. **Navigate** to the `keyence_vs_cephla_keyence` folder (should open automatically)
4. **Select** the `reclassified_pred_fixed.json` file
5. **Start verifying** sperm cells!

### 📁 Folder Structure Rules:
- ✅ **Keep the data folder next to the executable**
- ✅ **You can move the entire package anywhere**
- ❌ **Don't separate the executable from the data folder**

### 🔧 If Images Don't Load:
1. Make sure the `keyence_vs_cephla_keyence` folder is next to the app
2. Check that image files exist in `Patient_2/images/`
3. Try "Quick Load (100)" for faster testing

### 💻 Platform Notes:
- **Windows**: Run `SpermVerificationApp.exe`
- **macOS**: Run `SpermVerificationApp.app` 
- **Security warnings**: Click "More info" → "Run anyway" (Windows) or Right-click → Open (macOS)

---
**🎉 That's it! The app will automatically find your data files wherever you place the folder.**
"""
    
    with open("DISTRIBUTION_README.md", "w") as f:
        f.write(instructions)
    
    print("📖 Created DISTRIBUTION_README.md")

def main():
    """Main preparation process"""
    
    # Convert JSON paths
    success = prepare_json_for_executable()
    
    if success:
        # Create user instructions
        create_distribution_instructions()
        
        print(f"\n🎉 Ready for Distribution!")
        print(f"\n📦 Distribution Structure:")
        print(f"   📁 YourAppFolder/")
        print(f"   ├── 🖥️  SpermVerificationApp.exe (your built app)")
        print(f"   ├── 📁 keyence_vs_cephla_keyence/ (this data folder)")
        print(f"   └── 📖 DISTRIBUTION_README.md (user instructions)")
        
        print(f"\n✅ User Benefits:")
        print(f"   • Can place folder anywhere on their system")
        print(f"   • App automatically finds data folder")
        print(f"   • No complex setup required")
        print(f"   • Works immediately after download")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Build your app with PyInstaller")
        print(f"   2. Copy the keyence_vs_cephla_keyence folder next to the .exe")
        print(f"   3. Include DISTRIBUTION_README.md")
        print(f"   4. ZIP and share with users!")

if __name__ == "__main__":
    main()
