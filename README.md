# NOA Grid App

Standalone reviewer for detections produced by a DNN. Cross-platform (macOS/Windows/Linux). Offline.

## Setup (dev)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m noa_app
```

## Packaging (local)

```bash
pyinstaller --noconfirm --windowed --name NOAGridApp noa_app/__main__.py
```

## CI Demo Builds

- Push a tag starting with `demo-` to trigger cross-platform builds.
- Artifacts will appear in the GitHub Actions run as downloadable zips.

```bash
git tag demo-0.1.0
git push origin demo-0.1.0
```
