#!/usr/bin/env python3
"""
Sperm Cell Verification Application

A standalone GUI application for manually verifying neural network predictions
of sperm cell detections in microscopy images.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from PIL import Image
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QFont, QPalette, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QFileDialog, QMessageBox,
    QScrollArea, QFrame, QSplitter, QStatusBar, QDoubleSpinBox
)

# Import our beautiful modern theme
from modern_theme import apply_modern_theme

# Global variable for app directory (set in main())
APP_DIRECTORY = None

# Animation imports
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QRect
import random


class DetectionThumbnail(QLabel):
    """Thumbnail widget for a single detection with confirmation state."""
    
    clicked = Signal(dict)
    hovered = Signal(dict)
    
    def __init__(self, detection_data: dict, thumbnail_size: int = 80):
        super().__init__()
        self.detection_data = detection_data
        self.thumbnail_size = thumbnail_size
        self.confirmed = False
        
        self.setFixedSize(thumbnail_size, thumbnail_size + 20)  # Extra space for confidence
        self.setAlignment(Qt.AlignCenter)
        
        # Add confidence text at the bottom
        confidence = detection_data.get('confidence', 0.0)
        self.setText(f"Conf: {confidence:.2f}")
        self.setStyleSheet("""
            QLabel {
                border: 2px solid rgba(108, 117, 125, 0.3);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(255, 255, 255, 0.95),
                            stop:1 rgba(248, 249, 250, 0.9));
                border-radius: 8px;
                margin: 2px;
                color: black;
            }
            QLabel:hover {
                border: 2px solid #007bff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(0, 123, 255, 0.1),
                            stop:1 rgba(0, 123, 255, 0.05));
            }
        """)
        
        self.setScaledContents(True)
        self.setCursor(Qt.PointingHandCursor)
    
    def set_thumbnail(self, pixmap: QPixmap):
        """Set the thumbnail image."""
        self.setPixmap(pixmap)
    
    def set_confirmed(self, confirmed: bool):
        """Set confirmation state and update appearance."""
        self.confirmed = confirmed
        if confirmed:
            self.setStyleSheet("""
                QLabel {
                    border: 3px solid #28a745;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(40, 167, 69, 0.15),
                                stop:1 rgba(40, 167, 69, 0.08));
                    border-radius: 8px;
                    margin: 2px;
                    color: black;
                }
                QLabel:hover {
                    border: 3px solid #20c997;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(32, 201, 151, 0.2),
                                stop:1 rgba(32, 201, 151, 0.1));
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid rgba(108, 117, 125, 0.3);
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(255, 255, 255, 0.95),
                                stop:1 rgba(248, 249, 250, 0.9));
                    border-radius: 8px;
                    margin: 2px;
                    color: black;
                }
                QLabel:hover {
                    border: 2px solid #007bff;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(0, 123, 255, 0.1),
                                stop:1 rgba(0, 123, 255, 0.05));
                }
            """)
    
    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.detection_data)
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter (hover)."""
        self.hovered.emit(self.detection_data)
        super().enterEvent(event)


