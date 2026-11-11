from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

from .db_v3 import StoreV3
from .gmail_v4 import GmailV4


class PeriodicEmailReporterV4:
    def __init__(self, store: StoreV3, gmail: GmailV4) -> None:
        self.store = store
        self.gmail = gmail
        self.interval_hours = max(
            1,
            min(168, int(os.getenv("AGENT_MANAGER_EMAIL_INTERVAL_HOURS", "3"))),
        )

    def _latest_status_email(self) -> dict | None:
        rows = self.store.query(
            "SELECT id,created_at,status FROM email_queue "
            "WHERE kind='periodic_status' AND status IN ('pending','sent') "
            "ORDER BY id DESC LIMIT 1"
        )
        return rows[0] if rows else None

    def _is_due(self, now: datetime) -> bool:
        latest = self._latest_status_email()
        if not latest:
            return True
        if latest["status"] == "pending":
            return False
        try:
            previous = datetime.fromisoformat(str(latest["created_at"]))
        except Exception:
            return True
        return now >= previous + timedelta(hours=self.interval_hours)

    def _render(self, report: dict[str, Any]) -> str:
        lines = [
            "AGENT MANAGER V4 - PERIODIC STATUS",
            "",
            f"Interval: every {self.interval_hours} hours",
            f"State: {report.get('state','UNKNOWN')}",
            f"Managed targets: {report.get('managed_ok',0)}/{report.get('managed_total',0)} OK",
            f"Open incidents: {len(report.get('open_incidents') or [])}",
            "",
            "TARGETS",
        ]
        for target in report.get("targets") or []:
            state = "OK" if target.get("ok") else "FAIL"
            extra = target.get("error") or target.get("status_code") or ""
            lines.append(f"- {target.get('name') or target.get('id')}: {state} {extra}".rstrip())

        lines += ["", "AI PROVIDERS"]
        providers = report.get("providers") or {}
        for key in ("colibri", "ollama"):
            row = providers.get(key) or {}
            lines.append(
                f"- {key}: {'OK' if row.get('ok') else 'STANDBY/OFF'}"
                + (f" ({row.get('model')})" if row.get("model") else "")
            )

        incidents = report.get("open_incidents") or []
        if incidents:
            lines += ["", "OPEN INCIDENTS"]
            for inc in incidents[:20]:
                lines.append(
                    f"- [{inc.get('severity')}] {inc.get('component')}: {inc.get('title')}"
                )

        lines += [
            "",
            "Project Visibility: health endpoint + local process + GitHub monitoring.",
            "BlogLab: monitored independently; normal publisher logic is not modified.",
            "P0/P1 alerts are sent independently of this periodic cycle.",
        ]
        return "\n".join(lines)

    def queue_if_due(self, report: dict[str, Any]) -> bool:
        if self.gmail.auth_state() != "CONFIGURED":
            return False

        now = datetime.now()
        if not self._is_due(now):
            return False

        body = self._render(report)
        stamp = now.strftime("%Y-%m-%d %H:%M")
        subject = (
            f"Agent Manager V4 status - {report.get('state','UNKNOWN')} - {stamp}"
        )
        self.store.execute(
            "INSERT INTO email_queue(created_at,kind,priority,recipient,subject,body,status) "
            "VALUES(?,?,?,?,?,?,'pending')",
            (
                now.isoformat(),
                "periodic_status",
                50,
                self.gmail.recipient or None,
                subject,
                body,
            ),
        )
        self.store.action(
            "reporting-v4",
            "periodic_email",
            stamp,
            "queued",
            {"subject": subject, "interval_hours": self.interval_hours},
        )
        return True


# Backward-compatible alias so older imports/config do not break.
DailyEmailReporterV4 = PeriodicEmailReporterV4
