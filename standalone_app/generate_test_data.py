#!/usr/bin/env python3
"""Generate synthetic microscopy images and annotations for testing."""

import json
import random
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw


def generate_microscopy_background(width: int = 1280, height: int = 1024) -> np.ndarray:
    """Generate realistic microscopy background with noise and texture."""
    # Base grayscale background
    base = np.random.normal(180, 25, (height, width)).astype(np.uint8)
    base = np.clip(base, 100, 220)
    
    # Add some texture with noise
    noise = np.random.normal(0, 8, (height, width))
    textured = base + noise
    textured = np.clip(textured, 0, 255).astype(np.uint8)
    
    # Convert to RGB
    background = np.stack([textured, textured, textured], axis=2)
    return background


def draw_sperm_cell(draw: ImageDraw.Draw, x: int, y: int, size: int = 20) -> Tuple[int, int, int, int]:
    """Draw a synthetic sperm cell and return bounding box."""
    # Head (oval)
    head_w, head_h = size // 2, size // 3
    head_x1 = x - head_w // 2
    head_y1 = y - head_h // 2
    head_x2 = x + head_w // 2
    head_y2 = y + head_h // 2
    
    # Draw head
    draw.ellipse([head_x1, head_y1, head_x2, head_y2], 
                 fill=(80, 90, 100), outline=(60, 70, 80), width=1)
    
    # Tail (curved line)
    tail_length = size * 2
    tail_points = []
    for i in range(10):
        t = i / 9.0
        tail_x = x + int(tail_length * t * 0.8)
        tail_y = y + head_h // 2 + int(10 * np.sin(t * np.pi * 2) * (1 - t))
        tail_points.append((tail_x, tail_y))
    
    # Draw tail as connected lines
    for i in range(len(tail_points) - 1):
        draw.line([tail_points[i], tail_points[i + 1]], 
                  fill=(100, 110, 120), width=2)
    
    # Calculate bounding box
    all_x = [head_x1, head_x2] + [p[0] for p in tail_points]
    all_y = [head_y1, head_y2] + [p[1] for p in tail_points]
    
    bbox_x1 = max(0, min(all_x) - 5)
    bbox_y1 = max(0, min(all_y) - 5)
    bbox_x2 = min(1280, max(all_x) + 5)
    bbox_y2 = min(1024, max(all_y) + 5)
    
    return bbox_x1, bbox_y1, bbox_x2, bbox_y2


def generate_test_image(image_path: Path, num_cells: int = None) -> List[dict]:
    """Generate a synthetic microscopy image with sperm cells."""
    if num_cells is None:
        num_cells = random.randint(3, 12)
    
    # Generate background
    background = generate_microscopy_background()
    img = Image.fromarray(background)
    draw = ImageDraw.Draw(img)
    
    # Generate cells and annotations
    annotations = []
    for i in range(num_cells):
        # Random position (avoid edges)
        x = random.randint(50, 1230)
        y = random.randint(50, 974)
        size = random.randint(15, 30)
        
        # Draw cell and get bounding box
        bbox = draw_sperm_cell(draw, x, y, size)
        
        # Create annotation
        annotations.append({
            "bbox": list(bbox),
            "confidence": round(random.uniform(0.6, 0.95), 3),
            "cell_id": f"cell_{i+1}"
        })
    
    # Save image
    img.save(str(image_path))
    return annotations


def generate_test_dataset(output_dir: Path, num_images: int = 10) -> None:
    """Generate complete test dataset."""
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    all_annotations = []
    
    for i in range(num_images):
        image_name = f"microscopy_sample_{i+1:03d}.png"
        image_path = images_dir / image_name
        
        print(f"Generating {image_name}...")
        cell_annotations = generate_test_image(image_path)
        
        # Create entry for JSON
        entry = {
            "image_path": str(image_path.absolute()),
            "image_name": image_name,
            "detections": cell_annotations,
            "num_detections": len(cell_annotations)
        }
        all_annotations.append(entry)
    
    # Save annotations JSON
    annotations_path = output_dir / "annotations.json"
    with open(annotations_path, 'w') as f:
        json.dump(all_annotations, f, indent=2)
    
    print(f"\nGenerated {num_images} test images and annotations:")
    print(f"Images: {images_dir}")
    print(f"Annotations: {annotations_path}")
    print(f"Total detections: {sum(len(entry['detections']) for entry in all_annotations)}")


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "test_data"
    generate_test_dataset(output_dir, num_images=15)
