# Changelog

All notable changes to Traffic Analyzer are documented here.
This project follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] – 2024-06-01

### Added
- **Desktop GUI** – Tkinter application window with status display, Start/Stop controls, settings dialog, and activity log.
- **System Tray** – Minimise to tray, context menu with quick actions (pystray + Pillow).
- **Background Server** – Embedded FastAPI server managed as a subprocess with health monitoring.
- **Web Interface** – Responsive dark-theme frontend (HTML / CSS / JS) served by the embedded API.
  - Home page with Traffic Analysis and Route Optimisation forms.
  - Live Dashboard with stats and history.
  - Real-time API health indicator.
- **REST API** (FastAPI)
  - `POST /api/analyze` – AI traffic analysis
  - `POST /api/optimize-route` – Route optimisation
  - `GET  /api/congestion/{location}` – Quick congestion check
  - `GET  /api/weather/{location}` – Weather impact
  - `POST /api/alerts` – Create alert
  - `GET  /api/alerts` – List alerts
  - `GET  /api/history` – Analysis history
  - `GET  /api/health` – Health check
- **CLI** (Click) – Full command-line interface matching all API features.
- **Groq LLM integration** – Ultra-fast AI inference via `groq` Python SDK.
- **Build system** – `build_exe.py` PyInstaller script + `build_installer.nsi` NSIS installer.
- **Quick-start scripts** – `run.bat` (Windows) and `run.sh` (Linux/macOS).
- **Documentation** – README, README_EXE, INSTALL, BUILD, CHANGELOG, LICENSE.

---
