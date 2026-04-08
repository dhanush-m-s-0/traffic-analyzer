"""PyInstaller build script for Traffic Analyzer Windows EXE."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"
SPEC_FILE = ROOT / "traffic_analyzer.spec"


# ---------------------------------------------------------------------------
# PyInstaller spec content
# ---------------------------------------------------------------------------

SPEC_CONTENT = """\
# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(SPEC.split("\\\\")[0]).resolve() if hasattr(sys, 'frozen') else Path('.').resolve()

a = Analysis(
    ['src/main_app.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        ('frontend', 'frontend'),
        ('config', 'config'),
        ('api', 'api'),
        ('cli', 'cli'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'starlette',
        'pydantic',
        'groq',
        'langchain',
        'sqlalchemy',
        'aiofiles',
        'multiprocessing',
        'tkinter',
        'tkinter.ttk',
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'psutil',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'IPython', 'jupyter'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='traffic-analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='traffic-analyzer.ico',
    version_file=None,
    uac_admin=False,
)
"""


def clean() -> None:
    """Remove previous build artefacts."""
    for d in (DIST_DIR, BUILD_DIR):
        if d.exists():
            shutil.rmtree(d)
            print(f"Cleaned: {d}")
    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"Removed: {SPEC_FILE}")


def write_spec() -> None:
    """Write the PyInstaller spec file."""
    SPEC_FILE.write_text(SPEC_CONTENT, encoding="utf-8")
    print(f"Spec written: {SPEC_FILE}")


def build() -> None:
    """Run PyInstaller."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC_FILE),
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT), check=False)
    if result.returncode != 0:
        print("PyInstaller failed.", file=sys.stderr)
        sys.exit(result.returncode)
    print("Build complete → dist/traffic-analyzer.exe")


def create_portable_zip() -> None:
    """Bundle the EXE + docs into a portable ZIP."""
    zip_path = DIST_DIR / "traffic-analyzer-portable"
    bundle = zip_path
    bundle.mkdir(parents=True, exist_ok=True)

    exe = DIST_DIR / "traffic-analyzer.exe"
    if exe.exists():
        shutil.copy(exe, bundle / "traffic-analyzer-portable.exe")

    for doc in ("README.md", "README_EXE.md", "INSTALL.md", "CHANGELOG.md", "LICENSE.md", ".env.example"):
        src = ROOT / doc
        if src.exists():
            shutil.copy(src, bundle / doc)

    shutil.make_archive(str(zip_path), "zip", str(bundle))
    print(f"Portable ZIP: {zip_path}.zip")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build Traffic Analyzer Windows EXE")
    parser.add_argument("--clean", action="store_true", help="Clean build artefacts")
    parser.add_argument("--no-zip", action="store_true", help="Skip portable ZIP creation")
    args = parser.parse_args()

    if args.clean:
        clean()

    write_spec()
    build()

    if not args.no_zip:
        create_portable_zip()

    print("\nDone! Find your EXE in: dist/")
