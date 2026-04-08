"""Application settings and configuration management."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Groq LLM settings
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama3-8b-8192", alias="GROQ_MODEL")

    # Application settings
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Database
    database_url: str = Field(
        default="sqlite:///./traffic_analyzer.db", alias="DATABASE_URL"
    )

    # API settings
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    # Weather API
    weather_api_key: Optional[str] = Field(default=None, alias="WEATHER_API_KEY")
    weather_api_url: str = Field(
        default="https://api.openweathermap.org/data/2.5",
        alias="WEATHER_API_URL",
    )

    # Traffic API
    traffic_api_key: Optional[str] = Field(default=None, alias="TRAFFIC_API_KEY")

    # Agent settings
    agent_max_iterations: int = Field(default=10, alias="AGENT_MAX_ITERATIONS")
    agent_temperature: float = Field(default=0.1, alias="AGENT_TEMPERATURE")
    agent_verbose: bool = Field(default=False, alias="AGENT_VERBOSE")

    model_config = {"env_file": ".env", "populate_by_name": True}


# Singleton settings instance
settings = Settings()
