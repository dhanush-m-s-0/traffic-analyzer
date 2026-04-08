"""FastAPI application entry point for the traffic analyzer."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Traffic Analyzer API",
    description=(
        "Comprehensive traffic analysis powered by Agentic AI with Groq and LangChain. "
        "Provides real-time traffic conditions, route optimisation, congestion predictions, "
        "and traffic alerts."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow all origins in development; restrict in production via environment config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", summary="Health check")
def root() -> dict:
    """Return basic service information."""
    return {
        "service": "Traffic Analyzer API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", summary="Detailed health check")
def health() -> dict:
    """Return a detailed health status."""
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "groq_configured": bool(settings.groq_api_key),
        "weather_api_configured": bool(settings.weather_api_key),
    }
