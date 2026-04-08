# Installation Guide

## Option 1 – Portable EXE (Windows, no install)

1. Download `traffic-analyzer-portable.exe`.
2. Place it in any folder (e.g. `C:\Tools\TrafficAnalyzer\`).
3. Double-click to run.

## Option 2 – Windows Installer

1. Download `traffic-analyzer-setup.exe`.
2. Run as Administrator.
3. Follow the setup wizard.
4. Launch from Desktop or Start Menu shortcut.

## Option 3 – From Source (Python)

### Prerequisites

| Software | Version | Link |
|----------|---------|------|
| Python | 3.11+ | https://python.org/downloads |
| Git | any | https://git-scm.com |

### Steps

```bash
# 1. Clone
git clone https://github.com/dhanush-m-s-0/traffic-analyzer.git
cd traffic-analyzer

# 2. Virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env – paste your GROQ_API_KEY

# 5. Run
python -m src.main_app        # Desktop GUI
# OR
uvicorn api.main:app --reload # API server only
# OR
python -m cli.main --help     # CLI
```

## Docker (API server only)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t traffic-analyzer .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key traffic-analyzer
```

## Getting a Groq API Key

1. Visit <https://console.groq.com/keys>
2. Sign up / log in (free tier available)
3. Click **Create API Key**
4. Copy the key and add it to your `.env` file

## Verify Installation

```bash
# Health check
curl http://127.0.0.1:8000/api/health

# Should return: {"status":"ok","timestamp":"..."}
```
