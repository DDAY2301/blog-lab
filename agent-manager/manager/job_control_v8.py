from __future__ import annotations

import re
import uuid
from typing import Any

from .db_v3 import StoreV3, utcnow

JOB_CMD = re.compile(
    r"^(STATUS|CANCEL|RETRY|CONTINUE|REVISE)\s+(?:JOB[\s:-]*)?"
    r"([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})(?:\s*[:\-]\s*|\s+)?(.*)$",
    re.I | re.S,
)
REVIEW_CMD = re.compile(r"^(APPROVE|REJECT|REVIEW)\s+(REV-[0-9a-f]{12})$", re.I)
RISK = re.compile(
    r"\b(deploy|publish|merge|delete|rollback|objavi|izbrisi|odstrani|"
    r"restart|ponovno zazeni|ustavi|production)\b", re.I,
)


class JobControlV8:
    """Owner-scoped SQLite job controls, no email-only production approval."""

    def __init__(self, store: StoreV3):
        self.store = store
        with store.conn() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS job_control_v8(
                    job_id TEXT PRIMARY KEY, sender TEXT NOT NULL,
                    thread_id TEXT NOT NULL DEFAULT '', parent_id TEXT NOT NULL DEFAULT '',
                    cancel_requested INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS job_reviews_v8(
                    review_id TEXT PRIMARY KEY, job_id TEXT NOT NULL,
                    step_id TEXT NOT NULL, target TEXT NOT NULL,
                    summary TEXT NOT NULL, sender TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending', updated_at TEXT NOT NULL,
                    UNIQUE(job_id,step_id));
            """)

    @staticmethod
    def parse(text: str) -> tuple[str, str, str] | None:
        text = text.strip()
        m = JOB_CMD.fullmatch(text)
        if m:
            return m.group(1).upper(), m.group(2).lower(), (m.group(3) or "").strip()
        m = REVIEW_CMD.fullmatch(text)
        if m:
            return m.group(1).upper(), m.group(2).upper(), ""
        return None

    @staticmethod
    def requires_review(target: str, command: str) -> bool:
        # Fail closed. Free-form instructions and AI-planned steps are untrusted,
        # even when they avoid the known risky keywords.
        command = command.strip().lower()
        readonly = {
            "status", "stanje", "health", "preveri status",
            "status vseh agentov", "flota", "fleet status", "pomoc",
            "help", "incidenti", "incidents", "napake", "ram",
            "pomnilnik", "memory", "modeli", "models", "providers",
            "email status", "gmail status", "opravila", "jobs", "queue",
            "github status", "rollback plan bloglab", "rollback plan pv",
        }
        diagnostics = {"test api", "api ci", "ci", "preveri ci",
                       "frontend benchmark", "frontend qa", "lighthouse"}
        if target == "all":
            return command not in {
                "status", "stanje", "health", "status vseh agentov",
                "preveri status", "flota", "fleet status",
            }
        if command in readonly:
            return False
        if target == "project_visibility" and command in diagnostics:
            return False
        if target == "project_visibility" and command.startswith("preview_json ") and len(command) <= 4000:
            # Generates an isolated preview artifact; cannot publish or edit a repository.
            return False
        return True

    def bind(self, job: str, sender: str, thread: str = "", parent: str = "") -> None:
        if sender:
            self.store.execute(
                """INSERT OR IGNORE INTO job_control_v8
                   (job_id,sender,thread_id,parent_id,updated_at) VALUES(?,?,?,?,?)""",
                (job, sender.strip().lower(), thread, parent, utcnow()),
            )

    def _owned(self, job: str, sender: str) -> dict[str, Any]:
        rows = self.store.query("SELECT * FROM job_control_v8 WHERE job_id=?", (job,))
        if not rows or rows[0]["sender"] != sender.strip().lower():
            raise ValueError("Unknown job or sender not authorized.")
        return rows[0]

    def inspect(self, job: str, sender: str) -> dict[str, Any]:
        control = self._owned(job, sender)
        record = self.store.query(
            "SELECT id,status,created_at,updated_at,error FROM command_jobs WHERE id=?",
            (job,),
        )
        steps = self.store.query(
            """SELECT step_id,target,status,error,result_json FROM command_steps
               WHERE job_id=? ORDER BY rowid""", (job,),
        )
        reviews = self.store.query(
            """SELECT review_id,status,target FROM job_reviews_v8
               WHERE job_id=?""", (job,),
        )
        return {
            "job": record[0] if record else None, "steps": steps,
            "reviews": reviews, "cancel_requested": bool(control["cancel_requested"]),
            "parent_id": control["parent_id"] or None,
        }

    def cancel(self, job: str, sender: str) -> dict[str, Any]:
        data = self.inspect(job, sender)
        status = data["job"]["status"] if data["job"] else "unknown"
        if status not in {"running", "queued"}:
            return {"accepted": False, "status": status, "job": job}
        self.store.execute(
            "UPDATE job_control_v8 SET cancel_requested=1,updated_at=? WHERE job_id=?",
            (utcnow(), job),
        )
        return {"accepted": True, "job": job,
                "note": "Stops only undispatched steps, not in-flight remote work."}

    def cancelled(self, job: str) -> bool:
        rows = self.store.query(
            "SELECT cancel_requested FROM job_control_v8 WHERE job_id=?", (job,)
        )
        return bool(rows and rows[0]["cancel_requested"])

    def previous(self, job: str, sender: str) -> dict[str, Any]:
        self._owned(job, sender)
        rows = self.store.query(
            "SELECT id,status,request_text FROM command_jobs WHERE id=?", (job,)
        )
        if not rows:
            raise ValueError("Job record unavailable.")
        return rows[0]

    def request_review(self, job: str, step: str, target: str,
                       summary: str, sender: str) -> str:
        rows = self.store.query(
            "SELECT review_id FROM job_reviews_v8 WHERE job_id=? AND step_id=?",
            (job, step),
        )
        if rows:
            return rows[0]["review_id"]
        rid = "REV-" + uuid.uuid4().hex[:12].upper()
        self.store.execute(
            """INSERT INTO job_reviews_v8
               (review_id,job_id,step_id,target,summary,sender,updated_at)
               VALUES(?,?,?,?,?,?,?)""",
            (rid, job, step, target, summary[:500], sender.lower(), utcnow()),
        )
        return rid

    def review(self, rid: str, sender: str, verb: str) -> dict[str, Any]:
        rows = self.store.query(
            "SELECT * FROM job_reviews_v8 WHERE review_id=?", (rid,)
        )
        if not rows or rows[0]["sender"] != sender.strip().lower():
            raise ValueError("Review request not found or sender not authorized.")
        row = rows[0]
        if verb == "REJECT" and row["status"] == "pending":
            self.store.execute(
                "UPDATE job_reviews_v8 SET status='rejected',updated_at=? WHERE review_id=?",
                (utcnow(), rid),
            )
            return {"review": rid, "status": "rejected", "executed": False}
        return {
            "review": rid, "status": row["status"], "job": row["job_id"],
            "executed": False,
            "message": "APPROVE by email cannot deploy. Independent authenticated review required.",
        }

    def console_approve(self, rid: str) -> dict[str, Any]:
        """Authenticated Fleet Remote review: approve record, never execute a step."""
        from datetime import datetime, timedelta, timezone
        rows = self.store.query(
            "SELECT * FROM job_reviews_v8 WHERE review_id=?", (rid,)
        )
        if not rows:
            raise ValueError("Review request was not found.")
        row = rows[0]
        if row["status"] != "pending":
            raise ValueError("Review is not pending.")
        issued = datetime.fromisoformat(row["updated_at"])
        if datetime.now(timezone.utc) - issued > timedelta(hours=24):
            raise ValueError("Review expired; request a fresh review.")
        with self.store.conn() as conn:
            updated = conn.execute(
                "UPDATE job_reviews_v8 SET status='approved',updated_at=? "
                "WHERE review_id=? AND status='pending'", (utcnow(), rid),
            )
            if updated.rowcount != 1:
                raise ValueError("Review state changed concurrently.")
        self.store.action(
            "fleet-console-v8", "approve_review", row["job_id"], "approved",
            {"review_id": rid, "target": row["target"], "executed": False},
        )
        return {
            "review": rid, "status": "approved", "executed": False,
            "note": "Review approved by authenticated console, but no production "
                    "action is executed until a separate delivery gate exists.",
        }
