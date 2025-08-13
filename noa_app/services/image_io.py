from __future__ import annotations

from pathlib import Path
from typing import Tuple
import cv2
import numpy as np


def load_image_rgb(path: Path) -> np.ndarray:
	"""Load image as RGB numpy array preserving bit depth.

	- Supports PNG/JPG/TIFF (single page).
	- Returns shape (H, W, 3) dtype uint8 or uint16 depending on source.
	"""
	path = Path(path)
	img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
	if img is None:
		raise FileNotFoundError(path)
	# Ensure 3 channels
	if img.ndim == 2:
		img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
	elif img.shape[2] == 4:
		img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
	# Convert BGR->RGB
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	return img


def to_uint8_for_display(image: np.ndarray) -> np.ndarray:
	"""Convert 8/16-bit RGB to 8-bit for UI display with simple normalization.
	For uint16, scales using 0..65535 -> 0..255.
	"""
	if image.dtype == np.uint8:
		return image
	if image.dtype == np.uint16:
		return (image / 257).astype(np.uint8)
	raise ValueError(f"Unsupported dtype: {image.dtype}")
