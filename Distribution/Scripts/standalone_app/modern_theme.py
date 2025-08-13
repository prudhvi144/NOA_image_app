#!/usr/bin/env python3
"""
Modern Medical Theme for Sperm Verification App
Clean, professional styling with subtle animations and modern design.
"""

def get_modern_stylesheet() -> str:
    """Return the complete modern stylesheet for the application."""
    return """
    /* ===== MAIN WINDOW ===== */
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #f8f9fa, stop:0.3 #ffffff, stop:0.7 #f1f3f4, stop:1 #e8eaed);
        color: #1a1a1a;
    }
    
    /* ===== FRAMES AND PANELS ===== */
    QFrame {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 12px;
        padding: 8px;
    }
    
    QFrame[frameShape="4"] { /* StyledPanel */
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(248, 249, 250, 0.90));
        border: 1px solid rgba(108, 117, 125, 0.15);
        border-radius: 20px;

    }
    
    /* ===== BUTTONS ===== */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4285f4, stop:1 #1565c0);
        border: none;
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        min-width: 70px;
        max-height: 36px;
        margin: 2px;

    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a95f5, stop:1 #1976d2);

    }
    
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3367d6, stop:1 #0d47a1);

    }
    
    QPushButton:disabled {
        background: #6c757d;
        color: rgba(255, 255, 255, 0.6);
    }
    
    /* Special button styles */
    QPushButton[text="Start Session"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #1e7e34);
    }
    
    QPushButton[text="Start Session"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #32bd4a, stop:1 #228b3d);
    }
    
    QPushButton[text="Pause"], QPushButton[text="Resume"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffc107, stop:1 #e0a800);
        color: #212529;
    }
    
    QPushButton[text="Pause"]:hover, QPushButton[text="Resume"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffcd3c, stop:1 #e6b800);
    }
    
    QPushButton[text="Stop & Export"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc3545, stop:1 #c82333);
    }
    
    QPushButton[text="Stop & Export"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e04555, stop:1 #d32535);
    }
    
    QPushButton[text="Clear All"] {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c757d, stop:1 #5a6268);
    }
    
    QPushButton[text="Clear All"]:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #78848b, stop:1 #636c72);
    }
    
    /* ===== LABELS ===== */
    QLabel {
        color: #212529;
        font-size: 14px;
    }
    
    QLabel[text*="Timer:"] {
        background: rgba(40, 167, 69, 0.1);
        border: 1px solid rgba(40, 167, 69, 0.3);
        border-radius: 6px;
        padding: 8px 12px;
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 16px;
        font-weight: bold;
        color: #155724;
    }
    
    QLabel[text*="Progress:"] {
        background: rgba(0, 123, 255, 0.1);
        border: 1px solid rgba(0, 123, 255, 0.3);
        border-radius: 6px;
        padding: 6px 10px;
        font-weight: 600;
        color: #004085;
    }
    
    /* Title labels */
    QLabel[text="Detected Cells"], QLabel[text*="Full Image View"] {
        font-size: 16px;
        font-weight: bold;
        color: #495057;
        padding: 8px 0px;
        border: none;
        background: transparent;
    }
    
    /* ===== SCROLL AREAS ===== */
    QScrollArea {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(108, 117, 125, 0.2);
        border-radius: 12px;
    }
    
    QScrollBar:vertical {
        background: rgba(248, 249, 250, 0.8);
        width: 12px;
        border-radius: 6px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background: rgba(108, 117, 125, 0.5);
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: rgba(108, 117, 125, 0.7);
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background: rgba(248, 249, 250, 0.8);
        height: 12px;
        border-radius: 6px;
        margin: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background: rgba(108, 117, 125, 0.5);
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background: rgba(108, 117, 125, 0.7);
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    /* ===== SPIN BOX ===== */
    QDoubleSpinBox {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 6px;
        padding: 6px 8px;
        font-size: 14px;
        min-width: 80px;
    }
    
    QDoubleSpinBox:focus {
        border-color: #007bff;
        background: #fff;
    }
    
    /* ===== MENU BAR ===== */
    QMenuBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
        border-bottom: 1px solid #dee2e6;
        padding: 4px;
    }
    
    QMenuBar::item {
        background: transparent;
        padding: 8px 16px;
        border-radius: 6px;
        color: #495057;
    }
    
    QMenuBar::item:selected {
        background: rgba(0, 123, 255, 0.1);
        color: #007bff;
    }
    
    QMenu {
        background: white;
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 16px;
        border-radius: 4px;
    }
    
    QMenu::item:selected {
        background: #007bff;
        color: white;
    }
    
    /* ===== TOOLBAR ===== */
    QToolBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(248, 249, 250, 0.9));
        border: 1px solid rgba(108, 117, 125, 0.2);
        border-radius: 12px;
        padding: 8px;
        spacing: 8px;
    }
    
    QToolBar::separator {
        background: rgba(108, 117, 125, 0.3);
        width: 1px;
        margin: 4px;
    }
    
    /* ===== STATUS BAR ===== */
    QStatusBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
        border-top: 1px solid #dee2e6;
        padding: 4px;
    }
    
    QStatusBar::item {
        border: none;
    }
    
    QStatusBar QLabel {
        padding: 4px 8px;
        border-radius: 4px;
    }
    
    /* ===== SPLITTER ===== */
    QSplitter::handle {
        background: rgba(108, 117, 125, 0.3);
        border-radius: 2px;
    }
    
    QSplitter::handle:horizontal {
        width: 3px;
        margin: 2px 0px;
    }
    
    QSplitter::handle:vertical {
        height: 3px;
        margin: 0px 2px;
    }
    
    QSplitter::handle:hover {
        background: rgba(0, 123, 255, 0.5);
    }
    """


def apply_modern_theme(app):
    """Apply the modern theme to the Qt application."""
    # Set the modern stylesheet
    app.setStyleSheet(get_modern_stylesheet())
    
    # Set application-wide font
    from PySide6.QtGui import QFont
    font = QFont("SF Pro Display", 10)  # macOS system font
    if not font.exactMatch():
        font = QFont("Segoe UI", 10)    # Windows system font
    if not font.exactMatch():
        font = QFont("Ubuntu", 10)      # Linux system font
    if not font.exactMatch():
        font = QFont("Arial", 10)       # Fallback
    
    app.setFont(font)
