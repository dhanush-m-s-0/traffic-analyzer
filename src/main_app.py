"""Main Tkinter desktop application for Traffic Analyzer."""

import logging
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Optional

from config.settings import settings
from src.background_server import BackgroundServer
from src.system_tray import SystemTray

logger = logging.getLogger(__name__)

# Colours
CLR_BG = "#1e1e2e"
CLR_SURFACE = "#313244"
CLR_ACCENT = "#89b4fa"
CLR_SUCCESS = "#a6e3a1"
CLR_ERROR = "#f38ba8"
CLR_TEXT = "#cdd6f4"
CLR_MUTED = "#6c7086"


class SettingsDialog(tk.Toplevel):
    """Modal settings dialog."""

    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.title("Settings")
        self.resizable(False, False)
        self.configure(bg=CLR_BG)
        self.grab_set()
        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 12, "pady": 6}
        lbl_kw = {"bg": CLR_BG, "fg": CLR_TEXT, "font": ("Segoe UI", 10)}

        tk.Label(self, text="Groq API Key", **lbl_kw).grid(row=0, column=0, sticky="w", **pad)
        self._key_var = tk.StringVar(value=settings.GROQ_API_KEY)
        self._key_entry = tk.Entry(
            self, textvariable=self._key_var, show="*", width=45,
            bg=CLR_SURFACE, fg=CLR_TEXT, insertbackground=CLR_TEXT,
        )
        self._key_entry.grid(row=0, column=1, **pad)

        tk.Label(self, text="API Port", **lbl_kw).grid(row=1, column=0, sticky="w", **pad)
        self._port_var = tk.StringVar(value=str(settings.API_PORT))
        tk.Entry(
            self, textvariable=self._port_var, width=10,
            bg=CLR_SURFACE, fg=CLR_TEXT, insertbackground=CLR_TEXT,
        ).grid(row=1, column=1, sticky="w", **pad)

        btn_frame = tk.Frame(self, bg=CLR_BG)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=12)
        tk.Button(
            btn_frame, text="Save", bg=CLR_ACCENT, fg=CLR_BG, relief="flat",
            padx=16, command=self._save,
        ).pack(side="left", padx=6)
        tk.Button(
            btn_frame, text="Cancel", bg=CLR_SURFACE, fg=CLR_TEXT, relief="flat",
            padx=16, command=self.destroy,
        ).pack(side="left", padx=6)

    def _save(self) -> None:
        import os
        env_file = Path(__file__).resolve().parent.parent / ".env"
        lines: list[str] = []
        if env_file.exists():
            lines = env_file.read_text(encoding="utf-8").splitlines()

        def _set(key: str, value: str) -> None:
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}"
                    return
            lines.append(f"{key}={value}")

        _set("GROQ_API_KEY", self._key_var.get().strip())
        _set("API_PORT", self._port_var.get().strip())
        env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        messagebox.showinfo("Settings", "Settings saved. Restart the server to apply.")
        self.destroy()


