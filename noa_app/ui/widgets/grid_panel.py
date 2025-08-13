from __future__ import annotations

from typing import Optional, List, Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QPushButton,
	QGridLayout,
	QScrollArea,
)

from .thumb import ThumbWidget


class GridPanel(QWidget):
	itemHovered = Signal(object)
	itemClicked = Signal(object)
	wheelZoom = Signal(float, object)

	def __init__(self, parent: Optional[QWidget] = None) -> None:
		super().__init__(parent)
		self._thumb_size = 128
		self._rows = 10
		self._cols = 10
		self._items: List[dict] = []
		self._page = 0

		outer = QVBoxLayout(self)
		outer.setContentsMargins(8, 8, 8, 8)
		outer.setSpacing(8)

		self.scroll = QScrollArea(self)
		self.scroll.setWidgetResizable(True)
		container = QWidget()
		self.grid = QGridLayout(container)
		self.grid.setSpacing(8)
		self.scroll.setWidget(container)
		outer.addWidget(self.scroll, 1)

		controls = QHBoxLayout()
		self.prev_btn = QPushButton("◀")
		self.page_label = QLabel("1/1")
		self.next_btn = QPushButton("▶")
		controls.addWidget(self.prev_btn)
		controls.addWidget(self.page_label, 0, Qt.AlignCenter)
		controls.addWidget(self.next_btn)
		outer.addLayout(controls)

		self.prev_btn.clicked.connect(self.prev_page)
		self.next_btn.clicked.connect(self.next_page)

	def set_items(self, items: List[dict], rows: int = 10, cols: int = 10) -> None:
		self._items = items
		self._rows = rows
		self._cols = cols
		self._page = 0
		self._rebuild()

	def page_count(self) -> int:
		per = self._rows * self._cols
		return max(1, (len(self._items) + per - 1) // per)

	def _rebuild(self) -> None:
		# clear
		while self.grid.count():
			item = self.grid.takeAt(0)
			w = item.widget()
			if w:
				w.setParent(None)
		per = self._rows * self._cols
		start = self._page * per
		end = min(len(self._items), start + per)
		row = col = 0
		for idx in range(start, end):
			meta = self._items[idx]
			thumb: ThumbWidget = meta["thumb_widget"]
			self.grid.addWidget(thumb, row, col)
			row += 1
			if row >= self._rows:
				row = 0
				col += 1
		self.page_label.setText(f"{self._page + 1}/{self.page_count()}")

	def prev_page(self) -> None:
		if self._page > 0:
			self._page -= 1
			self._rebuild()

	def next_page(self) -> None:
		if self._page + 1 < self.page_count():
			self._page += 1
			self._rebuild()

	def build_thumb(self, meta: dict, pix) -> ThumbWidget:
		thumb = ThumbWidget(meta, pix)
		thumb.hovered.connect(self.itemHovered)
		thumb.clicked.connect(self.itemClicked)
		thumb.wheelZoom.connect(self.wheelZoom)
		return thumb
