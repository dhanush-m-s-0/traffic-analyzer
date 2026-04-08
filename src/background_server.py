"""Background API server process manager."""

import logging
import multiprocessing
import socket
import time
from typing import Optional

import uvicorn

from config.settings import settings

logger = logging.getLogger(__name__)


def _is_port_free(host: str, port: int) -> bool:
    """Return True if the given TCP port is not in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) != 0


def _server_worker(host: str, port: int, log_level: str) -> None:
    """Worker function that runs inside a child process."""
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=False,
        log_level=log_level.lower(),
    )


class BackgroundServer:
    """Manages the lifecycle of the embedded FastAPI server process."""

    def __init__(
        self,
        host: str = settings.API_HOST,
        port: int = settings.API_PORT,
        log_level: str = settings.LOG_LEVEL,
    ) -> None:
        self.host = host
        self.port = port
        self.log_level = log_level
        self._process: Optional[multiprocessing.Process] = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self) -> bool:
        """Start the server.  Returns True on success."""
        if self.is_running():
            logger.info("Server already running on port %s.", self.port)
            return True

        if not _is_port_free(self.host, self.port):
            logger.error(
                "Port %s is already in use by another application.", self.port
            )
            return False

        self._process = multiprocessing.Process(
            target=_server_worker,
            args=(self.host, self.port, self.log_level),
            daemon=True,
            name="traffic-analyzer-server",
        )
        self._process.start()
        logger.info("Server process started (PID %s).", self._process.pid)

        # Wait up to 10 s for the port to become active
        for _ in range(20):
            time.sleep(0.5)
            if not _is_port_free(self.host, self.port):
                logger.info(
                    "Server is up at http://%s:%s", self.host, self.port
                )
                return True

        logger.error("Server did not start within the expected time.")
        self.stop()
        return False

    def stop(self) -> None:
        """Gracefully terminate the server process."""
        if self._process and self._process.is_alive():
            logger.info("Stopping server process (PID %s)…", self._process.pid)
            self._process.terminate()
            self._process.join(timeout=5)
            if self._process.is_alive():
                self._process.kill()
                self._process.join(timeout=3)
            logger.info("Server stopped.")
        self._process = None

    def is_running(self) -> bool:
        """Return True when the server process is alive and port is active."""
        return (
            self._process is not None
            and self._process.is_alive()
            and not _is_port_free(self.host, self.port)
        )

    @property
    def url(self) -> str:
        """Base URL of the embedded server."""
        return f"http://{self.host}:{self.port}"

    @property
    def pid(self) -> Optional[int]:
        """PID of the server process, or None if not running."""
        return self._process.pid if self._process else None
