from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any

from .ai_router_v4 import AIRouterV4
from .db_v3 import StoreV3, utcnow
from .gmail_v4 import GmailV4
from .remote_v4 import _dispatch


class GmailCommandLoopV4:
    """Poll a Gmail inbox and route authenticated command emails to the agent fleet."""

    def __init__(self, store: StoreV3, gmail: GmailV4) -> None:
        self.store = store
        self.gmail = gmail
        self.enabled = os.getenv("GMAIL_COMMANDS_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
        self.interval = max(15, int(os.getenv("GMAIL_COMMAND_POLL_SECONDS", "30")))
        allowed = os.getenv("GMAIL_COMMAND_ALLOWED_SENDERS", gmail.recipient or "").strip()
        self.allowed_senders = {x.strip().lower() for x in allowed.split(",") if x.strip()}
        self._stop = asyncio.Event()
        self.last: dict[str, Any] = {}
        self.ai = AIRouterV4()

    def stop(self) -> None:
        self._stop.set()

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "poll_seconds": self.interval,
            "allowed_senders": sorted(self.allowed_senders),
            "last": self.last,
        }

    @staticmethod
    def _subject_target(subject: str) -> tuple[str | None, str]:
        text = str(subject or "").strip()
        match = re.match(
            r"^\[AGENT(?:\s+(ALL|BLOG(?:LAB)?|PV|PROJECT(?:\s+VISIBILITY)?|MANAGER|AM))?\]\s*(.*)$",
            text,
            flags=re.IGNORECASE,
        )
        if not match:
            return None, ""
        raw = (match.group(1) or "").strip().lower()
        tail = (match.group(2) or "").strip()
        mapping = {
            "all": "all",
            "blog": "bloglab",
            "bloglab": "bloglab",
            "pv": "project_visibility",
            "project": "project_visibility",
            "project visibility": "project_visibility",
            "manager": "manager",
            "am": "manager",
        }
        return mapping.get(raw) if raw else "", tail

    @staticmethod
    def _keyword_target(command: str) -> str:
        low = command.lower()
        if any(x in low for x in ("bloglab", "blog lab", "članek", "clanek", "objav", "blog ")):
            return "bloglab"
        if any(x in low for x in ("project visibility", "projekt visibility", "preflight", "builder", "website agent")):
            return "project_visibility"
        if any(x in low for x in ("agent manager", "manager", "incident", "maintenance", "gmail", "provider")):
            return "manager"
        return "all"

    async def _resolve_target(self, command: str) -> tuple[str, str]:
        fallback = self._keyword_target(command)
        system = (
            "Route an operator command to exactly one of: manager, project_visibility, bloglab, all. "
            "manager = health/maintenance/incidents/providers; project_visibility = website builder/QA/preflight; "
            "bloglab = blog content/site publishing; all = fleet-wide status or instructions intended for every agent. "
            "Return JSON only: {\"target\":\"...\",\"reason\":\"...\"}."
        )
        try:
            provider, data = await self.ai.chat_json(system, command)
            target = str(data.get("target") or "").strip().lower()
            if target in {"manager", "project_visibility", "bloglab", "all"}:
                return target, provider
        except Exception:
            pass
        return fallback, "deterministic"

    def _seen(self, message_id: str) -> dict[str, Any] | None:
        rows = self.store.query("SELECT * FROM mail_commands WHERE message_id=?", (message_id,))
        return rows[0] if rows else None

    def _insert_processing(self, details: dict[str, str], target: str, command: str) -> None:
        self.store.execute(
            """
            INSERT INTO mail_commands(
              message_id,thread_id,sender,subject,target,command_text,status,received_at
            ) VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                details["id"],
                details.get("thread_id", ""),
                details["sender"],
                details["subject"],
                target,
                command,
                "processing",
                utcnow(),
            ),
        )

    def _finish(
        self,
        message_id: str,
        status: str,
        *,
        result: dict[str, Any] | None = None,
        error: str | None = None,
        reply_message_id: str | None = None,
    ) -> None:
        self.store.execute(
            """
            UPDATE mail_commands
            SET status=?,processed_at=?,result=?,error=?,reply_message_id=?
            WHERE message_id=?
            """,
            (
                status,
                utcnow(),
                json.dumps(result, ensure_ascii=False)[:30000] if result is not None else None,
                (error or "")[:4000] or None,
                reply_message_id,
                message_id,
            ),
        )

    @staticmethod
    def _reply_body(target: str, command: str, ok: bool, result: Any = None, error: str = "") -> str:
        lines = [
            "Agent Manager V4 — email command result",
            "",
            f"Target: {target}",
            f"Status: {'COMPLETED' if ok else 'FAILED'}",
            "",
            "Command:",
            command,
            "",
        ]
        if ok:
            rendered = json.dumps(result, ensure_ascii=False, indent=2, default=str)
            lines.extend(["Result:", rendered[:18000]])
        else:
            lines.extend(["Error:", error[:6000]])
        lines.extend(
            [
                "",
                "Command syntax:",
                "[AGENT] = automatic routing",
                "[AGENT ALL] = all three agents",
                "[AGENT MANAGER] = Agent Manager",
                "[AGENT PV] = Project Visibility",
                "[AGENT BLOGLAB] = BlogLab",
            ]
        )
        return "\n".join(lines)

    async def process_one(self, message_id: str) -> dict[str, Any]:
        existing = self._seen(message_id)
        if existing:
            # Idempotency: a Gmail retry must never execute the same command twice.
            try:
                await asyncio.to_thread(self.gmail.mark_read, message_id)
            except Exception:
                pass
            return {"id": message_id, "status": "duplicate", "stored_status": existing.get("status")}

        message = await asyncio.to_thread(self.gmail.get_message, message_id)
        details = self.gmail.message_details(message)
        subject_target, subject_tail = self._subject_target(details["subject"])
        if subject_target is None:
            return {"id": message_id, "status": "ignored"}

        sender = details["sender"]
        if sender not in self.allowed_senders:
            self.store.action(
                "gmail-command-v4",
                "reject_sender",
                message_id,
                "denied",
                {"sender": sender, "subject": details["subject"]},
            )
            await asyncio.to_thread(self.gmail.mark_read, message_id)
            return {"id": message_id, "status": "denied", "sender": sender}

        command = details["body"].strip()
        if subject_tail:
            command = f"{subject_tail}\n\n{command}".strip()
        if not command:
            await asyncio.to_thread(
                self.gmail.send,
                "[AGENT RESULT] FAILED — empty command",
                "The command email did not contain a command in the subject or body.",
                sender,
            )
            await asyncio.to_thread(self.gmail.mark_read, message_id)
            return {"id": message_id, "status": "empty"}

        if subject_target:
            target = subject_target
            router = "subject"
        else:
            target, router = await self._resolve_target(command)

        self._insert_processing(details, target, command)
        self.store.action(
            "gmail-command-v4",
            "command_received",
            target,
            "processing",
            {"message_id": message_id, "sender": sender, "router": router, "subject": details["subject"]},
        )

        try:
            result = await _dispatch(target, command)
            reply_body = self._reply_body(target, command, True, result=result)
            reply_id = await asyncio.to_thread(
                self.gmail.send,
                f"[AGENT RESULT] {target.upper()} — COMPLETED",
                reply_body,
                sender,
            )
            self._finish(message_id, "completed", result=result, reply_message_id=reply_id)
            await asyncio.to_thread(self.gmail.mark_read, message_id)
            self.store.action(
                "gmail-command-v4",
                "command_completed",
                target,
                "completed",
                {"message_id": message_id, "reply_message_id": reply_id, "router": router},
            )
            return {"id": message_id, "status": "completed", "target": target, "reply_message_id": reply_id}
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            reply_id = ""
            try:
                reply_id = await asyncio.to_thread(
                    self.gmail.send,
                    f"[AGENT RESULT] {target.upper()} — FAILED",
                    self._reply_body(target, command, False, error=error),
                    sender,
                )
            except Exception:
                pass
            self._finish(message_id, "failed", error=error, reply_message_id=reply_id or None)
            await asyncio.to_thread(self.gmail.mark_read, message_id)
            self.store.action(
                "gmail-command-v4",
                "command_failed",
                target,
                "failed",
                {"message_id": message_id, "error": error[:1500], "router": router},
            )
            return {"id": message_id, "status": "failed", "target": target, "error": error}

    async def cycle(self) -> dict[str, Any]:
        if not self.enabled:
            self.last = {"ok": True, "enabled": False}
            return self.last
        if self.gmail.auth_state() != "CONFIGURED":
            self.last = {"ok": False, "enabled": True, "gmail_state": self.gmail.auth_state()}
            return self.last

        # Gmail narrows the candidate set; exact [AGENT ...] validation happens locally.
        rows = await asyncio.to_thread(self.gmail.list_messages, "is:unread newer_than:7d subject:AGENT", 30)
        results: list[dict[str, Any]] = []
        for row in reversed(rows):
            results.append(await self.process_one(row["id"]))
        self.last = {
            "ok": not any(x.get("status") == "failed" for x in results),
            "enabled": True,
            "candidates": len(rows),
            "processed": results,
            "ts": utcnow(),
        }
        self.store.heartbeat("gmail-command-loop", "running")
        return self.last

    async def run(self) -> None:
        while not self._stop.is_set():
            try:
                await self.cycle()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.last = {"ok": False, "error": str(exc), "ts": utcnow()}
                self.store.event(
                    "gmail_command_cycle_failed",
                    "gmail-command-v4",
                    "error",
                    {"error": str(exc)[:2000]},
                )
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass
