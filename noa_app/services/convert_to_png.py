from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import numpy as np


def _to_uint8(arr: np.ndarray) -> np.ndarray:
	if arr.dtype == np.uint8:
		return arr
	if arr.dtype == np.uint16:
		return (arr / 257).astype(np.uint8)
	if np.issubdtype(arr.dtype, np.floating):
		arr = np.clip(arr, 0.0, 1.0)
		return (arr * 255.0 + 0.5).astype(np.uint8)
	# Fallback
	return arr.astype(np.uint8, copy=False)


def _ensure_rgb(arr: np.ndarray) -> np.ndarray:
	if arr.ndim == 2:
		arr = np.stack([arr, arr, arr], axis=2)
	elif arr.ndim == 3:
		if arr.shape[2] == 4:
			arr = arr[:, :, :3]
		elif arr.shape[0] in (1, 3, 4) and arr.shape[2] not in (1, 3, 4):
			# (C, H, W) -> (H, W, C)
			arr = np.transpose(arr, (1, 2, 0))
			if arr.shape[2] == 4:
				arr = arr[:, :, :3]
	return arr


def _read_with_pil(path: Path) -> Optional[np.ndarray]:
	try:
		from PIL import Image
		with Image.open(str(path)) as im:
			if hasattr(im, "n_frames") and im.n_frames > 1:
				im.seek(0)
			arr = np.array(im)
			return arr
	except Exception:
		return None


def _read_with_tifffile(path: Path) -> Optional[np.ndarray]:
	try:
		import tifffile
		arr = tifffile.imread(str(path))
		if arr.ndim == 4:
			arr = arr[0]
		return arr
	except Exception:
		return None


def _read_with_cv2(path: Path) -> Optional[np.ndarray]:
	try:
		import cv2
		arr = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
		if arr is None:
			return None
		# BGR -> RGB for 3-channel
		if arr.ndim == 3 and arr.shape[2] == 3:
			arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
		if arr.ndim == 3 and arr.shape[2] == 4:
			arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2RGB)
		return arr
	except Exception:
		return None


def convert_all(images_dir: Path) -> None:
	from PIL import Image
	count_total = 0
	count_converted = 0
	count_skipped_exist = 0
	count_failed = 0

	for tif_path in sorted(images_dir.glob("*.tif")):
		count_total += 1
		png_path = tif_path.with_suffix(".png")
		if png_path.exists():
			count_skipped_exist += 1
			continue

		arr = (
			_read_with_pil(tif_path)
			or _read_with_tifffile(tif_path)
			or _read_with_cv2(tif_path)
		)
		if arr is None or arr.size == 0:
			print(f"FAILED: {tif_path.name} (could not decode)")
			count_failed += 1
			continue

		arr = _ensure_rgb(arr)
		arr = _to_uint8(arr)
		Image.fromarray(arr).save(str(png_path))
		print(f"WROTE: {png_path.name}")
		count_converted += 1

	print(
		f"Done. total={count_total}, converted={count_converted}, already_png={count_skipped_exist}, failed={count_failed}"
	)


def main() -> None:
	parser = argparse.ArgumentParser(description="Convert .tif images in a folder to .png (best-effort)")
	parser.add_argument("--images", required=True, type=Path, help="Path to images directory")
	args = parser.parse_args()
	convert_all(args.images)


if __name__ == "__main__":
	main()


