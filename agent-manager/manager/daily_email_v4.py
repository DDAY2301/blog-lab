from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from .db_v3 import StoreV3
from .gmail_v4 import GmailV4


class DailyEmailReporterV4:
    def __init__(self, store: StoreV3, gmail: GmailV4) -> None:
        self.store = store
        self.gmail = gmail
        self.hour = max(0, min(23, int(os.getenv("AGENT_MANAGER_DAILY_EMAIL_HOUR", "9"))))

    def _already_sent_today(self, day: str) -> bool:
        rows = self.store.query(
            "SELECT id FROM actions WHERE actor='reporting-v4' AND action='daily_email' AND target=? AND result='sent' LIMIT 1",
            (day,),
        )
        return bool(rows)

    def _already_queued_today(self, day: str) -> bool:
        rows = self.store.query(
            "SELECT id FROM email_queue WHERE kind='daily_status' AND created_at LIKE ? AND status IN ('pending','sent') LIMIT 1",
            (day + "%",),
        )
        return bool(rows)

    def _render(self, report: dict[str, Any]) -> str:
        lines = [
            "AGENT MANAGER V4 - DAILY STATUS",
            "",
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
        for key in ("colibri","ollama"):
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
            "Project Visibility is monitored locally by health endpoint/process checks and recovery logic.",
            "BlogLab is monitored independently and its normal publisher flow is not modified by this report.",
        ]
        return "\n".join(lines)

    def queue_if_due(self, report: dict[str, Any]) -> bool:
        if self.gmail.auth_state() not in {"CONFIGURED", "AUTH_REQUIRED", "CLIENT_SECRET_REQUIRED"}:
            return False
        now = datetime.now()
        if now.hour < self.hour:
            return False
        day = now.date().isoformat()
        if self._already_sent_today(day) or self._already_queued_today(day):
            return False

        body = self._render(report)
        subject = f"Agent Manager V4 daily status - {report.get('state','UNKNOWN')} - {day}"
        self.store.execute(
            "INSERT INTO email_queue(created_at,kind,priority,recipient,subject,body,status) VALUES(?,?,?,?,?,?,'pending')",
            (now.isoformat(), "daily_status", 50, self.gmail.recipient or None, subject, body),
        )
        # Mark queued; after a successful flush we promote to sent below.
        self.store.action("reporting-v4", "daily_email", day, "queued", {"subject": subject})
        return True

    def mark_sent_if_complete(self) -> None:
        today = datetime.now().date().isoformat()
        sent = self.store.query(
            "SELECT id FROM email_queue WHERE kind='daily_status' AND status='sent' AND created_at LIKE ? LIMIT 1",
            (today + "%",),
        )
        if sent and not self._already_sent_today(today):
            self.store.action("reporting-v4", "daily_email", today, "sent", {})
