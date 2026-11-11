from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone

from .db_v3 import StoreV3


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class NotificationCenterV4:
    def __init__(self, store: StoreV3) -> None:
        self.store = store
        self.desktop = os.getenv("AGENT_MANAGER_DESKTOP_NOTIFICATIONS", "1").lower() in {"1","true","yes","on"}

    def send(self, severity: str, title: str, body: str, source: str = "manager") -> None:
        self.store.execute(
            "INSERT INTO notifications(created_at,severity,source,title,body,status) VALUES(?,?,?,?,?,'new')",
            (utcnow(), severity, source, title, body[:4000]),
        )
        self.store.event("NOTIFICATION", source, severity.lower(), {"title": title, "body": body[:1000]})
        if severity.upper() in {"P0", "P1"} and source != "summary-v4":
            recipient = os.getenv("REPORT_TO_EMAIL", "").strip()
            gmail_enabled = os.getenv("GMAIL_REPORTING_ENABLED", "0").strip().lower() in {"1","true","yes","on"}
            if gmail_enabled and recipient:
                self.store.execute(
                    "INSERT INTO email_queue(created_at,kind,priority,recipient,subject,body,status) VALUES(?,?,?,?,?,?,'pending')",
                    (
                        utcnow(),
                        "critical_alert",
                        5 if severity.upper() == "P0" else 10,
                        recipient,
                        f"[{severity.upper()}] Agent Manager V4 - {title}",
                        f"{body}\n\nSource: {source}",
                    ),
                )
        if self.desktop and severity.upper() in {"P0", "P1"} and os.name == "nt":
            self._desktop_balloon(title, body)

    def _desktop_balloon(self, title: str, body: str) -> None:
        # Built-in Windows Forms only; no external PowerShell module required.
        safe_title = title.replace("'", "''")[:120]
        safe_body = body.replace("'", "''")[:400]
        script = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "Add-Type -AssemblyName System.Drawing;"
            "$n=New-Object System.Windows.Forms.NotifyIcon;"
            "$n.Icon=[System.Drawing.SystemIcons]::Warning;"
            "$n.Visible=$true;"
            f"$n.BalloonTipTitle='{safe_title}';"
            f"$n.BalloonTipText='{safe_body}';"
            "$n.ShowBalloonTip(7000);Start-Sleep -Seconds 8;$n.Dispose()"
        )
        try:
            subprocess.Popen(
                ["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception:
            pass

    def recent(self, limit: int = 100) -> list[dict]:
        return self.store.query(
            "SELECT * FROM notifications ORDER BY id DESC LIMIT ?",
            (max(1, min(limit, 500)),),
        )
