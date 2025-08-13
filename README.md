# NOA Grid App

Standalone reviewer for detections produced by a DNN. Cross-platform (macOS/Windows). Offline.

## Setup

- Python 3.11 recommended.
- Create venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run (dev)

```bash
python -m noa_app
```

## Package

```bash
pyinstaller --noconfirm --windowed --name NOAGridApp noa_app/__main__.py
```

Artifacts in `dist/NOAGridApp`.
