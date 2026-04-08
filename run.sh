#!/usr/bin/env bash
# Traffic Analyzer – Linux/macOS Quick Start

set -e

echo "============================================"
echo "  Traffic Analyzer v1.0.0"
echo "  Powered by Groq LLM + LangChain"
echo "============================================"
echo

# Python check
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 not found. Install Python 3.11+ first."
    exit 1
fi

# Create .env if missing
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[INFO] Created .env from .env.example – edit it and add your GROQ_API_KEY."
fi

# Virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment…"
    python3 -m venv venv
    echo "[INFO] Installing dependencies…"
    # shellcheck disable=SC1091
    source venv/bin/activate
    pip install -r requirements.txt --quiet
else
    # shellcheck disable=SC1091
    source venv/bin/activate
fi

# Run – headless servers default to CLI
if [ "${1}" = "--server" ]; then
    echo "[INFO] Starting API server on http://127.0.0.1:8000"
    python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
elif [ "${1}" = "--cli" ]; then
    shift
    python -m cli.main "$@"
else
    echo "[INFO] Starting Traffic Analyzer…"
    python -m src.main_app
fi
