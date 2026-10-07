from __future__ import annotations

import ctypes
import os
import socket
import subprocess
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


# ============================================================
# CONFIGURAÇÃO
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
PYTHONW = ROOT / ".venv" / "Scripts" / "pythonw.exe"

POSTGRES_BIN = Path(r"C:\Program Files\PostgreSQL\18\bin")
POSTGRES_DATA = Path(r"C:\Program Files\PostgreSQL\18\data")

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000

SIMULATOR_HOST = "127.0.0.1"
SIMULATOR_PORT = 8001

BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
SIMULATOR_URL = f"http://{SIMULATOR_HOST}:{SIMULATOR_PORT}"

STARTUP_TIMEOUT = 25
CHECK_INTERVAL = 0.5


# ============================================================
# SINGLE INSTANCE
# ============================================================

MUTEX_NAME = "ESP32_IOT_CONTROL_CENTER_SINGLE_INSTANCE"


def acquire_single_instance():
    kernel32 = ctypes.windll.kernel32

    mutex = kernel32.CreateMutexW(
        None,
        False,
        MUTEX_NAME,
    )

    if not mutex:
        return None

    ERROR_ALREADY_EXISTS = 183

    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(mutex)
        return None

    return mutex


# ============================================================
# PROCESS HELPERS
# ============================================================

CREATE_NO_WINDOW = getattr(
    subprocess,
    "CREATE_NO_WINDOW",
    0x08000000,
)

CREATE_NEW_PROCESS_GROUP = getattr(
    subprocess,
    "CREATE_NEW_PROCESS_GROUP",
    0x00000200,
)


def port_is_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection(
            (host, port),
            timeout=0.25,
        ):
            return True
    except OSError:
        return False


