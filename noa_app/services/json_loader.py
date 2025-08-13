from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Any
import json


@dataclass
class Detection:
	image_path: Path
	box_id: str
	xmin: int
	ymin: int
	xmax: int
	ymax: int
	confidence: float


def _to_int(x: Any) -> int:
	try:
		return int(round(float(x)))
	except Exception:
		return int(x)


def load_detections(json_path: Path) -> List[Detection]:
	"""Parse dataset JSON (sample schema) into a flat list of detections.

	Schema inferred from sample:
	[
	  {
	    "image_path": "/abs/or/relative/path/to/image.tif",
	    "pred_boxes": [[xmin, ymin, xmax, ymax], ...],
	    "pred_scores": [score0, score1, ...],
	    "predictions": [[p0, p1], ...],  # unused for now
	    "num_detected_sperm": N
	  },
	  ...
	]
	"""
	json_path = Path(json_path)
	with json_path.open("r", encoding="utf-8") as f:
		data = json.load(f)

	detections: List[Detection] = []
	for image_entry in data:
		image_str = image_entry.get("image_path")
		if not image_str:
			continue
		image_p = Path(image_str)
		boxes = image_entry.get("pred_boxes") or []
		scores = image_entry.get("pred_scores") or []
		count = min(len(boxes), len(scores))
		for i in range(count):
			xmin, ymin, xmax, ymax = boxes[i]
			conf = float(scores[i])
			box_id = f"{image_p.name}:{i}"
			detections.append(
				Detection(
					image_path=image_p,
					box_id=box_id,
					xmin=_to_int(xmin),
					ymin=_to_int(ymin),
					xmax=_to_int(xmax),
					ymax=_to_int(ymax),
					confidence=conf,
				)
			)
	return detections
