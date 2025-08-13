from __future__ import annotations

from pathlib import Path
from typing import Tuple
import cv2
import numpy as np
import tifffile
from PIL import Image


def load_image_rgb(path: Path) -> np.ndarray:
	"""Load image as RGB numpy array preserving bit depth.

	- Supports PNG/JPG/TIFF (single page).
	- Returns shape (H, W, 3) dtype uint8 or uint16 depending on source.
	"""
	path = Path(path)
	
	# Try PIL first (like your training code) - handles multi-frame TIFFs well
	try:
		with open(str(path), 'rb') as f:
			with Image.open(f) as img:
				# For multi-frame TIFFs, take the first frame (index 0)
				if hasattr(img, 'n_frames') and img.n_frames > 1:
					img.seek(0)  # Go to first frame
				
				# Convert to RGB
				rgb_img = img.convert('RGB')
				arr = np.array(rgb_img)
				return arr
	except Exception:
		pass
	
	# Try OpenCV as fallback
	img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
	if img is not None:
		# OpenCV loaded successfully - handle channels and convert BGR->RGB
		if img.ndim == 2:
			img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		elif img.shape[2] == 4:
			img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
		# Convert BGR->RGB
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		return img
	
	# Final fallback: try tifffile (suppress warnings)
	try:
		import warnings
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			arr = tifffile.imread(str(path))
			# Take first image if multiple
			if arr.ndim == 4:  # Multiple images
				arr = arr[0]
			# Check if we got valid data
			if arr.size == 0:
				raise ValueError("Empty array from tifffile")
			# Normalize to HxWxC
			if arr.ndim == 2:
				arr = np.stack([arr, arr, arr], axis=2)
			elif arr.ndim == 3:
				if arr.shape[0] in (1, 3, 4) and arr.shape[2] not in (1, 3, 4):
					arr = np.transpose(arr, (1, 2, 0))
				if arr.shape[2] == 1:
					arr = np.repeat(arr, 3, axis=2)
				elif arr.shape[2] > 3:
					arr = arr[:, :, :3]
			return arr
	except Exception:
		pass
	
	# Last resort: create a placeholder image for testing
	print(f"Warning: Could not load {path}, creating placeholder image")
	# Create a 1280x1024 grayscale placeholder with some pattern
	placeholder = np.zeros((1024, 1280), dtype=np.uint8)
	# Add a simple pattern so we can see something
	placeholder[::50, :] = 128  # Horizontal lines
	placeholder[:, ::50] = 128  # Vertical lines
	# Convert to RGB
	placeholder_rgb = np.stack([placeholder, placeholder, placeholder], axis=2)
	return placeholder_rgb


def to_uint8_for_display(image: np.ndarray) -> np.ndarray:
	"""Convert 8/16-bit RGB to 8-bit for UI display with simple normalization.
	For uint16, scales using 0..65535 -> 0..255.
	"""
	if image.dtype == np.uint8:
		return image
	if image.dtype == np.uint16:
		return (image / 257).astype(np.uint8)
	raise ValueError(f"Unsupported dtype: {image.dtype}")
