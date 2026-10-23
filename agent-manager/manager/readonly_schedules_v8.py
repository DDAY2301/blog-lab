"""SQLite-backed one-shot read-only schedules; no production mutation by timer."""
from __future__ import annotations

import asyncio
import re
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .db_v3 import StoreV3, utcnow

try:
    LOCAL_TZ = ZoneInfo("Europe/Ljubljana")
except ZoneInfoNotFoundError:
    LOCAL_TZ = None  # Windows requires tzdata; keep the Manager online.
SCHEDULE_RE = re.compile(
    r"^SCHEDULE\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?)\s+(.+)$",
    re.I,
)
UNSCHEDULE_RE = re.compile(r"^UNSCHEDULE\s+(SCH-[0-9A-F]{12})$", re.I)


class ReadonlySchedulesV8:
    def __init__(self, store: StoreV3, bus, gmail):
        self.store, self.bus, self.gmail = store, bus, gmail
        with store.conn() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS readonly_schedules_v8(
                    schedule_id TEXT PRIMARY KEY,
                    owner_sender TEXT NOT NULL, command_text TEXT NOT NULL,
                    run_at_utc TEXT NOT NULL, status TEXT NOT NULL,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    result TEXT NOT NULL DEFAULT '');
                CREATE INDEX IF NOT EXISTS idx_schedules_due_v8
                ON readonly_schedules_v8(status,run_at_utc);
            """)
    def recover_interrupted(self) -> None:
        # Only the actual Manager startup can declare abandoned timer work;
        # a CLI import or smoke check must not change live job states.
        self.store.execute(
            "UPDATE readonly_schedules_v8 SET status='interrupted',updated_at=? "
            "WHERE status='running'", (utcnow(),),
        )

    def create(self, sender: str, local_iso: str, command: str) -> dict:
        if not self.bus._simple_operator_target(command):
            raise ValueError("Scheduled jobs are limited to read-only operator commands.")
        if LOCAL_TZ is None:
            raise ValueError("Timezone data unavailable. Install the tzdata Python package.")
        dt = datetime.fromisoformat(local_iso)
        if dt.tzinfo is not None:
            raise ValueError("Use local Europe/Ljubljana time without an offset.")
        aware = dt.replace(tzinfo=LOCAL_TZ)
        future = aware.astimezone(timezone.utc)
        if future.astimezone(LOCAL_TZ).replace(tzinfo=None) != dt:
            raise ValueError("Local scheduled time is not valid due to daylight-saving transition.")
        now = datetime.now(timezone.utc)
        if future < now or future > now + timedelta(days=365):
            raise ValueError("Schedule must be future-dated and within one year.")
        sid = "SCH-" + uuid.uuid4().hex[:12].upper()
        ts = utcnow()
        self.store.execute(
            """INSERT INTO readonly_schedules_v8
               (schedule_id,owner_sender,command_text,run_at_utc,status,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?)""",
            (sid, sender.lower(), command.strip(), future.isoformat(), "pending", ts, ts),
        )
        return {"schedule_id": sid, "status": "pending",
                "run_at_local": aware.isoformat(), "command": command.strip()}

    def list_owned(self, sender: str) -> list[dict]:
        return self.store.query(
            """SELECT schedule_id,command_text,run_at_utc,status,updated_at
               FROM readonly_schedules_v8 WHERE owner_sender=?
               ORDER BY run_at_utc LIMIT 30""",
            (sender.strip().lower(),),
        )

    def cancel(self, sender: str, schedule_id: str) -> dict:
        with self.store.conn() as conn:
            updated = conn.execute(
                """UPDATE readonly_schedules_v8 SET status='cancelled',updated_at=?
                   WHERE schedule_id=? AND owner_sender=? AND status='pending'""",
                (utcnow(), schedule_id.upper(), sender.strip().lower()),
            )
        return {"schedule_id": schedule_id.upper(), "cancelled": updated.rowcount == 1}

    async def run_due(self) -> list[dict]:
        candidates = self.store.query(
            """SELECT schedule_id,owner_sender,command_text
               FROM readonly_schedules_v8 WHERE status='pending'
               AND run_at_utc<=? ORDER BY run_at_utc LIMIT 2""", (utcnow(),),
        )
        results = []
        for row in candidates:
            sid = row["schedule_id"]
            with self.store.conn() as conn:
                claimed = conn.execute(
                    """UPDATE readonly_schedules_v8 SET status='running',updated_at=?
                       WHERE schedule_id=? AND status='pending'""",
                    (utcnow(), sid),
                )
            if claimed.rowcount != 1:
                continue
            try:
                outcome = await self.bus.execute(
                    row["command_text"], source="schedule", source_id=sid
                )
                status = "completed" if outcome.get("status") == "completed" else "failed"
                summary = str(outcome.get("status") or "unknown")
            except Exception as exc:
                status, summary = "failed", f"{type(exc).__name__}: {exc}"
            self.store.execute(
                """UPDATE readonly_schedules_v8 SET status=?,updated_at=?,result=?
                   WHERE schedule_id=?""", (status, utcnow(), summary[:1200], sid),
            )
            # Queue a result so email delivery can retry independently.
            self.store.execute(
                """INSERT INTO email_queue(created_at,kind,priority,recipient,subject,body,status)
                   VALUES(?,?,?,?,?,?,'pending')""",
                (utcnow(), "v8-schedule", 5, row["owner_sender"],
                 f"[AGENT SCHEDULE RESULT] {sid} - {status.upper()}",
                 f"Scheduled command: {row['command_text']}\nStatus: {status}\n{summary[:500]}"),
            )
            results.append({"schedule_id": sid, "status": status})
        return results
