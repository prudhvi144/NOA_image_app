Build and signing overview (macOS, Windows, Linux)

Prereqs
- Python 3.11 on all runners
- Secrets in repo settings if signing/notarization is required:
  - Windows: WIN_CERT_PFX (base64), WIN_CERT_PASSWORD
  - macOS: MACOS_CERT_P12 (base64), MACOS_CERT_PASSWORD, MACOS_DEVELOPER_ID_APP, MACOS_TEAM_ID, MACOS_NOTARIZATION_APPLE_ID, MACOS_NOTARIZATION_PASSWORD

Local test build
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm --windowed --name SpermVerificationApp standalone_app/run_app.py
```

CI builds
- Push a tag `demo-*` to trigger the workflow `.github/workflows/build.yml`
- Outputs under Actions artifacts per OS

Gatekeeper/SmartScreen
- macOS: provide Developer ID Application cert; workflow will codesign, zip, notarize, and staple
- Windows: provide Authenticode PFX; workflow will sign the EXE inside `dist/SpermVerificationApp`

Linux
- No signing standard; artifact is a zipped PyInstaller folder, compatible with glibc-based distros similar to Ubuntu 22.04


