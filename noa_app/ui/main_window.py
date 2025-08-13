from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
	QMainWindow,
	QSplitter,
	QToolBar,
	QStatusBar,
	QLabel,
	QFileDialog,
	QDoubleSpinBox,
	QInputDialog,
	QMessageBox,
)

from .widgets.grid_panel import GridPanel
from .widgets.view_panel import ViewPanel
from ..services.json_loader import load_detections, Detection
from ..services.image_io import load_image_rgb, to_uint8_for_display
from ..services.cropper import crop_with_padding, CropSpec, BBox
from ..services.cache import LRUCache
from ..services.qt_image import numpy_rgb_to_qpixmap


class PauseOverlay(QLabel):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setStyleSheet(
			"background: rgba(0,0,0,0.6); color: white; font-size: 28px;"
		)
		self.setAlignment(Qt.AlignCenter)
		self.setText("Paused")
		self.hide()


class MainWindow(QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self.setWindowTitle("NOA Grid App")
		self.resize(1400, 900)

		# Data/state
		self.detections: List[Detection] = []
		self.confirmed: set[str] = set()
		self.conf_threshold: float = 0.0
		self.thumb_cache = LRUCache[str, object](capacity=512)
		self.crop_spec = CropSpec(padding_ratio=1.0, output_size=512)

		# Toolbar
		self.toolbar = QToolBar("Main Toolbar", self)
		self.addToolBar(Qt.TopToolBarArea, self.toolbar)

		self.action_load_images = QAction("Load Images", self)
		self.action_load_json = QAction("Load JSON", self)
		self.action_start = QAction("Start", self)
		self.action_pause = QAction("Pause", self)
		self.action_stop = QAction("Stop/OK", self)
		self.action_clear = QAction("Clear", self)

		for action in (
			self.action_load_images,
			self.action_load_json,
			self.action_start,
			self.action_pause,
			self.action_stop,
			self.action_clear,
		):
			self.toolbar.addAction(action)

		self.toolbar.addSeparator()
		self.toolbar.addWidget(QLabel("Confidence ≥"))
		self.conf_spin = QDoubleSpinBox(self)
		self.conf_spin.setRange(0.0, 1.0)
		self.conf_spin.setSingleStep(0.01)
		self.toolbar.addWidget(self.conf_spin)

		# Central split: grid (left) and viewfinder (right)
		splitter = QSplitter(Qt.Horizontal, self)
		self.grid_panel = GridPanel(self)
		self.view_panel = ViewPanel(self)
		splitter.addWidget(self.grid_panel)
		splitter.addWidget(self.view_panel)
		splitter.setStretchFactor(0, 3)
		splitter.setStretchFactor(1, 2)
		self.setCentralWidget(splitter)

		# Status bar with coordinates and timer
		status = QStatusBar(self)
		self.setStatusBar(status)
		self.coords_label = QLabel("(x1, y1; x2, y2)")
		self.timer_label = QLabel("00:00:00")
		status.addPermanentWidget(self.coords_label)
		status.addPermanentWidget(self.timer_label)

		# Pause overlay
		self.overlay = PauseOverlay(self)
		self.overlay.setGeometry(self.rect())
		self.overlay.raise_()

		# Timer state
        self.session_started: Optional[datetime] = None
        self.session_paused_at: Optional[datetime] = None
		self.total_paused = timedelta(0)
		self.timer = QTimer(self)
		self.timer.timeout.connect(self._tick)

		# Wire signals
		self.action_load_json.triggered.connect(self.load_json)
		self.action_clear.triggered.connect(self.clear_all)
		self.action_start.triggered.connect(self.start_timer)
		self.action_pause.triggered.connect(self.toggle_pause)
		self.action_stop.triggered.connect(self.stop_and_export)
		self.conf_spin.valueChanged.connect(self.on_conf_changed)
		self.grid_panel.itemHovered.connect(self.on_item_hover)
		self.grid_panel.itemClicked.connect(self.on_item_click)
		self.grid_panel.wheelZoom.connect(self.on_wheel_zoom)

	def resizeEvent(self, event):  # type: ignore[override]
		super().resizeEvent(event)
		self.overlay.setGeometry(self.rect())

	# Data loading
	def load_json(self) -> None:
		json_path_str, _ = QFileDialog.getOpenFileName(self, "Select JSON", str(Path.home()), "JSON (*.json)")
		if not json_path_str:
			return
		json_path = Path(json_path_str)
		self.detections = load_detections(json_path)
		self._refresh_grid()

	def on_conf_changed(self, val: float) -> None:
		self.conf_threshold = val
		self._refresh_grid()

	def _filtered_detections(self) -> List[Detection]:
		return [d for d in self.detections if d.confidence >= self.conf_threshold]

	def _thumb_for(self, det: Detection):
		key = f"thumb:{det.image_path}:{det.box_id}"
		cached = self.thumb_cache.get(key)
		if cached is not None:
			return cached
		img = load_image_rgb(det.image_path)
		from ..services.cropper import CropSpec, BBox, crop_with_padding
		thumb_img = crop_with_padding(img, BBox(det.xmin, det.ymin, det.xmax, det.ymax), CropSpec(padding_ratio=1.0, output_size=128))
		thumb_img8 = to_uint8_for_display(thumb_img)
		pix = numpy_rgb_to_qpixmap(thumb_img8)
		self.thumb_cache.put(key, pix)
		return pix

	def _crop_for_view(self, det: Detection):
		key = f"view:{det.image_path}:{det.box_id}"
		cached = self.thumb_cache.get(key)
		if cached is not None:
			return cached
		img = load_image_rgb(det.image_path)
		crop_img = crop_with_padding(img, BBox(det.xmin, det.ymin, det.xmax, det.ymax), self.crop_spec)
		crop_img8 = to_uint8_for_display(crop_img)
		pix = numpy_rgb_to_qpixmap(crop_img8)
		self.thumb_cache.put(key, pix)
		return pix

	def _refresh_grid(self) -> None:
		items: List[Dict] = []
		for det in self._filtered_detections():
			meta = {
				"det": det,
			}
			pix = self._thumb_for(det)
			thumb_widget = self.grid_panel.build_thumb(meta, pix)
			thumb_widget.setConfirmed(det.box_id in self.confirmed)
			meta["thumb_widget"] = thumb_widget
			items.append(meta)
		self.grid_panel.set_items(items, rows=10, cols=10)

	# Interactions
	def on_item_hover(self, meta: Dict) -> None:
		det: Detection = meta["det"]
		pix = self._crop_for_view(det)
		self.view_panel.set_image(pix)
		self.view_panel.set_coords_text(f"({det.xmin}, {det.ymin}; {det.xmax}, {det.ymax})")
		self.coords_label.setText(f"({det.xmin}, {det.ymin}; {det.xmax}, {det.ymax})")

	def on_wheel_zoom(self, factor: float, meta: Dict) -> None:
		self.view_panel.zoom_by(factor)

	def on_item_click(self, meta: Dict) -> None:
		det: Detection = meta["det"]
		if det.box_id in self.confirmed:
			self.confirmed.remove(det.box_id)
		else:
			self.confirmed.add(det.box_id)
		# update visual
		meta["thumb_widget"].setConfirmed(det.box_id in self.confirmed)

	# Timer controls
	def start_timer(self) -> None:
		if self.session_started is not None:
			return
		text, ok = QInputDialog.getText(self, "Reviewer ID", "Enter reviewer ID (optional):")
		self.reviewer_id = text if ok else ""
		self.session_started = datetime.now()
		self.total_paused = timedelta(0)
		self.session_paused_at = None
		self.timer.start(1000)

	def toggle_pause(self) -> None:
		if self.session_started is None:
			return
		if self.session_paused_at is None:
			# pause now
			self.session_paused_at = datetime.now()
			self.overlay.show()
			self.grid_panel.setDisabled(True)
		else:
			# resume
			paused = datetime.now() - self.session_paused_at
			self.total_paused += paused
			self.session_paused_at = None
			self.overlay.hide()
			self.grid_panel.setDisabled(False)

	def _tick(self) -> None:
		if self.session_started is None:
			self.timer_label.setText("00:00:00")
			return
		end = datetime.now()
		elapsed = end - self.session_started - self.total_paused
		if self.session_paused_at is not None:
			elapsed -= (end - self.session_paused_at)
		self.timer_label.setText(self._format_td(elapsed))

	def _format_td(self, td: timedelta) -> str:
		total = int(td.total_seconds())
		h = total // 3600
		m = (total % 3600) // 60
		s = total % 60
		return f"{h:02d}:{m:02d}:{s:02d}"

	def stop_and_export(self) -> None:
		if self.session_started is None:
			return
		ended_at = datetime.now()
		elapsed = ended_at - self.session_started - self.total_paused
		# Build export rows for confirmed only
		rows = []
		for det in self._filtered_detections():
			if det.box_id in self.confirmed:
				rows.append({
					"image_path": str(det.image_path),
					"box_id": det.box_id,
					"xmin": det.xmin,
					"ymin": det.ymin,
					"xmax": det.xmax,
					"ymax": det.ymax,
					"started_at": self.session_started.isoformat(),
					"ended_at": ended_at.isoformat(),
					"elapsed_time": self._format_td(elapsed),
					"reviewer_id": getattr(self, "reviewer_id", ""),
				})
		if not rows:
			QMessageBox.information(self, "Export", "No confirmed items to export.")
			return
		# Save next to images: default to directory of first confirmed image
		first_dir = Path(rows[0]["image_path"]).parent
		out_csv = first_dir / "confirmations.csv"
		self._write_csv(out_csv, rows)
		QMessageBox.information(self, "Export", f"Saved {len(rows)} confirmations to\n{out_csv}")
		# reset timer state
		self.timer.stop()
		self.session_started = None
		self.session_paused_at = None
		self.total_paused = timedelta(0)
		self.timer_label.setText("00:00:00")

	def _write_csv(self, path: Path, rows: List[dict]) -> None:
		import csv
		with path.open("w", newline="", encoding="utf-8") as f:
			writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
			writer.writeheader()
			writer.writerows(rows)

	def clear_all(self) -> None:
		self.detections = []
		self.confirmed.clear()
		self.thumb_cache = LRUCache(capacity=512)
		self.grid_panel.set_items([])
		self.view_panel.clear_image()
		self.coords_label.setText("(x1, y1; x2, y2)")
		self.timer.stop()
		self.session_started = None
		self.session_paused_at = None
		self.total_paused = timedelta(0)
		self.timer_label.setText("00:00:00")
