from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "data" / "watchdog-v4.log"
START_SCRIPT = ROOT / "scripts" / "start-stack-v4.ps1"
CHECK_INTERVAL = max(15, int(os.getenv("AGENT_MANAGER_WATCHDOG_INTERVAL", "30")))
FAIL_THRESHOLD = max(2, int(os.getenv("AGENT_MANAGER_WATCHDOG_FAILURES", "2")))
COOLDOWN = max(30, int(os.getenv("AGENT_MANAGER_WATCHDOG_COOLDOWN", "90")))


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(event: str, **payload) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": utcnow(), "event": event, **payload}
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def healthy(url: str, timeout: float = 5.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def reconcile() -> bool:
    if os.name != "nt":
        return False
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.Popen(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(START_SCRIPT),
            ],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
        log("reconcile_started")
        return True
    except Exception as exc:
        log("reconcile_failed", error=str(exc))
        return False


def main() -> None:
    failures = 0
    last_reconcile = 0.0
    log("watchdog_started", pid=os.getpid(), interval=CHECK_INTERVAL)
    while True:
        manager_ok = healthy("http://127.0.0.1:8787/health")
        remote_expected = bool(os.getenv("FLEET_REMOTE_PASSWORD") or os.getenv("FLEET_TUNNEL_CONFIG"))
        remote_ok = (not remote_expected) or healthy("http://127.0.0.1:8788/health")

        if manager_ok and remote_ok:
            failures = 0
        else:
            failures += 1
            log("stack_probe_failed", consecutive=failures, manager_ok=manager_ok, remote_ok=remote_ok)
            if failures >= FAIL_THRESHOLD and time.time() - last_reconcile >= COOLDOWN:
                if reconcile():
                    last_reconcile = time.time()
                failures = 0
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
