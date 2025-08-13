from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any


def build_local_image_map(images_dir: Path) -> Dict[str, Path]:

	image_map: Dict[str, Path] = {}
	if not images_dir.exists():
		raise FileNotFoundError(f"Images directory not found: {images_dir}")

	for p in images_dir.iterdir():
		if not p.is_file():
			continue
		image_map[p.name] = p.resolve()
	return image_map


def filter_and_rewrite_entries(data: List[dict], image_map: Dict[str, Path]) -> List[dict]:

	kept: List[dict] = []
	for entry in data:
		image_str = entry.get("image_path")
		if not image_str:
			continue
		basename = Path(image_str).name
		local_path = image_map.get(basename)
		if local_path is None:
			continue
		new_entry = dict(entry)
		new_entry["image_path"] = str(local_path)
		kept.append(new_entry)
	return kept


def main() -> None:

	parser = argparse.ArgumentParser(description="Rewrite JSON image_path entries to local images and drop missing ones.")
	parser.add_argument("--input", required=True, type=Path, help="Path to input JSON file")
	parser.add_argument("--images", required=True, type=Path, help="Path to local images directory")
	parser.add_argument("--output", required=True, type=Path, help="Path to write filtered JSON file")
	args = parser.parse_args()

	input_json: Path = args.input
	images_dir: Path = args.images
	output_json: Path = args.output

	with input_json.open("r") as f:
		data: List[Any] = json.load(f)
		if not isinstance(data, list):
			raise ValueError("Input JSON must be a list of image entries")

	image_map = build_local_image_map(images_dir)
	filtered = filter_and_rewrite_entries(data, image_map)

	output_json.parent.mkdir(parents=True, exist_ok=True)
	with output_json.open("w") as f:
		json.dump(filtered, f, indent=2)

	print(f"Total entries in input: {len(data)}")
	print(f"Images available locally: {len(image_map)}")
	print(f"Entries kept (matched to local images): {len(filtered)}")
	if filtered:
		first = filtered[0]
		print("Example updated entry image_path:", first.get("image_path"))


if __name__ == "__main__":
	main()


