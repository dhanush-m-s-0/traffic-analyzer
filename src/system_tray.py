"""System tray integration using pystray."""

import logging
import threading
import webbrowser
from typing import TYPE_CHECKING, Optional

logger = logging.getLogger(__name__)

try:
    import pystray
    from PIL import Image, ImageDraw

    _TRAY_AVAILABLE = True
except ImportError:
    _TRAY_AVAILABLE = False
    logger.warning("pystray / Pillow not installed – system tray disabled.")

if TYPE_CHECKING:
    from src.main_app import TrafficAnalyzerApp


def _build_tray_icon() -> "Image.Image":  # type: ignore[name-defined]
    """Generate a simple traffic-light icon for the system tray."""
    img = Image.new("RGBA", (64, 64), color=(30, 30, 30, 0))
    draw = ImageDraw.Draw(img)
    # Outer circle
    draw.ellipse([4, 4, 60, 60], fill=(40, 40, 40), outline=(200, 200, 200), width=2)
    # Traffic lights
    draw.ellipse([20, 8, 44, 22], fill=(220, 50, 50))    # red
    draw.ellipse([20, 26, 44, 40], fill=(220, 165, 0))   # amber
    draw.ellipse([20, 44, 44, 58], fill=(50, 200, 50))   # green
    return img


class SystemTray:
    """Wraps a pystray icon with Traffic Analyzer actions."""

    def __init__(self, app: "TrafficAnalyzerApp") -> None:
        self._app = app
        self._icon: Optional["pystray.Icon"] = None  # type: ignore[name-defined]
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Initialise and run the tray icon in a background thread."""
        if not _TRAY_AVAILABLE:
            return

        menu = pystray.Menu(
            pystray.MenuItem("Open Web Interface", self._on_open_browser),
            pystray.MenuItem("Show Window", self._on_show_window),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Start Server", self._on_start_server),
            pystray.MenuItem("Stop Server", self._on_stop_server),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

        self._icon = pystray.Icon(
            name="traffic_analyzer",
            icon=_build_tray_icon(),
            title="Traffic Analyzer",
            menu=menu,
        )

        self._thread = threading.Thread(
            target=self._icon.run, daemon=True, name="tray-thread"
        )
        self._thread.start()
        logger.info("System tray icon started.")

    def stop(self) -> None:
        """Remove the tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception as exc:  # noqa: BLE001
                logger.debug("Tray stop error: %s", exc)
        self._icon = None

    def update_title(self, title: str) -> None:
        """Update the tray icon tooltip."""
        if self._icon:
            self._icon.title = title

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_open_browser(self, *_: object) -> None:
        url = self._app.server.url if self._app.server.is_running() else "#"
        webbrowser.open(url)

    def _on_show_window(self, *_: object) -> None:
        try:
            self._app.root.deiconify()
            self._app.root.lift()
        except Exception:  # noqa: BLE001
            pass

    def _on_start_server(self, *_: object) -> None:
        self._app.start_server()

    def _on_stop_server(self, *_: object) -> None:
        self._app.stop_server()

    def _on_quit(self, *_: object) -> None:
        self._app.quit_app()