class ViewfinderWidget(QScrollArea):
    """Large view widget for displaying full images with zoom capability."""
    
    def __init__(self, size: int = 400):
        super().__init__()
        self.setMinimumSize(400, 300)  # Set minimum size instead of fixed size
        
        # Set size policy to expand
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setStyleSheet("""
            QScrollArea {
                border: 1px solid rgba(66, 133, 244, 0.2);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(255, 255, 255, 0.98),
                            stop:1 rgba(248, 249, 250, 0.95));
                border-radius: 16px;

            }
        """)
        
        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: transparent;")
        self.image_label.setText("Hover over thumbnails\nto see full image")
        self.image_label.setWordWrap(True)
        
        # Allow image label to expand
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setScaledContents(False)  # We'll handle scaling manually
        
        # Set up scroll area
        self.setWidget(self.image_label)
        self.setWidgetResizable(True)
        
        # Zoom properties
        self.zoom_factor = 1.0
        self.original_pixmap = None
        
    def set_image(self, image_path: str, bbox: list):
        """Set the full image with bounding box overlay."""
        try:
            # Load full image - simple, no conversions
            img = Image.open(image_path).convert("RGB")
            
            # Convert to numpy for drawing
            img_array = np.array(img)
            
            # Draw bounding box on the image
            from PIL import ImageDraw
            img_pil = Image.fromarray(img_array)
            draw = ImageDraw.Draw(img_pil)
            
            x1, y1, x2, y2 = bbox
            # Draw red bounding box
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
            
            # Reset label styling when showing images
            self.image_label.setStyleSheet("background-color: transparent;")
            
            # Convert PIL Image directly to QPixmap
            import io
            buffer = io.BytesIO()
            img_pil.save(buffer, format='PNG')
            buffer.seek(0)
            self.original_pixmap = QPixmap()
            self.original_pixmap.loadFromData(buffer.getvalue())
            
            # Calculate initial zoom to fit the viewfinder better
            self.fit_to_viewfinder()
            self.update_display()
            
        except Exception as e:
            print(f"Error loading full image: {e}")
            self.image_label.setText("Error loading\nfull image")
    
    def fit_to_viewfinder(self):
        """Calculate zoom factor to fit image nicely in viewfinder."""
        if self.original_pixmap:
            # Get viewfinder size (accounting for margins and scrollbars)
            viewfinder_size = self.viewport().size()
            available_width = viewfinder_size.width() - 20  # Some margin
            available_height = viewfinder_size.height() - 20
            
            # Get original image size
            img_width = self.original_pixmap.width()
            img_height = self.original_pixmap.height()
            
            # Calculate scale factors for width and height
            width_scale = available_width / img_width if img_width > 0 else 1.0
            height_scale = available_height / img_height if img_height > 0 else 1.0
            
            # Use the smaller scale factor to ensure it fits
            self.zoom_factor = min(width_scale, height_scale, 1.0)  # Don't zoom in beyond 1:1
            
            # Ensure minimum readable size
            self.zoom_factor = max(self.zoom_factor, 0.1)

    def update_display(self):
        """Update the display with current zoom."""
        if self.original_pixmap:
            # Scale pixmap according to zoom
            scaled_size = self.original_pixmap.size() * self.zoom_factor
            scaled_pixmap = self.original_pixmap.scaled(
                scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            
            # Set the scaled pixmap
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to zoom in at clicked location."""
        if self.original_pixmap and event.button() == Qt.LeftButton:
            # Get click position relative to the image
            click_pos = event.position()
            
            # Get the image label's position within the scroll area
            label_pos = self.image_label.pos()
            
            # Calculate zoom center relative to image
            zoom_center_x = (click_pos.x() - label_pos.x()) / self.zoom_factor
            zoom_center_y = (click_pos.y() - label_pos.y()) / self.zoom_factor
            
            # Zoom in
            old_zoom = self.zoom_factor
            self.zoom_factor = min(self.zoom_factor * 1.5, 3.0)  # Max 3x zoom
            
            if self.zoom_factor != old_zoom:
                self.update_display()
                
                # Center the view on the clicked point
                scrollbar_h = self.horizontalScrollBar()
                scrollbar_v = self.verticalScrollBar()
                
                # Calculate new scroll positions to center on click point
                new_h = int(zoom_center_x * self.zoom_factor - self.viewport().width() / 2)
                new_v = int(zoom_center_y * self.zoom_factor - self.viewport().height() / 2)
                
                scrollbar_h.setValue(new_h)
                scrollbar_v.setValue(new_v)
        
        super().mouseDoubleClickEvent(event)
    
    def zoom_in(self):
        """Zoom in by 50%."""
        if self.original_pixmap:
            self.zoom_factor = min(self.zoom_factor * 1.5, 3.0)  # Max 3x zoom
            self.update_display()
    
    def zoom_out(self):
        """Zoom out by 33%."""
        if self.original_pixmap:
            self.zoom_factor = max(self.zoom_factor / 1.5, 0.1)  # Min 0.1x zoom
            self.update_display()
    
    def reset_zoom(self):
        """Reset zoom to fit the viewfinder."""
        if self.original_pixmap:
            self.fit_to_viewfinder()
            self.update_display()
    
    def clear_image(self):
        """Clear the current image."""
        self.original_pixmap = None
        self.zoom_factor = 1.0
        self.image_label.clear()
        self.image_label.setText("Hover over thumbnails\nto see full image")
        self.image_label.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 0.6);
                color: white;
                font-size: 16px;
                font-weight: 500;
                padding: 20px;
                border-radius: 12px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)


class PauseOverlay(QWidget):
    """Elegant overlay widget shown when app is paused."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                            stop:0 rgba(0, 0, 0, 0.7),
                            stop:1 rgba(0, 0, 0, 0.85));
                color: white;
                font-size: 32px;
                font-weight: bold;
                border-radius: 20px;
            }
        """)
        
        # Only cover the content area, not the buttons
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Elegant pause icon
        pause_label = QLabel("⏸")  # Unicode pause symbol
        pause_label.setAlignment(Qt.AlignCenter)
        pause_label.setStyleSheet("""
            QLabel {
                font-size: 64px;
                color: rgba(255, 255, 255, 0.9);
                background: transparent;
                margin: 20px;
            }
        """)
        layout.addWidget(pause_label)
        
        # Text label
        text_label = QLabel("PAUSED")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: rgba(255, 255, 255, 0.95);
                background: transparent;
                letter-spacing: 3px;
            }
        """)
        layout.addWidget(text_label)
        
        # Subtitle
        subtitle = QLabel("Click Resume to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: rgba(255, 255, 255, 0.7);
                background: transparent;
                font-weight: normal;
                margin-top: 10px;
            }
        """)
        layout.addWidget(subtitle)
        
        self.setLayout(layout)
        self.hide()


class CelebrationWidget(QWidget):
    """Fun celebration animation widget shown when session is completed."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # Different animation types with emojis and messages
        self.animations = {
            'start': {
                'emojis': ["🚀", "🎯", "⚡", "🔥", "💪", "🌟", "🎪", "🎨", "🎵", "🎳"],
                'messages': ["Let's Start!", "Ready to Go!", "Here We Go!", "Game On!", "Let's Rock!", "Time to Shine!", "Action Time!", "Let's Do This!"]
            },
            'resume': {
                'emojis': ["😴", "💤", "🥱", "☕", "🔋", "😊", "👋", "🤗", "😌", "🙂"],
                'messages': ["Welcome Back!", "Refreshed?", "Ready Again!", "Back in Action!", "Let's Continue!", "Feeling Better?", "Nice Break!", "Back to Work!"]
            },
            'completion': {
                'emojis': ["🎉", "🥳", "✨", "🎊", "🏆", "👏", "🎯", "💪", "🌟", "🚀"],
                'messages': ["Excellent Work!", "Mission Complete!", "Well Done!", "Amazing!", "Perfect!", "Outstanding!", "Fantastic!", "Brilliant!"]
            }
        }
        
        # Create main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        # Background with nice gradient and transparency
        self.setStyleSheet("""
            QWidget {
                background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                            stop:0 rgba(76, 175, 80, 0.85),
                            stop:0.7 rgba(56, 142, 60, 0.8),
                            stop:1 rgba(27, 94, 32, 0.75));
                border-radius: 25px;
            }
        """)
        
        # Large emoji
        self.emoji_label = QLabel()
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setStyleSheet("""
            QLabel {
                font-size: 120px;
                background: transparent;
                color: white;
                padding: 20px;
            }
        """)
        layout.addWidget(self.emoji_label)
        
        # Celebration message
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: white;
                background: rgba(0, 0, 0, 0.3);
                padding: 15px 30px;
                border-radius: 15px;
                letter-spacing: 2px;
            }
        """)
        layout.addWidget(self.message_label)
        
        # Stats message
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: white;
                background: rgba(0, 0, 0, 0.2);
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: 500;
            }
        """)
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
        self.hide()
    
    def show_animation(self, animation_type, **kwargs):
        """Show animation based on type."""
        if animation_type not in self.animations:
            return
            
        anim_data = self.animations[animation_type]
        emoji = random.choice(anim_data['emojis'])
        message = random.choice(anim_data['messages'])
        
        # Set content based on animation type
        self.emoji_label.setText(emoji)
        self.message_label.setText(message)
        
        if animation_type == 'completion':
            # For completion, show detailed stats
            confirmed_count = kwargs.get('confirmed_count', 0)
            total_count = kwargs.get('total_count', 0)
            elapsed_time = kwargs.get('elapsed_time', 0)
            
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            self.stats_label.setText(f"Verified {confirmed_count}/{total_count} detections in {time_str}")
            self.stats_label.show()
            
            # Different background for completion
            self.setStyleSheet("""
                QWidget {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                                stop:0 rgba(76, 175, 80, 0.85),
                                stop:0.7 rgba(56, 142, 60, 0.8),
                                stop:1 rgba(27, 94, 32, 0.75));
                    border-radius: 25px;
                }
            """)
            duration = 4000
        elif animation_type == 'start':
            # For start, motivational message
            self.stats_label.setText("Time to verify some amazing work!")
            self.stats_label.show()
            
            # Energetic blue background
            self.setStyleSheet("""
                QWidget {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                                stop:0 rgba(33, 150, 243, 0.85),
                                stop:0.7 rgba(25, 118, 210, 0.8),
                                stop:1 rgba(13, 71, 161, 0.75));
                    border-radius: 25px;
                }
            """)
            duration = 2500
        else:  # resume
            # For resume, simple welcome back
            self.stats_label.setText("Hope you had a nice break!")
            self.stats_label.show()
            
            # Calm purple background
            self.setStyleSheet("""
                QWidget {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                                stop:0 rgba(156, 39, 176, 0.85),
                                stop:0.7 rgba(123, 31, 162, 0.8),
                                stop:1 rgba(74, 20, 140, 0.75));
                    border-radius: 25px;
                }
            """)
            duration = 2000
        
        # Show and animate
        self.show()
        self.raise_()
        
        # Auto-hide after specified duration
        QTimer.singleShot(duration, self.hide)
    
    def show_celebration(self, confirmed_count, total_count, elapsed_time):
        """Show completion celebration - for backward compatibility."""
        self.show_animation('completion', 
                          confirmed_count=confirmed_count, 
                          total_count=total_count, 
                          elapsed_time=elapsed_time)


