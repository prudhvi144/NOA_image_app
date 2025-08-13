# Sperm Cell Verification Tool

A standalone GUI application for manually verifying neural network predictions of sperm cell detections in microscopy images.

## Features

- **Load Annotations**: Load JSON files containing image paths and bounding box coordinates
- **Grid View**: Thumbnail grid of detected cells for quick overview
- **Detail View**: Hover over thumbnails to see larger, padded crops in the viewfinder
- **Confirmation System**: Click thumbnails to confirm/unconfirm detections (green border = confirmed)
- **Timer System**: Start/pause/stop timer to track verification session duration
- **Pause Mode**: Pause timer and obfuscate images when needed
- **Excel Export**: Export confirmed detections with timing data to Excel format
- **Cross-Platform**: Works on Windows and macOS

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Test Data** (optional):
   ```bash
   python generate_test_data.py
   ```

3. **Run Application**:
   ```bash
   python run_app.py
   ```

## Usage Workflow

1. **Load Data**: Click "Load Annotations" and select the `test_data/annotations.json` file
2. **Start Session**: Click "Start Session" to begin timing
3. **Review Detections**: 
   - Hover over thumbnails to see detailed view
   - Click thumbnails to confirm/unconfirm (green = confirmed)
   - Use scroll to navigate through all detections
4. **Export Results**: Click "Stop & Export" to save verified results to Excel

## File Structure

```
standalone_app/
├── sperm_verification_app.py    # Main application
├── generate_test_data.py        # Test data generator
├── run_app.py                   # Simple launcher
├── requirements.txt             # Dependencies
├── README.md                    # This file
└── test_data/
    ├── annotations.json         # Test annotations
    └── images/                  # Test microscopy images
        ├── microscopy_sample_001.png
        ├── microscopy_sample_002.png
        └── ...
```

## JSON Format

The application expects JSON files with this structure:

```json
[
  {
    "image_path": "/path/to/image.png",
    "image_name": "image.png",
    "detections": [
      {
        "bbox": [x1, y1, x2, y2],
        "confidence": 0.85,
        "cell_id": "cell_1"
      }
    ],
    "num_detections": 1
  }
]
```

## Export Format

Confirmed detections are exported to Excel with these columns:
- `image_path`: Full path to source image
- `detection_id`: Unique detection identifier
- `cell_id`: Cell identifier from annotations
- `x1, y1, x2, y2`: Bounding box coordinates
- `confidence`: Detection confidence score
- `verified`: Always True for exported items
- `session_duration`: Total verification time
- `export_time`: Timestamp of export

## Building Executables

To create standalone executables:

### Windows:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed run_app.py
```

### macOS:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed run_app.py
```

The executable will be created in the `dist/` folder.

## System Requirements

- Python 3.8+
- PySide6 (Qt6)
- NumPy
- Pandas
- Pillow (PIL)
- OpenPyXL

## License

This tool is provided for research purposes.
