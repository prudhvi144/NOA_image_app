#!/usr/bin/env python3
"""
Debug script to test path resolution from Distribution folder
"""

import os
from pathlib import Path
import json

def debug_path_resolution():
    print("=== PATH RESOLUTION DEBUG ===")
    print(f"Current working directory: {os.getcwd()}")
    
    # Test the exact scenario you're using
    root_path = "/Users/prudhvi/Desktop/NOA_image_app/Distribution/Data"
    json_path = "/Users/prudhvi/Desktop/NOA_image_app/Distribution/Data/keyence_vs_cephla_keyence/reclassified_pred_fixed.json"
    
    print(f"Root path: {root_path}")
    print(f"JSON path: {json_path}")
    
    # Check if paths exist
    print(f"Root exists: {Path(root_path).exists()}")
    print(f"JSON exists: {Path(json_path).exists()}")
    
    # Load a sample from JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Get first detection
    first_detection = data[0]
    image_path = first_detection['image_path']
    print(f"Sample image path from JSON: {image_path}")
    
    # Test different path resolution methods
    print("\n=== TESTING PATH RESOLUTION ===")
    
    # Method 1: Direct join
    resolved1 = Path(root_path) / image_path
    print(f"Method 1 (root + image_path): {resolved1}")
    print(f"Method 1 exists: {resolved1.exists()}")
    
    # Method 2: Remove leading ./
    clean_image_path = image_path.replace('./', '')
    resolved2 = Path(root_path) / clean_image_path
    print(f"Method 2 (root + clean_path): {resolved2}")
    print(f"Method 2 exists: {resolved2.exists()}")
    
    # Method 3: Resolve from JSON directory
    json_dir = Path(json_path).parent
    resolved3 = json_dir / image_path.replace('./', '')
    print(f"Method 3 (json_dir + clean_path): {resolved3}")
    print(f"Method 3 exists: {resolved3.exists()}")
    
    # Test actual file listing
    print(f"\n=== ACTUAL FILES IN PATIENT_2/images ===")
    images_dir = Path(root_path) / "keyence_vs_cephla_keyence/Patient_2/images"
    if images_dir.exists():
        files = list(images_dir.glob("*.tif"))[:5]
        for f in files:
            print(f"  {f.name}")
    else:
        print("Images directory not found!")

if __name__ == "__main__":
    debug_path_resolution()
