# NOA Grid App – Project Memory

Last Updated: 2025-08-13 11:00

## Goal
- Standalone desktop app (Windows/macOS) to review sperm detections and export confirmations with timing data.

## Decisions
- Stack: Python (PySide6/Qt), OpenCV + Pillow + NumPy; packaged with PyInstaller; fully offline.
- Inputs: PNG/JPG/TIFF (single-page). Typical 1920x1440 or 2084x2084. 16 bpp, RGB assumed.
- Annotations: JSON dataset file; image filename inside JSON; multiple boxes per image; pixels origin top-left; bbox = (xmin, ymin, xmax, ymax); include confidence with UI filter.
- Cropping: 100% padding on all sides; force square; pad outside image with black. Viewfinder target 512 px.
- Grid & nav: Default 10x10 grid; auto-fit to window; pagination; arrow keys navigate.
- Hover/viewfinder: Hover grid item shows padded crop in right panel; no bbox overlay; coordinates text below; mouse wheel over grid item zooms viewfinder.
- Confirm flow: Click toggles confirmed (green highlight). Only confirmed vs unconfirmed. No persistence; export on Stop/OK.
- Timer: Start/Pause/Stop. Paused state obfuscates images and disables interaction. Display hh:mm:ss. Record started_at, pause/resume timestamps, ended_at, elapsed.
- Output: Auto-save next to images as CSV or XLSX. Only confirmed rows with: image_path, box_id, xmin, ymin, xmax, ymax, started_at, ended_at, elapsed_time, reviewer_id.
- Performance: Lazy load/crop on demand with on-disk cache; keep RAM usage ≤ 70%; offline only.
- Look & feel: Modern, clean UI with subtle gradients (Apple-like).
- Controls: Load Images, Load JSON, Start, Pause, Stop/OK, Clear.

## Open Questions / Dependencies
- Need sample JSON schema to finalize parser (keys: image path, detections list, bbox, confidence, box ids).
- Reviewer ID entry method: simple text field at session start (assumed).

## Planned Work
1. Scaffold PySide6 app: main window, grid panel, viewfinder, toolbar, status bar, timer display.
2. JSON loader (after schema), image loader (16-bit safe), confidence filter.
3. Cropper: pad-by-100%, force square, black padding; caching (LRU + disk).
4. Grid pagination + lazy rendering; hover viewfinder with wheel-to-zoom.
5. Selection/confirmation model; keyboard navigation.
6. Timer with pause overlay and event logging.
7. Exporter (CSV/XLSX) auto-saved next to images; reviewer id capture.
8. Packaging for macOS & Windows.

## Notes
- GPU not required; keep CPU/memory within 70% RAM.