class TrafficAnalyzerApp:
    """Main desktop application window."""

    def __init__(self) -> None:
        self.server = BackgroundServer()
        self.tray: Optional[SystemTray] = None
        self._monitor_job: Optional[str] = None

        self.root = tk.Tk()
        self.root.title(f"{settings.APP_NAME} v{settings.APP_VERSION}")
        self.root.geometry(f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}")
        self.root.configure(bg=CLR_BG)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._set_icon()
        self._build_ui()

        # System tray
        self.tray = SystemTray(self)
        self.tray.start()

    # ------------------------------------------------------------------
    # Icon
    # ------------------------------------------------------------------

    def _set_icon(self) -> None:
        icon_path = Path(__file__).resolve().parent.parent / "traffic-analyzer.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Header
        header = tk.Frame(self.root, bg=CLR_ACCENT, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text=f"🚦 {settings.APP_NAME}",
            font=("Segoe UI", 18, "bold"),
            bg=CLR_ACCENT,
            fg=CLR_BG,
        ).pack(side="left", padx=20, pady=10)
        tk.Label(
            header,
            text=f"v{settings.APP_VERSION}",
            font=("Segoe UI", 10),
            bg=CLR_ACCENT,
            fg=CLR_BG,
        ).pack(side="right", padx=20)

        # Status bar
        status_frame = tk.Frame(self.root, bg=CLR_SURFACE, pady=8)
        status_frame.pack(fill="x", padx=16, pady=(16, 0))

        tk.Label(
            status_frame, text="Server Status:", font=("Segoe UI", 10),
            bg=CLR_SURFACE, fg=CLR_TEXT,
        ).pack(side="left", padx=8)

        self._status_dot = tk.Label(
            status_frame, text="●", font=("Segoe UI", 14),
            bg=CLR_SURFACE, fg=CLR_ERROR,
        )
        self._status_dot.pack(side="left")

        self._status_label = tk.Label(
            status_frame, text="Stopped", font=("Segoe UI", 10, "bold"),
            bg=CLR_SURFACE, fg=CLR_ERROR,
        )
        self._status_label.pack(side="left", padx=4)

        self._url_label = tk.Label(
            status_frame, text="", font=("Segoe UI", 9),
            bg=CLR_SURFACE, fg=CLR_MUTED,
        )
        self._url_label.pack(side="left", padx=12)

        # CPU / Memory info
        self._stats_label = tk.Label(
            status_frame, text="", font=("Segoe UI", 9),
            bg=CLR_SURFACE, fg=CLR_MUTED,
        )
        self._stats_label.pack(side="right", padx=8)

        # Control buttons
        btn_frame = tk.Frame(self.root, bg=CLR_BG)
        btn_frame.pack(fill="x", padx=16, pady=12)

        self._start_btn = tk.Button(
            btn_frame, text="▶  Start Server",
            font=("Segoe UI", 10, "bold"),
            bg=CLR_SUCCESS, fg=CLR_BG, relief="flat", padx=18, pady=8,
            cursor="hand2", command=self._on_start,
        )
        self._start_btn.pack(side="left", padx=4)

        self._stop_btn = tk.Button(
            btn_frame, text="■  Stop Server",
            font=("Segoe UI", 10, "bold"),
            bg=CLR_ERROR, fg=CLR_BG, relief="flat", padx=18, pady=8,
            cursor="hand2", command=self._on_stop, state="disabled",
        )
        self._stop_btn.pack(side="left", padx=4)

        self._open_btn = tk.Button(
            btn_frame, text="🌐  Open Web Interface",
            font=("Segoe UI", 10),
            bg=CLR_ACCENT, fg=CLR_BG, relief="flat", padx=18, pady=8,
            cursor="hand2", command=self._on_open_browser, state="disabled",
        )
        self._open_btn.pack(side="left", padx=4)

        tk.Button(
            btn_frame, text="⚙  Settings",
            font=("Segoe UI", 10),
            bg=CLR_SURFACE, fg=CLR_TEXT, relief="flat", padx=12, pady=8,
            cursor="hand2", command=self._on_settings,
        ).pack(side="right", padx=4)

        tk.Button(
            btn_frame, text="❓  Help",
            font=("Segoe UI", 10),
            bg=CLR_SURFACE, fg=CLR_TEXT, relief="flat", padx=12, pady=8,
            cursor="hand2", command=self._on_help,
        ).pack(side="right", padx=4)

        # Auto-start checkbox
        self._autostart_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self.root,
            text="Auto-start server on launch",
            variable=self._autostart_var,
            bg=CLR_BG, fg=CLR_MUTED, activebackground=CLR_BG,
            selectcolor=CLR_SURFACE, font=("Segoe UI", 9),
        ).pack(anchor="w", padx=20)

        # Log / info text area
        log_frame = tk.Frame(self.root, bg=CLR_BG)
        log_frame.pack(fill="both", expand=True, padx=16, pady=8)
        tk.Label(
            log_frame, text="Activity Log", font=("Segoe UI", 10, "bold"),
            bg=CLR_BG, fg=CLR_TEXT,
        ).pack(anchor="w")

        self._log_text = tk.Text(
            log_frame, bg=CLR_SURFACE, fg=CLR_TEXT,
            font=("Consolas", 9), relief="flat", state="disabled",
            wrap="word",
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._log_text.pack(fill="both", expand=True)

        # Footer
        tk.Label(
            self.root,
            text="Powered by Groq LLM + LangChain  |  Local processing only",
            font=("Segoe UI", 8), bg=CLR_BG, fg=CLR_MUTED,
        ).pack(pady=(0, 6))

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def _log(self, message: str, colour: str = CLR_TEXT) -> None:
        """Append a line to the activity log widget (thread-safe)."""
        def _insert() -> None:
            self._log_text.configure(state="normal")
            self._log_text.insert("end", f"{message}\n", "msg")
            self._log_text.tag_configure("msg", foreground=colour)
            self._log_text.see("end")
            self._log_text.configure(state="disabled")

        self.root.after(0, _insert)

    # ------------------------------------------------------------------
    # Server control
    # ------------------------------------------------------------------

    def start_server(self) -> None:
        """Public: start the API server (callable from tray)."""
        self._on_start()

    def stop_server(self) -> None:
        """Public: stop the API server (callable from tray)."""
        self._on_stop()

    def _on_start(self) -> None:
        self._start_btn.configure(state="disabled")
        self._log("Starting server…", CLR_ACCENT)

        def _worker() -> None:
            ok = self.server.start()
            if ok:
                self.root.after(0, self._on_server_started)
            else:
                self.root.after(0, lambda: self._on_server_failed("Failed to start server."))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_stop(self) -> None:
        self._stop_btn.configure(state="disabled")
        self._log("Stopping server…", CLR_ERROR)
        threading.Thread(target=self.server.stop, daemon=True).start()
        self.root.after(1500, self._update_status)

    def _on_server_started(self) -> None:
        self._log(f"Server running at {self.server.url}", CLR_SUCCESS)
        if self._autostart_var.get():
            self._log("Auto-opening browser…", CLR_ACCENT)
            webbrowser.open(self.server.url)
        self._update_status()
        self._start_monitor()

    def _on_server_failed(self, message: str) -> None:
        self._log(f"ERROR: {message}", CLR_ERROR)
        messagebox.showerror("Server Error", message)
        self._start_btn.configure(state="normal")

    # ------------------------------------------------------------------
    # Status monitoring
    # ------------------------------------------------------------------

    def _start_monitor(self) -> None:
        self._monitor_job = self.root.after(3000, self._monitor_loop)

    def _monitor_loop(self) -> None:
        self._update_status()
        self._update_stats()
        self._monitor_job = self.root.after(3000, self._monitor_loop)

    def _update_status(self) -> None:
        running = self.server.is_running()
        if running:
            self._status_dot.configure(fg=CLR_SUCCESS)
            self._status_label.configure(text="Running", fg=CLR_SUCCESS)
            self._url_label.configure(text=self.server.url)
            self._start_btn.configure(state="disabled")
            self._stop_btn.configure(state="normal")
            self._open_btn.configure(state="normal")
            if self.tray:
                self.tray.update_title(f"Traffic Analyzer – Running on {self.server.url}")
        else:
            self._status_dot.configure(fg=CLR_ERROR)
            self._status_label.configure(text="Stopped", fg=CLR_ERROR)
            self._url_label.configure(text="")
            self._start_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled")
            self._open_btn.configure(state="disabled")
            if self.tray:
                self.tray.update_title("Traffic Analyzer – Stopped")

    def _update_stats(self) -> None:
        try:
            import psutil
            proc = self.server._process
            if proc and proc.is_alive():
                p = psutil.Process(proc.pid)
                mem_mb = p.memory_info().rss / 1_048_576
                cpu = p.cpu_percent(interval=None)
                self._stats_label.configure(
                    text=f"CPU: {cpu:.1f}%  RAM: {mem_mb:.0f} MB"
                )
                return
        except Exception:  # noqa: BLE001
            pass
        self._stats_label.configure(text="")

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------

    def _on_open_browser(self) -> None:
        if self.server.is_running():
            webbrowser.open(self.server.url)
        else:
            messagebox.showwarning("Server not running", "Start the server first.")

    def _on_settings(self) -> None:
        SettingsDialog(self.root)

    def _on_help(self) -> None:
        help_text = (
            f"{settings.APP_NAME} v{settings.APP_VERSION}\n\n"
            "1. Click 'Start Server' to launch the API backend.\n"
            "2. The web interface will open automatically in your browser.\n"
            "3. Use the web UI to analyse traffic and optimise routes.\n"
            "4. You can also use the CLI:\n"
            "   python -m cli.main analyze --location 'New York'\n\n"
            "API Docs: http://127.0.0.1:8000/docs\n"
            "Support: github.com/dhanush-m-s-0/traffic-analyzer"
        )
        messagebox.showinfo("Help", help_text)

    # ------------------------------------------------------------------
    # Window lifecycle
    # ------------------------------------------------------------------

    def _on_close(self) -> None:
        """Minimise to tray instead of closing if tray is available."""
        try:
            import pystray  # noqa: F401
            self.root.withdraw()
        except ImportError:
            self.quit_app()

    def quit_app(self) -> None:
        """Fully shut down the application."""
        self._log("Shutting down…")
        if self._monitor_job:
            self.root.after_cancel(self._monitor_job)
        self.server.stop()
        if self.tray:
            self.tray.stop()
        self.root.destroy()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the Tk event loop.  Optionally auto-start the server."""
        self._log(f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}")
        self._log("Click 'Start Server' or enable Auto-start to begin.")
        if self._autostart_var.get():
            self.root.after(500, self._on_start)
        self.root.mainloop()


def main() -> None:
    """Application entry point."""
    logging.basicConfig(level=logging.INFO)
    app = TrafficAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()
