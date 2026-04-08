"""FastAPI application entry point for Traffic Analyzer."""

import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router
from config.settings import settings

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Traffic Analyzer API powered by Groq LLM and LangChain. "
            "Provides real-time traffic analysis, route optimization, "
            "congestion prediction, and alert management."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS – allow the embedded browser (localhost) to call the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API routes under /api prefix
    app.include_router(router, prefix="/api", tags=["traffic"])

    # Serve the embedded frontend
    if FRONTEND_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

        @app.get("/", include_in_schema=False)
        def serve_index() -> FileResponse:
            return FileResponse(str(FRONTEND_DIR / "index.html"))

        @app.get("/dashboard", include_in_schema=False)
        def serve_dashboard() -> FileResponse:
            return FileResponse(str(FRONTEND_DIR / "dashboard.html"))

    return app


app = create_app()

# ---------------------------------------------------------------------------
# Direct execution entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info(
        "Starting %s API on %s:%s", settings.APP_NAME, settings.API_HOST, settings.API_PORT
    )
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
        log_level=settings.LOG_LEVEL.lower(),
    )
