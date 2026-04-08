"""Configuration management for Traffic Analyzer."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    # Groq / LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-8b-8192")

    # Server
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'traffic_analyzer.db'}"
    )

    # Weather API (optional)
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", str(BASE_DIR / "traffic_analyzer.log"))

    # Desktop app
    APP_NAME: str = "Traffic Analyzer"
    APP_VERSION: str = "1.0.0"
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600

    @property
    def api_base_url(self) -> str:
        """Return the base URL for the embedded API server."""
        return f"http://{self.API_HOST}:{self.API_PORT}"


settings = Settings()
