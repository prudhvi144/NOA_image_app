# 🚀 Sperm Verification App - Build Instructions

## 📦 **Quick Build**

### **Prerequisites**
```bash
# Install dependencies
pip install -r requirements-build.txt

# Make build script executable (macOS/Linux)
chmod +x build.py
```

### **Build for Current Platform**
```bash
python build.py
```

---

## 🍎 **macOS Build & Code Signing**

### **✅ Current Status**
- ✅ **App Bundle Created**: `dist/SpermVerificationApp.app`
- ✅ **Basic Structure**: Proper macOS app bundle with Info.plist
- ⚠️ **Code Signing**: Requires Developer Certificate for Gatekeeper

### **🔐 Code Signing for Gatekeeper**

**Option 1: Developer ID Certificate (Recommended)**
1. **Get Apple Developer Account** ($99/year)
2. **Download Developer ID Certificate** from Apple Developer Portal
3. **Install Certificate** in Keychain Access
4. **Sign the App**:
   ```bash
   codesign --deep --force --verify --verbose \
     --sign "Developer ID Application: Your Name (TEAM_ID)" \
     --options runtime \
     dist/SpermVerificationApp.app
   ```
5. **Verify Signature**:
   ```bash
   codesign --verify --deep --strict dist/SpermVerificationApp.app
   spctl --assess --type exec dist/SpermVerificationApp.app
   ```

**Option 2: Ad-hoc Signing (Local Use)**
```bash
codesign --deep --force --sign - dist/SpermVerificationApp.app
```

**Option 3: Notarization (Full Gatekeeper)**
```bash
# After signing with Developer ID
xcrun notarytool submit dist/SpermVerificationApp.app.zip \
  --apple-id your@email.com \
  --password your-app-password \
  --team-id TEAM_ID \
  --wait

# Staple notarization
xcrun stapler staple dist/SpermVerificationApp.app
```

### **📱 Create DMG (Optional)**
```bash
hdiutil create -volname "Sperm Verification App" \
  -srcfolder dist/SpermVerificationApp.app \
  -ov -format UDZO \
  SpermVerificationApp.dmg
```

---

## 🪟 **Windows Build**

### **Cross-Compilation from macOS**
```bash
# Install Windows Python (via Wine or VM)
# Or use GitHub Actions for automated builds

# Manual PyInstaller for Windows
python -m PyInstaller --clean \
  --onedir \
  --windowed \
  --name SpermVerificationApp \
  --add-data "standalone_app/modern_theme.py:." \
  --add-data "standalone_app/test_data:test_data" \
  standalone_app/sperm_verification_app.py
```

### **Native Windows Build**
```cmd
REM On Windows machine
pip install -r requirements-build.txt
python build.py
```

### **Windows Installer (Optional)**
- **NSIS**: Create professional installer
- **Inno Setup**: Alternative installer creator
- **WiX Toolset**: MSI installer

---

## 🔧 **Build Configuration**

### **Customize build_config.spec**
```python
# Add icon
icon='path/to/icon.ico'  # Windows
icon='path/to/icon.icns'  # macOS

# Exclude modules
excludes=['tkinter', 'unittest']

# Additional data files
datas=[('data/', 'data/')]
```

### **Bundle Identifier**
```python
# In build_config.spec for macOS
bundle_identifier='com.yourcompany.spermverificationapp'
```

---

## 📁 **Output Structure**

### **macOS**
```
dist/
├── SpermVerificationApp.app/     # macOS App Bundle
│   ├── Contents/
│   │   ├── MacOS/
│   │   │   └── SpermVerificationApp  # Executable
│   │   ├── Resources/            # App resources
│   │   ├── Frameworks/           # Dependencies
│   │   └── Info.plist           # App metadata
│   └── ...
└── SpermVerificationApp/         # Standalone folder version
    ├── SpermVerificationApp      # Executable
    └── _internal/               # Dependencies
```

### **Windows**
```
dist/
└── SpermVerificationApp/
    ├── SpermVerificationApp.exe  # Executable
    └── _internal/               # Dependencies
```

---

## 🚀 **Distribution**

### **macOS**
1. **Direct Distribution**: Share `.app` bundle
2. **DMG**: Create disk image for easy installation
3. **App Store**: Submit through Xcode (requires additional setup)

### **Windows**
1. **ZIP**: Compress executable folder
2. **Installer**: Use NSIS/Inno Setup for professional installation
3. **Store**: Microsoft Store submission

---

## 🐛 **Troubleshooting**

### **Common Issues**
- **Missing Modules**: Add to `hiddenimports` in spec file
- **Data Files**: Ensure paths are correct in `datas`
- **Permissions**: App may need camera/microphone permissions
- **Antivirus**: Some antivirus may flag unsigned executables

### **Testing**
```bash
# Test the built app
./dist/SpermVerificationApp.app/Contents/MacOS/SpermVerificationApp
```

---

## 🎯 **Automated Builds (GitHub Actions)**

Create `.github/workflows/build.yml` for automatic cross-platform builds:
- macOS builds on `macos-latest`
- Windows builds on `windows-latest`
- Automatic releases with GitHub Actions

---

**🎉 Your app is now ready for distribution!**
