# Sperm Verification App - Distribution Package

## 📁 Folder Structure

### **Mac/** 
Contains the macOS application ready to run:
- `SpermVerificationApp.app` - Double-click to run on Mac

### **Windows/** 
Contains the Windows application (will be added after Windows build):
- `SpermVerificationApp.exe` - Double-click to run on Windows

### **Data/** 
Contains sample data and JSON files:
- `keyence_vs_cephla_keyence/` - Sample dataset with images and annotations
- Use this as a reference for your own data structure

### **Scripts/** 
Contains source code and build scripts:
- `standalone_app/` - Complete Python source code
- `build.py` - Build script for creating executables
- `build_config.spec` - PyInstaller configuration
- `requirements.txt` - Python dependencies

## 🚀 Quick Start

### For Mac Users:
1. Open the `Mac/` folder
2. Double-click `SpermVerificationApp.app`
3. When prompted, select your data root directory
4. Choose your JSON annotation file
5. Start annotating!

### For Windows Users:
1. Open the `Windows/` folder  
2. Double-click `SpermVerificationApp.exe`
3. Follow the same steps as Mac users

## 📋 How to Use Your Own Data

1. **Prepare your data structure:**
   ```
   YourDataFolder/
   ├── annotations.json          # Your annotation file
   ├── Patient_X/
   │   └── images/
   │       ├── image1.tif
   │       ├── image2.tif
   │       └── ...
   └── Patient_Y/
       └── images/
           ├── image1.tif
           └── ...
   ```

2. **Launch the app:**
   - Run the appropriate executable for your platform
   - When prompted, select `YourDataFolder/` as the root directory
   - Select your `annotations.json` file
   - The app will automatically find all referenced images

3. **JSON Format:**
   Your JSON should contain detection data with image paths relative to the root directory:
   ```json
   [
     {
       "image_path": "Patient_X/images/image1.tif",
       "detections": [
         {
           "bbox": [x, y, width, height],
           "confidence": 0.95
         }
       ]
     }
   ]
   ```

## 🛠️ Development

To modify or rebuild the application:

1. **Install Python dependencies:**
   ```bash
   cd Scripts/
   pip install -r requirements.txt
   ```

2. **Run from source:**
   ```bash
   cd Scripts/standalone_app/
   python sperm_verification_app.py
   ```

3. **Build new executable:**
   ```bash
   cd Scripts/
   python build.py
   ```

## ⚙️ Features

- **Modern UI:** Clean, professional interface with smooth animations
- **Flexible Data Loading:** Works with any properly structured dataset
- **Interactive Annotation:** Click to confirm/unconfirm sperm detections
- **Real-time Preview:** Hover over thumbnails to see full image with bounding boxes
- **Session Timing:** Track annotation time and productivity
- **Excel Export:** Export results with detailed timing information
- **Confidence Filtering:** Filter detections by confidence threshold
- **Cross-platform:** Identical experience on Mac and Windows

## 🔧 System Requirements

- **Mac:** macOS 10.14 or later
- **Windows:** Windows 10 or later
- **Memory:** 4GB RAM recommended
- **Storage:** 100MB for app + space for your data

## 📞 Support

For technical support or questions about the application, please refer to the source code in the `Scripts/` folder or contact your development team.

---

**Version:** 1.0  
**Built with:** Python, PySide6, PyInstaller  
**Last Updated:** $(date)
