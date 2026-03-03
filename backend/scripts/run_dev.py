"""Start the backend dev server on a free port.

Usage:
    cd backend && python -m scripts.run_dev
"""

from __future__ import annotations

import socket
import subprocess
import sys


def is_port_free(port: int) -> bool:
    """Check if a TCP port is available on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def find_free_port(start: int, max_tries: int = 10) -> int:
    """Return *start* if free, otherwise scan up to *start + max_tries*."""
    for offset in range(max_tries):
        port = start + offset
        if is_port_free(port):
            return port
    raise RuntimeError(f"No free port found in range {start}–{start + max_tries - 1}")


def main() -> None:
    from app.config import get_settings

    settings = get_settings()
    desired = settings.BACKEND_PORT

    port = find_free_port(desired)
    if port != desired:
        print(f"[run_dev] Puerto {desired} ocupado → usando {port}")
    else:
        print(f"[run_dev] Iniciando backend en puerto {port}")

    subprocess.run(
        [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", str(port),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
