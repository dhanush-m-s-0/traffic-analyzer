# Traffic Analyzer – Windows EXE User Guide

## Quick Start

1. **Download** `traffic-analyzer-portable.exe` (no installation needed).
2. **Double-click** the EXE to launch.
3. The desktop application window opens automatically.
4. Click **▶ Start Server** to launch the embedded API.
5. Your default browser opens the web interface at `http://127.0.0.1:8000`.

## First-time Setup

On first launch you will be prompted to enter your Groq API key:

1. Open **Settings** (⚙ button in the app).
2. Paste your Groq API key (`gsk_…`).
3. Click **Save** and restart the server.

Get a free key at <https://console.groq.com/keys>.

## System Tray

- The app minimises to the system tray when you close the window.
- Right-click the tray icon for quick actions:
  - Open Web Interface
  - Show Window
  - Start / Stop Server
  - Quit

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Port 8000 in use" | Change `API_PORT` in Settings or close the other app. |
| No AI responses | Check your `GROQ_API_KEY` in Settings. |
| Antivirus warning | Add an exception for `traffic-analyzer.exe` (false positive). |
| Slow first start | PyInstaller EXEs self-extract on first run – normal. |

## System Requirements

- Windows 10 / 11 (64-bit)
- 4 GB RAM minimum
- Internet connection (for Groq AI calls)
- ~150 MB disk space
