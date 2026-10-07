from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import psutil


ROOT = Path(__file__).resolve().parents[1].resolve()


def _is_owned_manager_process(proc: psutil.Process) -> bool:
    try:
        cwd = Path(proc.cwd()).resolve()
        cmd = " ".join(proc.cmdline()).lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError):
        return False
    try:
        in_root = cwd == ROOT or cwd.is_relative_to(ROOT)
    except AttributeError:
        in_root = cwd == ROOT or ROOT in cwd.parents
    return in_root and "run.py" in cmd


def stop_manager_listener(port: int = 8787) -> tuple[bool, str]:
    listeners = [
        c for c in psutil.net_connections(kind="inet")
        if c.laddr and c.laddr.port == port and c.status == psutil.CONN_LISTEN and c.pid
    ]
    if not listeners:
        return True, "no listener"
    for conn in listeners:
        try:
            proc = psutil.Process(conn.pid)
        except psutil.NoSuchProcess:
            continue
        if not _is_owned_manager_process(proc):
            return False, f"port {port} belongs to unrelated PID {conn.pid}"
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except psutil.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    deadline = time.time() + 5
    while time.time() < deadline:
        if not any(
            c.laddr and c.laddr.port == port and c.status == psutil.CONN_LISTEN
            for c in psutil.net_connections(kind="inet")
        ):
            return True, "owned manager listener stopped"
        time.sleep(0.25)
    return False, f"port {port} is still listening after stop"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manager", action="store_true")
    args = parser.parse_args()
    if args.manager:
        ok, message = stop_manager_listener()
        print(message)
        return 0 if ok else 2
    parser.error("choose a reconcile target")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
