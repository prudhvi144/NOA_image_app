from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import cv2


@dataclass
class BBox:
	xmin: int
	ymin: int
	xmax: int
	ymax: int


@dataclass
class CropSpec:
	padding_ratio: float = 1.0  # 100% each side
	output_size: int = 512      # for viewfinder; grid thumbs will be scaled separately


def _ensure_rgb_u16(image: np.ndarray) -> np.ndarray:
	if image.dtype == np.uint8:
		return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	# assume OpenCV loads as uint16 BGR for 16-bit images
	return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def crop_with_padding(image: np.ndarray, bbox: BBox, spec: CropSpec) -> np.ndarray:
	"""Return a square, padded crop around bbox.

	- padding_ratio=1.0 adds box width/height on each side.
	- padding outside image is filled with black.
	- output is resized to spec.output_size (square).
	"""
	h, w = image.shape[:2]
	bw = bbox.xmax - bbox.xmin
	bh = bbox.ymax - bbox.ymin
	pad_x = int(bw * spec.padding_ratio)
	pad_y = int(bh * spec.padding_ratio)
	cx = (bbox.xmin + bbox.xmax) // 2
	cy = (bbox.ymin + bbox.ymax) // 2
	# square half-size is max of padded extents
	half = max((bw // 2) + pad_x, (bh // 2) + pad_y)
	left = cx - half
	right = cx + half
	top = cy - half
	bottom = cy + half

	# Compute intersection with image and required padding
	x0 = max(0, left)
	y0 = max(0, top)
	x1 = min(w, right)
	y1 = min(h, bottom)

	crop = image[y0:y1, x0:x1]
	size = 2 * half
	canvas = np.zeros((size, size, image.shape[2]), dtype=image.dtype)
	# place crop on canvas
	dx = x0 - left
	dy = y0 - top
	canvas[dy:dy + crop.shape[0], dx:dx + crop.shape[1]] = crop
	# resize to output size
	resized = cv2.resize(canvas, (spec.output_size, spec.output_size), interpolation=cv2.INTER_AREA)
	return resized
