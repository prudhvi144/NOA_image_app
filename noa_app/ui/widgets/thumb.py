from __future__ import annotations

from typing import Optional, Any
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QMouseEvent, QEnterEvent, QWheelEvent, QPixmap


class ThumbWidget(QLabel):
	hovered = Signal(object)
	clicked = Signal(object)
	wheelZoom = Signal(float, object)

	def __init__(self, meta: dict, pix: Optional[QPixmap] = None, parent=None) -> None:
		super().__init__(parent)
		self.meta = meta
		self.setMinimumSize(64, 64)
		self.setAlignment(Qt.AlignCenter)
		self.setStyleSheet("background:#1b1b1b; border:2px solid #333; border-radius:6px;")
		if pix is not None:
			self.setPixmap(pix)
		self._confirmed = False

	def setConfirmed(self, ok: bool) -> None:
		self._confirmed = ok
		color = "#2ecc71" if ok else "#333"
		self.setStyleSheet(f"background:#1b1b1b; border:2px solid {color}; border-radius:6px;")

	def enterEvent(self, event: QEnterEvent) -> None:  # type: ignore[override]
		self.hovered.emit(self.meta)
		super().enterEvent(event)

	def mousePressEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
		if event.button() == Qt.LeftButton:
			self.clicked.emit(self.meta)
		super().mousePressEvent(event)

	def wheelEvent(self, event: QWheelEvent) -> None:  # type: ignore[override]
		delta = event.angleDelta().y()
		factor = 1.0 + (0.1 if delta > 0 else -0.1)
		self.wheelZoom.emit(factor, self.meta)
		super().wheelEvent(event)
