from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Any


def rewrite(json_in: Path, images_dir: Path, json_out: Path) -> None:
	with json_in.open("r", encoding="utf-8") as f:
		data: List[Any] = json.load(f)

	# Build set of available PNG basenames
	pngs = {p.name for p in images_dir.glob("*.png")}

	kept = []
	for entry in data:
		img_path = entry.get("image_path")
		if not img_path:
			continue
		name = Path(img_path).name
		name_png = Path(name).with_suffix(".png").name
		if name_png in pngs:
			new_entry = dict(entry)
			new_entry["image_path"] = str(images_dir / name_png)
			kept.append(new_entry)

	json_out.parent.mkdir(parents=True, exist_ok=True)
	with json_out.open("w", encoding="utf-8") as f:
		json.dump(kept, f, indent=2)

	print(f"Input entries: {len(data)}")
	print(f"PNG images found: {len(pngs)}")
	print(f"Entries kept (PNG available): {len(kept)}")


def main() -> None:
	parser = argparse.ArgumentParser(description="Rewrite JSON image paths to .png where available")
	parser.add_argument("--input", required=True, type=Path)
	parser.add_argument("--images", required=True, type=Path)
	parser.add_argument("--output", required=True, type=Path)
	args = parser.parse_args()

	rewrite(args.input, args.images, args.output)


if __name__ == "__main__":
	main()


