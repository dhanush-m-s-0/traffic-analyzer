# Traffic Analyzer

**AI-Powered Traffic Intelligence** – real-time analysis, route optimisation, and congestion prediction powered by [Groq LLM](https://groq.com) and [LangChain](https://python.langchain.com).

## Features

| Feature | Description |
|---------|-------------|
| 🔍 Traffic Analysis | AI-driven congestion level & delay estimation |
| 🗺 Route Optimisation | Best path between origin and destination |
| 🌦 Weather Impact | Weather effect on road conditions |
| ⚠ Alert Management | Create & list traffic alerts |
| 🖥 Desktop App | Tkinter GUI with system tray support |
| 🌐 Web Interface | Responsive browser UI auto-launched on start |
| 📟 CLI | Full-featured command-line interface |
| 🚀 REST API | FastAPI with interactive Swagger docs |

## Quick Start

### Prerequisites

- Python 3.11+
- A [Groq API key](https://console.groq.com/keys) (free tier available)

### Installation

```bash
git clone https://github.com/dhanush-m-s-0/traffic-analyzer.git
cd traffic-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running

**Desktop Application (GUI):**
```bash
python -m src.main_app
```

**API Server only:**
```bash
python -m uvicorn api.main:app --reload
# Open http://127.0.0.1:8000
```

**CLI:**
```bash
python -m cli.main --help
python -m cli.main analyze --location "New York"
python -m cli.main optimize-route --origin "Brooklyn" --destination "Manhattan"
```

**Windows – double-click:**
```
run.bat
```

**Linux/macOS:**
```bash
./run.sh
./run.sh --server      # API only
./run.sh --cli analyze --location "London"
```

## Project Structure

```
traffic-analyzer/
├── src/                    # Desktop GUI application
│   ├── main_app.py         # Tkinter window & app controller
│   ├── background_server.py # API process manager
│   └── system_tray.py      # System tray integration
├── frontend/               # Embedded web interface
│   ├── index.html          # Home / analysis page
│   ├── dashboard.html      # Live dashboard
│   ├── style.css           # Modern dark theme
│   └── script.js           # Frontend logic
├── config/
│   └── settings.py         # Environment-based configuration
├── api/
│   ├── main.py             # FastAPI app factory
│   └── routes.py           # All API endpoints
├── cli/
│   └── main.py             # Click CLI commands
├── build_exe.py            # PyInstaller build script
├── build_installer.nsi     # NSIS Windows installer
├── run.bat / run.sh        # Quick start scripts
├── requirements.txt
└── .env.example
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Server health check |
| POST | `/api/analyze` | Analyze traffic for a location |
| POST | `/api/optimize-route` | Find optimal route |
| GET | `/api/congestion/{location}` | Quick congestion check |
| POST | `/api/alerts` | Create a traffic alert |
| GET | `/api/alerts` | List active alerts |
| GET | `/api/history` | Recent analysis history |
| GET | `/api/weather/{location}` | Weather impact analysis |

Interactive docs available at `http://127.0.0.1:8000/docs`.

## Building a Windows EXE

See [BUILD.md](BUILD.md) for full instructions.

```bash
pip install pyinstaller
python build_exe.py
# Output: dist/traffic-analyzer.exe
```

## Configuration

All settings are managed via `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | _(required)_ | Your Groq API key |
| `GROQ_MODEL` | `llama3-8b-8192` | Model to use |
| `API_HOST` | `127.0.0.1` | API bind address |
| `API_PORT` | `8000` | API port |
| `DATABASE_URL` | SQLite local file | Database connection |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## License

MIT License – see [LICENSE.md](LICENSE.md).