from __future__ import annotations

from typing import Tuple
import numpy as np
from PySide6.QtGui import QImage, QPixmap


def numpy_rgb_to_qpixmap(arr: np.ndarray) -> QPixmap:
	"""Convert RGB uint8 array to QPixmap."""
	if arr.dtype != np.uint8:
		raise ValueError("Array must be uint8 for QImage")
	h, w = arr.shape[:2]
	bytes_per_line = 3 * w
	qimg = QImage(arr.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
	return QPixmap.fromImage(qimg.copy())
