from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap


class ViewPanel(QWidget):
	def __init__(self, parent: Optional[QWidget] = None) -> None:
		super().__init__(parent)
		layout = QVBoxLayout(self)
		layout.setContentsMargins(8, 8, 8, 8)
		layout.setSpacing(8)
		self.viewport = QLabel("Viewfinder")
		self.viewport.setAlignment(Qt.AlignCenter)
		self.viewport.setStyleSheet("background: #111; color: #bbb; padding: 24px; border-radius: 8px;")
		self.coords = QLabel("")
		self.coords.setAlignment(Qt.AlignRight)
		self.coords.setStyleSheet("color: #888;")
		layout.addWidget(self.viewport, 1)
		layout.addWidget(self.coords)
		self._pix: Optional[QPixmap] = None
		self._zoom: float = 1.0

	def set_image(self, pix: QPixmap) -> None:
		self._pix = pix
		self._zoom = 1.0
		self._render()

	def clear_image(self) -> None:
		self._pix = None
		self.viewport.clear()

	def set_coords_text(self, text: str) -> None:
		self.coords.setText(text)

	def zoom_by(self, factor: float) -> None:
		self._zoom = max(0.2, min(3.0, self._zoom * factor))
		self._render()

	def _render(self) -> None:
		if self._pix is None:
			self.viewport.clear()
			return
		size = self.viewport.size()
		w = int(size.width() * self._zoom)
		h = int(size.height() * self._zoom)
		scaled = self._pix.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.viewport.setPixmap(scaled)