def run_hidden(
    command: list[str],
    cwd: Path | None = None,
) -> subprocess.Popen:

    startupinfo = subprocess.STARTUPINFO()

    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0

    return subprocess.Popen(
        command,
        cwd=str(cwd or ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        startupinfo=startupinfo,
        creationflags=CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP,
    )


def wait_for_port(
    host: str,
    port: int,
    timeout: float,
) -> bool:

    start = time.monotonic()

    while time.monotonic() - start < timeout:

        if port_is_open(host, port):
            return True

        time.sleep(CHECK_INTERVAL)

    return False


# ============================================================
# APPLICATION
# ============================================================

class Launcher:

    def __init__(self, root: tk.Tk):

        self.root = root

        self.root.title("ESP32 IoT Control Center")
        self.root.geometry("760x520")
        self.root.minsize(700, 460)

        self.root.configure(
            bg="#0b1117",
        )

        self.processes: list[subprocess.Popen] = []

        self.starting = False
        self.closing = False

        self.status_vars = {
            "postgres": tk.StringVar(value="Aguardando"),
            "backend": tk.StringVar(value="Aguardando"),
            "simulator": tk.StringVar(value="Aguardando"),
        }

        self.create_interface()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close,
        )

        self.root.after(
            300,
            self.start_system,
        )


    # ========================================================
    # INTERFACE
    # ========================================================

    def create_interface(self):

        container = tk.Frame(
            self.root,
            bg="#0b1117",
        )

        container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25,
        )

        title = tk.Label(
            container,
            text="ESP32 IoT",
            font=("Segoe UI", 26, "bold"),
            fg="#f1f5f9",
            bg="#0b1117",
        )

        title.pack(
            anchor="w",
        )

        subtitle = tk.Label(
            container,
            text="Control Center • execução 100% local",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#0b1117",
        )

        subtitle.pack(
            anchor="w",
            pady=(2, 25),
        )

        self.create_status(
            container,
            "PostgreSQL",
            "postgres",
            "Banco de dados local",
        )

        self.create_status(
            container,
            "Backend API",
            "backend",
            "FastAPI • porta 8000",
        )

        self.create_status(
            container,
            "ESP32 Simulator",
            "simulator",
            "Simulador • porta 8001",
        )

        separator = ttk.Separator(
            container,
            orient="horizontal",
        )

        separator.pack(
            fill="x",
            pady=25,
        )

        self.log_text = tk.Text(
            container,
            height=9,
            bg="#070b10",
            fg="#cbd5e1",
            insertbackground="#ffffff",
            relief="flat",
            font=("Consolas", 9),
            padx=12,
            pady=10,
        )

        self.log_text.pack(
            fill="both",
            expand=True,
        )

        self.log_text.configure(
            state="disabled",
        )

        self.progress = ttk.Progressbar(
            container,
            mode="indeterminate",
        )

        self.progress.pack(
            fill="x",
            pady=(15, 0),
        )


    def create_status(
        self,
        parent,
        title,
        key,
        description,
    ):

        frame = tk.Frame(
            parent,
            bg="#111923",
            height=70,
        )

        frame.pack(
            fill="x",
            pady=5,
        )

        frame.pack_propagate(False)

        indicator = tk.Label(
            frame,
            text="●",
            font=("Segoe UI", 18),
            fg="#64748b",
            bg="#111923",
        )

        indicator.pack(
            side="left",
            padx=(15, 12),
        )

        info = tk.Frame(
            frame,
            bg="#111923",
        )

        info.pack(
            side="left",
            fill="both",
            expand=True,
        )

        tk.Label(
            info,
            text=title,
            font=("Segoe UI", 11, "bold"),
            fg="#f8fafc",
            bg="#111923",
        ).pack(
            anchor="w",
            pady=(10, 0),
        )

        tk.Label(
            info,
            text=description,
            font=("Segoe UI", 8),
            fg="#64748b",
            bg="#111923",
        ).pack(
            anchor="w",
        )

        status = tk.Label(
            frame,
            textvariable=self.status_vars[key],
            font=("Segoe UI", 9, "bold"),
            fg="#94a3b8",
            bg="#111923",
        )

        status.pack(
            side="right",
            padx=18,
        )

        frame.indicator = indicator
        frame.status = status


        setattr(
            self,
            f"{key}_frame",
            frame,
        )


    # ========================================================
    # LOG
    # ========================================================

    def log(self, message: str):

        def write():

            self.log_text.configure(
                state="normal",
            )

            timestamp = time.strftime(
                "%H:%M:%S"
            )

            self.log_text.insert(
                "end",
                f"[{timestamp}] {message}\n",
            )

            self.log_text.see(
                "end",
            )

            self.log_text.configure(
                state="disabled",
            )

        self.root.after(
            0,
            write,
        )


    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        key: str,
        status: str,
        color: str,
    ):

        def update():

            self.status_vars[key].set(
                status,
            )

            frame = getattr(
                self,
                f"{key}_frame",
            )

            frame.indicator.configure(
                fg=color,
            )

            frame.status.configure(
                fg=color,
            )

        self.root.after(
            0,
            update,
        )


    # ========================================================
    # START SYSTEM
    # ========================================================

    def start_system(self):

        if self.starting:
            return

        self.starting = True

        self.progress.start(
            10,
        )

        thread = threading.Thread(
            target=self._startup_worker,
            daemon=True,
        )

        thread.start()


    def _startup_worker(self):

        try:

            self.log(
                "Iniciando sistema local..."
            )

            # ------------------------------------------------
            # VALIDATE PYTHON
            # ------------------------------------------------

            if not PYTHON.exists():

                raise RuntimeError(
                    f"Python da venv não encontrado:\n{PYTHON}"
                )

            self.log(
                "Python da .venv encontrado."
            )

            # ------------------------------------------------
            # POSTGRESQL
            # ------------------------------------------------

            self.log(
                "Verificando PostgreSQL..."
            )

            if port_is_open(
                "127.0.0.1",
                5432,
            ):

                self.set_status(
                    "postgres",
                    "ONLINE",
                    "#22c55e",
                )

                self.log(
                    "PostgreSQL já está em execução."
                )

            else:

                self.set_status(
                    "postgres",
                    "INICIANDO...",
                    "#f59e0b",
                )

                pg_ctl = POSTGRES_BIN / "pg_ctl.exe"

                if not pg_ctl.exists():

                    raise RuntimeError(
                        f"pg_ctl.exe não encontrado:\n{pg_ctl}"
                    )

                if not POSTGRES_DATA.exists():

                    raise RuntimeError(
                        f"Diretório do PostgreSQL não encontrado:\n"
                        f"{POSTGRES_DATA}"
                    )

                self.log(
                    "Iniciando PostgreSQL em segundo plano..."
                )

                process = run_hidden(
                    [
                        str(pg_ctl),
                        "-D",
                        str(POSTGRES_DATA),
                        "start",
                    ],
                    cwd=POSTGRES_BIN,
                )

                self.processes.append(
                    process,
                )

                if not wait_for_port(
                    "127.0.0.1",
                    5432,
                    STARTUP_TIMEOUT,
                ):

                    raise RuntimeError(
                        "PostgreSQL não ficou disponível."
                    )

                self.set_status(
                    "postgres",
                    "ONLINE",
                    "#22c55e",
                )

                self.log(
                    "PostgreSQL iniciado."
                )


            # ------------------------------------------------
            # BACKEND
            # ------------------------------------------------

            self.set_status(
                "backend",
                "VERIFICANDO...",
                "#f59e0b",
            )

            if port_is_open(
                BACKEND_HOST,
                BACKEND_PORT,
            ):

                self.set_status(
                    "backend",
                    "ONLINE",
                    "#22c55e",
                )

                self.log(
                    "Backend já está em execução."
                )

            else:

                self.set_status(
                    "backend",
                    "INICIANDO...",
                    "#f59e0b",
                )

                self.log(
                    "Iniciando Backend..."
                )

                process = run_hidden(
                    [
                        str(PYTHON),
                        "-m",
                        "uvicorn",
                        "backend.app.main:app",
                        "--host",
                        BACKEND_HOST,
                        "--port",
                        str(BACKEND_PORT),
                    ],
                    cwd=ROOT,
                )

                self.processes.append(
                    process,
                )

                if not wait_for_port(
                    BACKEND_HOST,
                    BACKEND_PORT,
                    STARTUP_TIMEOUT,
                ):

                    raise RuntimeError(
                        "Backend não ficou disponível na porta 8000."
                    )

                self.set_status(
                    "backend",
                    "ONLINE",
                    "#22c55e",
                )

                self.log(
                    "Backend iniciado."
                )


            # ------------------------------------------------
            # SIMULATOR
            # ------------------------------------------------

            self.set_status(
                "simulator",
                "VERIFICANDO...",
                "#f59e0b",
            )

            if port_is_open(
                SIMULATOR_HOST,
                SIMULATOR_PORT,
            ):

                self.set_status(
                    "simulator",
                    "ONLINE",
                    "#22c55e",
                )

                self.log(
                    "Simulador já está em execução."
                )

            else:

                self.set_status(
                    "simulator",
                    "INICIANDO...",
                    "#f59e0b",
                )

                self.log(
                    "Iniciando ESP32 Simulator..."
                )

                process = run_hidden(
                    [
                        str(PYTHON),
                        "-m",
                        "uvicorn",
                        "simulator.main:app",
                        "--host",
                        SIMULATOR_HOST,
                        "--port",
                        str(SIMULATOR_PORT),
                    ],
                    cwd=ROOT,
                )

                self.processes.append(
                    process,
                )

                if not wait_for_port(
                    SIMULATOR_HOST,
                    SIMULATOR_PORT,
                    STARTUP_TIMEOUT,
                ):

                    raise RuntimeError(
                        "Simulador não ficou disponível na porta 8001."
                    )

                self.set_status(
                    "simulator",
                    "ONLINE",
                    "#22c55e",
                )

                self.log(
                    "ESP32 Simulator iniciado."
                )


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            self.log(
                "========================================"
            )

            self.log(
                "SISTEMA ONLINE"
            )

            self.log(
                "Backend: http://127.0.0.1:8000"
            )

            self.log(
                "Simulator: http://127.0.0.1:8001"
            )

            self.log(
                "Execução 100% local/offline."
            )

            self.root.after(
                0,
                self.start_finished,
            )

        except Exception as exc:

            self.log(
                f"ERRO: {exc}"
            )

            self.root.after(
                0,
                lambda: self.start_failed(
                    str(exc)
                ),
            )


    def start_finished(self):

        self.starting = False

        self.progress.stop()


    def start_failed(
        self,
        error: str,
    ):

        self.starting = False

        self.progress.stop()

        messagebox.showerror(
            "Falha ao iniciar",
            error,
            parent=self.root,
        )


    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        if self.closing:
            return

        self.closing = True

        self.log(
            "Encerrando serviços iniciados pelo launcher..."
        )

        for process in reversed(
            self.processes
        ):

            try:

                if process.poll() is None:

                    process.terminate()

                    try:
                        process.wait(
                            timeout=3,
                        )

                    except subprocess.TimeoutExpired:

                        process.kill()

            except Exception:
                pass

        self.processes.clear()

        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

def main():

    mutex = acquire_single_instance()

    if mutex is None:
        return

    root = tk.Tk()

    app = Launcher(
        root,
    )

    root.mainloop()


if __name__ == "__main__":
    main()