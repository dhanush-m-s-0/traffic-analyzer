# Building Traffic Analyzer from Source

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Runtime |
| PyInstaller | 6.8+ | EXE packaging |
| NSIS | 3.x | Windows installer |
| Git | any | Source control |

## Quick Build

```bash
# Install build dependencies
pip install -r requirements.txt

# Build standalone EXE
python build_exe.py

# Output:
# dist/traffic-analyzer.exe        ← standalone EXE
# dist/traffic-analyzer-portable/  ← portable bundle folder
# dist/traffic-analyzer-portable.zip ← distribution ZIP
```

## Step-by-Step

### 1 – Install Python dependencies

```bash
pip install pyinstaller pillow
pip install -r requirements.txt
```

### 2 – (Optional) Create an application icon

Place a 256×256 `.ico` file at `traffic-analyzer.ico` in the project root.
You can convert a PNG with:

```bash
python -c "
from PIL import Image
img = Image.open('icon.png').resize((256,256))
img.save('traffic-analyzer.ico')
"
```

### 3 – Build the EXE

```bash
python build_exe.py
```

Flags:
- `--clean`   Remove previous build artefacts first
- `--no-zip`  Skip creating the portable ZIP

### 4 – Build the NSIS Installer (Windows only)

```
makensis build_installer.nsi
```

Output: `dist/traffic-analyzer-setup.exe`

### 5 – Create the distribution ZIP manually

```bash
python -c "
import shutil, pathlib
shutil.make_archive('traffic-analyzer-dist', 'zip', 'dist')
"
```

## CI / Automated Builds

The recommended CI pipeline (GitHub Actions):

```yaml
- uses: actions/setup-python@v5
  with: { python-version: '3.11' }
- run: pip install -r requirements.txt pyinstaller
- run: python build_exe.py --clean
- uses: actions/upload-artifact@v4
  with:
    name: traffic-analyzer-windows
    path: dist/traffic-analyzer-portable.zip
```

## Troubleshooting Builds

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` in EXE | Add module to `hiddenimports` in `build_exe.py` |
| EXE flagged by antivirus | Sign the EXE with a code-signing certificate |
| Large EXE size | Enable UPX compression (set `upx=True` in spec) |
| Missing frontend files | Ensure `datas` list in spec includes `('frontend', 'frontend')` |
