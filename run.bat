@echo off
:: Traffic Analyzer – Windows Quick Start
:: Double-click this file to start the application.

title Traffic Analyzer

echo ============================================
echo   Traffic Analyzer v1.0.0
echo   Powered by Groq LLM + LangChain
echo ============================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create .env if missing
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [INFO] Created .env from .env.example
        echo [INFO] Edit .env and add your GROQ_API_KEY before continuing.
        notepad .env
        pause
    )
)

:: Install dependencies if needed
if not exist "venv\" (
    echo [INFO] Creating virtual environment…
    python -m venv venv
    echo [INFO] Installing dependencies…
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet
) else (
    call venv\Scripts\activate.bat
)

:: Start the desktop application
echo [INFO] Starting Traffic Analyzer…
python -m src.main_app

deactivate
pause
