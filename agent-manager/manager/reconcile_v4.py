from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import psutil


ROOT = Path(__file__).resolve().parents[1].resolve()


def _within(child: Path, root: Path) -> bool:
    try:
        return child == root or child.is_relative_to(root)
    except AttributeError:
        return child == root or root in child.parents


def _is_owned_manager_process(proc: psutil.Process) -> bool:
    try:
        cwd = Path(proc.cwd()).resolve()
        cmd = " ".join(proc.cmdline()).lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError):
        return False
    return _within(cwd, ROOT) and "run.py" in cmd


def _is_owned_project_visibility_process(proc: psutil.Process, root: Path) -> bool:
    try:
        cwd = Path(proc.cwd()).resolve()
        cmd = " ".join(proc.cmdline()).lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError):
        return False
    return _within(cwd, root) and "api.server:app" in cmd


def _listeners(port: int):
    return [
        c for c in psutil.net_connections(kind="inet")
        if c.laddr and c.laddr.port == port and c.status == psutil.CONN_LISTEN and c.pid
    ]


def _stop_owned(port: int, predicate) -> tuple[bool, str]:
    listeners = _listeners(port)
    if not listeners:
        return True, "no listener"

    for conn in listeners:
        try:
            proc = psutil.Process(conn.pid)
        except psutil.NoSuchProcess:
            continue
        if not predicate(proc):
            return False, f"port {port} belongs to unrelated PID {conn.pid}"
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except psutil.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    deadline = time.time() + 5
    while time.time() < deadline:
        if not _listeners(port):
            return True, f"owned listener on port {port} stopped"
        time.sleep(0.25)
    return False, f"port {port} is still listening after stop"


def stop_manager_listener(port: int = 8787) -> tuple[bool, str]:
    return _stop_owned(port, _is_owned_manager_process)


def stop_project_visibility_listener(
    root: str | Path | None = None,
    port: int = 8000,
) -> tuple[bool, str]:
    value = str(root or os.getenv("PROJECT_VISIBILITY_ROOT", "")).strip()
    if not value:
        return False, "PROJECT_VISIBILITY_ROOT is not configured"
    pv_root = Path(value).expanduser().resolve()
    if not pv_root.exists():
        return False, f"Project Visibility root does not exist: {pv_root}"
    return _stop_owned(port, lambda proc: _is_owned_project_visibility_process(proc, pv_root))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manager", action="store_true")
    parser.add_argument("--project-visibility", action="store_true")
    parser.add_argument("--root", default="")
    args = parser.parse_args()

    if args.manager:
        ok, message = stop_manager_listener()
    elif args.project_visibility:
        ok, message = stop_project_visibility_listener(args.root or None)
    else:
        parser.error("choose a reconcile target")
        return 2

    print(message)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