class SpermVerificationApp(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sperm Cell Verification Tool v1.0")
        self.setMinimumSize(1600, 1000)
        self.resize(1920, 1200)
        
        # Center window on screen
        from PySide6.QtGui import QScreen
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, 
                  (screen.height() - self.height()) // 2)
        
        # Data
        self.annotations_data: List[dict] = []
        self.current_detections: List[dict] = []
        self.confirmed_detections: set = set()
        self.data_root_path: str = ""  # User-specified root path for data
        self.image_lookup_cache: Dict[str, str] = {}  # basename -> resolved path cache
        
        # Click timing tracking
        self.click_timestamps: dict = {}  # detection_id -> timestamp
        self.click_intervals: list = []   # list of time intervals between clicks
        self.last_click_time = None
        
        # Timer
        self.session_start_time: Optional[datetime] = None
        self.total_pause_time = timedelta(0)
        self.pause_start_time: Optional[datetime] = None
        self.is_paused = False
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_display)
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.update_ui_state()
    
    def setup_ui(self):
        """Setup the main user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(3, 3, 3, 3)  # Minimal window margins
        main_layout.setSpacing(2)  # Minimal spacing between sections
        
        # Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Grid of thumbnails
        grid_frame = QFrame()
        grid_frame.setFrameStyle(QFrame.StyledPanel)
        grid_layout = QVBoxLayout(grid_frame)
        grid_layout.setContentsMargins(4, 4, 4, 4)  # Minimal grid panel margins
        
        grid_title = QLabel("Detected Cells")
        grid_title.setFont(QFont("Arial", 12, QFont.Bold))
        grid_layout.addWidget(grid_title)
        
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_scroll.setWidget(self.grid_widget)
        grid_layout.addWidget(self.grid_scroll)
        
        content_splitter.addWidget(grid_frame)
        
        # Right side: Viewfinder
        viewfinder_frame = QFrame()
        viewfinder_frame.setFrameStyle(QFrame.StyledPanel)
        viewfinder_layout = QVBoxLayout(viewfinder_frame)
        viewfinder_layout.setContentsMargins(4, 4, 4, 4)  # Minimal viewfinder margins
        
        viewfinder_title = QLabel("Full Image View (Double-click to zoom)")
        viewfinder_title.setFont(QFont("Arial", 12, QFont.Bold))
        viewfinder_layout.addWidget(viewfinder_title)
        
        # Zoom controls
        zoom_controls = QHBoxLayout()
        zoom_controls.setSpacing(8)
        
        self.zoom_in_btn = QPushButton("🔍+ Zoom In")
        self.zoom_in_btn.setMinimumHeight(32)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_controls.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("🔍- Zoom Out")
        self.zoom_out_btn.setMinimumHeight(32)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_controls.addWidget(self.zoom_out_btn)
        
        self.reset_zoom_btn = QPushButton("🎯 Reset Zoom")
        self.reset_zoom_btn.setMinimumHeight(32)
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        zoom_controls.addWidget(self.reset_zoom_btn)
        
        zoom_controls.addStretch()  # Push buttons to the left
        
        zoom_controls_widget = QWidget()
        zoom_controls_widget.setLayout(zoom_controls)
        viewfinder_layout.addWidget(zoom_controls_widget)
        
        self.viewfinder = ViewfinderWidget()
        viewfinder_layout.addWidget(self.viewfinder)
        
        # Coordinates display
        self.coords_label = QLabel("Coordinates: (x1, y1, x2, y2)")
        viewfinder_layout.addWidget(self.coords_label)
        
        content_splitter.addWidget(viewfinder_frame)
        # Give the grid enough initial width to display 6 columns without overshooting
        content_splitter.setSizes([880, 880])
        content_splitter.setStretchFactor(0, 3)  # grid
        content_splitter.setStretchFactor(1, 5)  # viewfinder
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.timer_label = QLabel("Timer: 00:00:00")
        self.status_label = QLabel("Ready")
        self.progress_label = QLabel("Sperm objects selected: 0/0")
        
        self.status_bar.addWidget(self.timer_label)
        self.status_bar.addPermanentWidget(self.progress_label)
        self.status_bar.addPermanentWidget(self.status_label)
        
        # Pause overlay
        self.pause_overlay = PauseOverlay(central_widget)
        
        # Celebration widget
        self.celebration_widget = CelebrationWidget(central_widget)
    
    def zoom_in(self):
        """Zoom in the viewfinder."""
        self.viewfinder.zoom_in()
    
    def zoom_out(self):
        """Zoom out the viewfinder."""
        self.viewfinder.zoom_out()
    
    def reset_zoom(self):
        """Reset zoom in the viewfinder."""
        self.viewfinder.reset_zoom()
        
    def create_control_panel(self) -> QWidget:
        """Create the control panel with buttons."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setMaximumHeight(50)  # Limit height to compress buttons
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(4, 2, 4, 2)  # Much smaller margins
        layout.setSpacing(4)  # Minimal spacing between buttons
        
        # File operations
        self.load_btn = QPushButton("📁 Browse Annotations")
        self.load_btn.clicked.connect(self.load_annotations)
        layout.addWidget(self.load_btn)
        
        self.load_real_data_btn = QPushButton("🔬 Load Data")
        self.load_real_data_btn.clicked.connect(self.load_real_data)
        layout.addWidget(self.load_real_data_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(self.clear_btn)
        
        layout.addStretch()
        
        # Confidence threshold control
        threshold_label = QLabel("Confidence:")
        layout.addWidget(threshold_label)
        
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.0, 1.0)
        self.threshold_spinbox.setSingleStep(0.05)
        self.threshold_spinbox.setValue(0.5)  # Default threshold
        self.threshold_spinbox.setDecimals(2)
        self.threshold_spinbox.setToolTip("Minimum confidence threshold for displaying detections")
        # Ensure black text in the confidence input
        self.threshold_spinbox.setStyleSheet("color: black;")
        # Don't connect automatic change handler to prevent loops
        layout.addWidget(self.threshold_spinbox)
        
        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.apply_confidence_filter)
        self.apply_filter_btn.setEnabled(False)  # Disabled until data is loaded
        layout.addWidget(self.apply_filter_btn)
        
        layout.addStretch()
        
        # Timer controls
        self.start_btn = QPushButton("Start Session")
        self.start_btn.clicked.connect(self.start_session)
        layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("Stop & Export")
        self.stop_btn.clicked.connect(self.stop_and_export)
        layout.addWidget(self.stop_btn)
        
        return panel
    
    def setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        load_action = file_menu.addAction("Load Annotations")
        load_action.triggered.connect(self.load_annotations)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
    
    def load_annotations(self):
        """Load annotations from JSON file (single dialog)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Annotations JSON File",
            str(APP_DIRECTORY) if APP_DIRECTORY else str(Path.home()),
            "JSON Files (*.json)"
        )
        if not file_path:
            return
        try:
            # Set JSON path and data root to the JSON's folder
            self.json_file_path = file_path
            self.data_root_path = str(Path(file_path).parent)

            with open(file_path, 'r') as f:
                self.annotations_data = json.load(f)

            self.process_annotations()
            self.update_ui_state()
            self.apply_filter_btn.setEnabled(True)
            self.status_label.setText(f"Loaded {len(self.current_detections)} detections")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load annotations:\n{str(e)}")
    
    def load_real_data(self):
        """Load data file (single JSON dialog only)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load JSON Annotations File",
            str(APP_DIRECTORY) if APP_DIRECTORY else str(Path.home()),
            "JSON Files (*.json)"
        )
        if not file_path:
            return

        # Disable button and show loading status
        self.load_real_data_btn.setEnabled(False)
        self.load_real_data_btn.setText("⏳ Loading...")
        self.status_label.setText("Loading data file...")
        QApplication.processEvents()

        try:
            # Set JSON path and data root to the JSON's folder
            self.json_file_path = file_path
            self.data_root_path = str(Path(file_path).parent)

            self.status_label.setText("Reading JSON file...")
            QApplication.processEvents()
            with open(file_path, 'r') as f:
                self.annotations_data = json.load(f)

            self.status_label.setText("Processing detections...")
            QApplication.processEvents()

            self.process_annotations()
            self.update_ui_state()

            # Re-enable button and enable filter
            self.load_real_data_btn.setEnabled(True)
            self.load_real_data_btn.setText("🔬 Load Data")
            self.apply_filter_btn.setEnabled(True)

            self.status_label.setText(
                f"✅ Loaded {len(self.current_detections)} detections from {len(self.annotations_data)} images"
            )

        except Exception as e:
            # Re-enable button on error
            self.load_real_data_btn.setEnabled(True)
            self.load_real_data_btn.setText("🔬 Load Data")
            self.status_label.setText("❌ Failed to load data")
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{str(e)}")
    

    def process_annotations(self):
        """Process loaded annotations and create detection list."""
        self.current_detections = []
        self.confirmed_detections = set()
        
        # Get JSON directory for resolving relative paths
        json_dir = Path(getattr(self, 'json_file_path', '.')).parent
        
        for image_entry in self.annotations_data:
            image_path = image_entry.get("image_path", "")
            # Resolve the image path relative to the JSON file location
            resolved_image_path = self.resolve_image_path(image_path, json_dir)
            
            # Handle both formats: old dummy data and real data
            if "detections" in image_entry:
                # Old dummy data format
                detections = image_entry.get("detections", [])
                for i, detection in enumerate(detections):
                    # Apply confidence threshold filter
                    threshold = getattr(self, 'threshold_spinbox', None)
                    min_confidence = threshold.value() if threshold else 0.5
                    confidence = detection.get("confidence", 0.0)
                    
                    if confidence >= min_confidence:
                        detection_id = f"{Path(image_path).name}_{i}"
                        detection_data = {
                            "id": detection_id,
                            "image_path": resolved_image_path,
                            "bbox": detection["bbox"],
                            "confidence": confidence,
                            "cell_id": detection.get("cell_id", f"cell_{i}")
                        }
                        self.current_detections.append(detection_data)
            else:
                # Real data format: pred_boxes and pred_scores
                pred_boxes = image_entry.get("pred_boxes", [])
                pred_scores = image_entry.get("pred_scores", [])
                
                for i, (bbox, score) in enumerate(zip(pred_boxes, pred_scores)):
                    # Apply confidence threshold filter
                    threshold = getattr(self, 'threshold_spinbox', None)
                    min_confidence = threshold.value() if threshold else 0.5
                    
                    if score >= min_confidence:
                        detection_id = f"{Path(image_path).name}_{i}"
                        detection_data = {
                            "id": detection_id,
                            "image_path": resolved_image_path,
                            "bbox": bbox,  # bbox is already [x1, y1, x2, y2]
                            "confidence": score,
                            "cell_id": f"sperm_{i+1}"
                        }
                        self.current_detections.append(detection_data)
        
        self.populate_grid()
    
    def resolve_image_path(self, image_path: str, json_dir: Path) -> str:
        """Resolve image path relative to JSON directory with robust fallbacks.
        Supports layouts like: json_dir/some_folder_name/images/filename.ext
        """
        img_path = Path(image_path)

        # 0) Absolute path that exists
        if img_path.is_absolute() and img_path.exists():
            return str(img_path)

        basename = img_path.name

        # 1) Base root: user-chosen root if set, else the JSON's directory
        root = Path(self.data_root_path) if self.data_root_path else json_dir

        # 2) Try original relative path rebased to root (handles './...')
        rebased = (root / image_path.lstrip("./")).resolve()
        if rebased.exists():
            return str(rebased)

        # 3) Cached lookup by basename
        cached = self.image_lookup_cache.get(basename)
        if cached and Path(cached).exists():
            return cached

        # 4) Prefer matches inside an 'images' directory under root
        for p in root.rglob(basename):
            if p.parent.name.lower() == "images":
                self.image_lookup_cache[basename] = str(p)
                return str(p)

        # 5) Fallback: any basename match under root
        for p in root.rglob(basename):
            self.image_lookup_cache[basename] = str(p)
            return str(p)

        # 6) Give up: return original path (will error on load)
        return image_path

    def apply_confidence_filter(self):
        """Apply confidence threshold filter to loaded data."""
        if not hasattr(self, 'annotations_data') or not self.annotations_data:
            QMessageBox.warning(self, "No Data", "Please load data first before applying filters.")
            return
        
        # Reprocess annotations with new threshold
        self.process_annotations()
        self.update_ui_state()
        threshold = self.threshold_spinbox.value()
        total_filtered = len(self.current_detections)
        self.status_label.setText(f"✅ Filtered: {total_filtered} detections with confidence ≥ {threshold:.2f}")
    
    def populate_grid(self):
        """Populate the grid with detection thumbnails."""
        # Clear existing grid
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        self.status_label.setText("Creating thumbnails...")
        QApplication.processEvents()
        
        # Sort detections by confidence (highest first)
        sorted_detections = sorted(self.current_detections, 
                                 key=lambda x: x.get('confidence', 0), 
                                 reverse=True)
        
        # Add thumbnails with progress feedback
        cols = 6  # Fewer columns for larger thumbnails
        total_detections = len(sorted_detections)
        
        for i, detection in enumerate(sorted_detections):
            # Show progress every 50 thumbnails
            if i % 50 == 0:
                self.status_label.setText(f"Creating thumbnails... {i}/{total_detections}")
                QApplication.processEvents()
            
            row, col = divmod(i, cols)
            
            thumbnail = DetectionThumbnail(detection, thumbnail_size=120)  # Much larger thumbnails
            thumbnail.clicked.connect(self.on_thumbnail_clicked)
            thumbnail.hovered.connect(self.on_thumbnail_hovered)
            
            # Load and set thumbnail image
            self.load_thumbnail(thumbnail, detection)
            
            self.grid_layout.addWidget(thumbnail, row, col)
    
    def load_thumbnail(self, thumbnail: DetectionThumbnail, detection: dict):
        """Load thumbnail image for detection (cropped only)."""
        try:
            image_path = detection["image_path"]
            bbox = detection["bbox"]
            
            # Load image and crop - simple, no conversions
            img = Image.open(image_path).convert("RGB")
            x1, y1, x2, y2 = bbox
            
            # Crop exactly to bounding box (no padding for thumbnail)
            cropped = img.crop((x1, y1, x2, y2))
            
            # Convert PIL Image directly to QPixmap
            import io
            buffer = io.BytesIO()
            cropped.save(buffer, format='PNG')
            buffer.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            thumbnail.set_thumbnail(pixmap)
            
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            # Set placeholder
            thumbnail.setText("No Image")
    
    def on_thumbnail_clicked(self, detection: dict):
        """Handle thumbnail click (confirm/unconfirm)."""
        # Don't allow annotation before session starts
        if not self.session_start_time:
            QMessageBox.warning(self, "Session Not Started", 
                              "Please start a session before annotating detections.")
            return
            
        detection_id = detection["id"]
        current_time = datetime.now()
        
        if detection_id in self.confirmed_detections:
            self.confirmed_detections.remove(detection_id)
            confirmed = False
            # Remove timestamp when unconfirming
            if detection_id in self.click_timestamps:
                del self.click_timestamps[detection_id]
        else:
            self.confirmed_detections.add(detection_id)
            confirmed = True
            
            # Record click timestamp
            self.click_timestamps[detection_id] = current_time
            
            # Calculate interval since last click
            if self.last_click_time:
                interval = (current_time - self.last_click_time).total_seconds()
                self.click_intervals.append(interval)
            
            self.last_click_time = current_time
        
        # Update thumbnail appearance
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, DetectionThumbnail) and widget.detection_data["id"] == detection_id:
                widget.set_confirmed(confirmed)
                break
        
        self.update_progress()
    
    def on_thumbnail_hovered(self, detection: dict):
        """Handle thumbnail hover (show full image in viewfinder)."""
        try:
            # Show full image with bounding box overlay
            image_path = detection["image_path"]
            bbox = detection["bbox"]
            
            self.viewfinder.set_image(image_path, bbox)
            
            # Update coordinates
            self.coords_label.setText(f"Coordinates: ({bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]})")
            
        except Exception as e:
            print(f"Error loading viewfinder image: {e}")
            self.viewfinder.clear_image()
    
    def start_session(self):
        """Start verification session with timer."""
        if not self.current_detections:
            QMessageBox.warning(self, "Warning", "Please load annotations first.")
            return
        
        self.session_start_time = datetime.now()
        self.total_pause_time = timedelta(0)
        self.is_paused = False
        
        # Reset click timing data for new session
        self.click_timestamps.clear()
        self.click_intervals.clear()
        self.last_click_time = None
        
        self.timer.start(1000)  # Update every second
        self.update_ui_state()
        self.status_label.setText("Session started")
        
        # Show start animation
        self.celebration_widget.show_animation('start')
    
    def toggle_pause(self):
        """Toggle pause state."""
        if not self.session_start_time:
            return
        
        if self.is_paused:
            # Resume
            if self.pause_start_time:
                self.total_pause_time += datetime.now() - self.pause_start_time
                self.pause_start_time = None
            self.is_paused = False
            self.pause_overlay.hide()
            self.timer.start(1000)
            
            # Show resume animation
            self.celebration_widget.show_animation('resume')
        else:
            # Pause
            self.pause_start_time = datetime.now()
            self.is_paused = True
            self.pause_overlay.show()
            self.pause_overlay.raise_()
            # Allow interaction with buttons by not setting focus policy
            self.pause_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            self.timer.stop()
        
        self.update_ui_state()
    
    def stop_and_export(self):
        """Stop session and export results."""
        if not self.session_start_time:
            QMessageBox.warning(self, "Warning", "No active session.")
            return
        
        session_end_time = datetime.now()
        total_time = session_end_time - self.session_start_time - self.total_pause_time
        
        if self.is_paused and self.pause_start_time:
            total_time -= datetime.now() - self.pause_start_time
        
        self.timer.stop()
        self.export_results(total_time)
        
        # Show celebration animation
        confirmed_count = len(self.confirmed_detections)
        total_count = len(self.current_detections)
        elapsed_seconds = total_time.total_seconds()
        self.celebration_widget.show_celebration(confirmed_count, total_count, elapsed_seconds)
        
        # Reset
        self.session_start_time = None
        self.is_paused = False
        self.pause_overlay.hide()
        self.update_ui_state()
    
    def export_results(self, total_time: timedelta):
        """Export verification results to Excel."""
        if not self.confirmed_detections:
            QMessageBox.information(self, "Export", "No confirmations to export.")
            return
        
        # Prepare data with click timing
        export_data = []
        sorted_confirmations = sorted(self.click_timestamps.items(), key=lambda x: x[1])  # Sort by timestamp
        
        for i, (detection_id, click_time) in enumerate(sorted_confirmations):
            # Find the detection data
            detection = None
            for det in self.current_detections:
                if det["id"] == detection_id:
                    detection = det
                    break
            
            if detection:
                bbox = detection["bbox"]
                
                # Calculate time since session start
                time_since_start = (click_time - self.session_start_time).total_seconds()
                
                # Get interval from previous click (if any)
                interval_from_previous = self.click_intervals[i-1] if i > 0 and i-1 < len(self.click_intervals) else 0
                
                export_data.append({
                    "click_order": i + 1,
                    "image_path": detection["image_path"],
                    "detection_id": detection["id"],
                    "cell_id": detection["cell_id"],
                    "x1": bbox[0],
                    "y1": bbox[1],
                    "x2": bbox[2],
                    "y2": bbox[3],
                    "confidence": detection["confidence"],
                    "verified": True,
                    "click_timestamp": click_time.strftime("%H:%M:%S.%f")[:-3],  # HH:MM:SS.mmm
                    "time_since_start_seconds": round(time_since_start, 3),
                    "interval_from_previous_seconds": round(interval_from_previous, 3),
                    "session_duration": str(total_time),
                    "export_time": datetime.now().isoformat()
                })
        
        # Save to Excel
        df = pd.DataFrame(export_data)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", f"verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                # Create Excel file with multiple sheets
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Main data sheet
                    df.to_excel(writer, sheet_name='Verification Results', index=False)
                    
                    # Summary statistics sheet
                    if self.click_intervals:
                        avg_interval = sum(self.click_intervals) / len(self.click_intervals)
                        min_interval = min(self.click_intervals)
                        max_interval = max(self.click_intervals)
                    else:
                        avg_interval = min_interval = max_interval = 0
                    
                    summary_data = {
                        'Metric': [
                            'Total Confirmed Detections',
                            'Total Session Duration',
                            'Total Clicks Made',
                            'Average Time Between Clicks (seconds)',
                            'Minimum Time Between Clicks (seconds)',
                            'Maximum Time Between Clicks (seconds)',
                            'First Click Time',
                            'Last Click Time',
                            'Total Active Annotation Time (seconds)'
                        ],
                        'Value': [
                            len(export_data),
                            str(total_time),
                            len(self.click_intervals) + 1,  # +1 for first click
                            round(avg_interval, 3),
                            round(min_interval, 3),
                            round(max_interval, 3),
                            sorted_confirmations[0][1].strftime("%H:%M:%S") if sorted_confirmations else "N/A",
                            sorted_confirmations[-1][1].strftime("%H:%M:%S") if sorted_confirmations else "N/A",
                            round(sum(self.click_intervals), 3) if self.click_intervals else 0
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Session Summary', index=False)
                
                QMessageBox.information(
                    self, "Export Complete",
                    f"Results exported successfully!\n\n"
                    f"Confirmed detections: {len(export_data)}\n"
                    f"Session duration: {total_time}\n"
                    f"Average time between clicks: {avg_interval:.2f}s\n"
                    f"File: {file_path}"
                )
                self.status_label.setText(f"Exported {len(export_data)} confirmations")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export results:\n{str(e)}")
    
    def clear_all(self):
        """Clear all data and reset application."""
        reply = QMessageBox.question(
            self, "Clear All", "Are you sure you want to clear all data?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.annotations_data = []
            self.current_detections = []
            self.confirmed_detections = set()
            self.data_root_path = ""  # Reset root path
            
            # Reset click timing data
            self.click_timestamps.clear()
            self.click_intervals.clear()
            self.last_click_time = None
            
            # Clear grid
            for i in reversed(range(self.grid_layout.count())):
                self.grid_layout.itemAt(i).widget().setParent(None)
            
            # Reset timer
            if self.timer.isActive():
                self.timer.stop()
            self.session_start_time = None
            self.is_paused = False
            self.pause_overlay.hide()
            
            # Reset UI
            self.viewfinder.clear_image()
            self.coords_label.setText("Coordinates: (x1, y1, x2, y2)")
            self.update_ui_state()
            self.status_label.setText("Cleared all data")
    
    def update_timer_display(self):
        """Update timer display."""
        if not self.session_start_time:
            return
        
        current_time = datetime.now()
        elapsed = current_time - self.session_start_time - self.total_pause_time
        
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        self.timer_label.setText(f"Timer: {hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def update_progress(self):
        """Update progress display."""
        total = len(self.current_detections)
        confirmed = len(self.confirmed_detections)
        self.progress_label.setText(f"Sperm objects selected: {confirmed}/{total}")
    
    def update_ui_state(self):
        """Update UI element states based on current state."""
        has_data = bool(self.current_detections)
        session_active = self.session_start_time is not None
        
        self.start_btn.setEnabled(has_data and not session_active)
        self.pause_btn.setEnabled(session_active)
        self.stop_btn.setEnabled(session_active)
        self.pause_btn.setText("Resume" if self.is_paused else "Pause")
        
        self.update_progress()
        
        if not session_active:
            self.timer_label.setText("Timer: 00:00:00")
    
    def resizeEvent(self, event):
        """Handle window resize."""
        super().resizeEvent(event)
        if hasattr(self, 'pause_overlay'):
            # Position overlay to cover content area but not control panel
            content_rect = self.centralWidget().rect()
            control_height = 60  # Approximate height of control panel
            overlay_rect = content_rect.adjusted(0, control_height, 0, 0)
            self.pause_overlay.setGeometry(overlay_rect)
        
        if hasattr(self, 'celebration_widget'):
            # Center celebration widget in the main area
            content_rect = self.centralWidget().rect()
            widget_width, widget_height = 500, 400
            x = (content_rect.width() - widget_width) // 2
            y = (content_rect.height() - widget_height) // 2
            self.celebration_widget.setGeometry(x, y, widget_width, widget_height)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About",
            "Sperm Cell Verification Tool v1.0\n\n"
            "A tool for manually verifying neural network predictions\n"
            "of sperm cell detections in microscopy images.\n\n"
            "Built with PySide6 and Python."
        )


def get_app_directory():
    """Get the directory where the app executable is located"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle - use executable's directory
        if sys.platform == 'darwin':  # macOS
            # For .app bundles, go up to the directory containing the .app
            app_path = Path(sys.executable).parent.parent.parent  # Contents/MacOS → Contents → App.app → parent
        else:  # Windows
            app_path = Path(sys.executable).parent
        print(f"📦 Running as bundled app from: {app_path}")
        return app_path
    else:
        # Running as script - project root directory for development
        script_dir = Path(__file__).parent.absolute()  # standalone_app directory
        project_root = script_dir.parent  # NOA_image_app directory
        print(f"🐍 Running as script from: {project_root}")
        return project_root

def main():
    """Main application entry point."""
    # Get the app directory and set global variable for data access
    global APP_DIRECTORY
    APP_DIRECTORY = get_app_directory()
    
    # Don't change working directory in bundled app - let users work from their current location
    if not getattr(sys, 'frozen', False):
        # Only change directory when running as script for development
        os.chdir(APP_DIRECTORY)
    
    print(f"✅ Working directory: {Path.cwd()}")
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Sperm Verification Tool")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Research Lab")
    
    # Apply beautiful modern theme
    apply_modern_theme(app)
    
    # Create and show main window
    window = SpermVerificationApp()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
