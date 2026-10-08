from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any

from .artifacts_v2 import MAX_EMAIL_ARTIFACT_BYTES
from .command_bus_v2 import UniversalCommandBusV2
from .db_v3 import StoreV3, utcnow
from .gmail_v4 import GmailV4


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
        self.bus = UniversalCommandBusV2(store)

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
    def _reply_body(target: str, command: str, status: str, result: Any = None, error: str = "") -> str:
        lines = [
            "Agent Manager V4 — Universal Command Bus V2",
            "",
            f"Requested target: {target or 'AUTO'}",
            f"Status: {status.upper()}",
            "",
            "Command:",
            command,
            "",
        ]
        if result is not None:
            rendered = json.dumps(result, ensure_ascii=False, indent=2, default=str)
            lines.extend(["Execution:", rendered[:18000]])
        if error:
            lines.extend(["", "Error:", error[:6000]])
        lines.extend(
            [
                "",
                "Routing:",
                "[AGENT] = natural-language automatic planning",
                "[AGENT ALL] = all registered agents",
                "[AGENT MANAGER] = Agent Manager",
                "[AGENT PV] = Project Visibility",
                "[AGENT BLOGLAB] = BlogLab",
                "Attachments are ingested automatically; supported BlogLab images are uploaded and passed to the publishing command.",
            ]
        )
        return "\n".join(lines)

    async def process_one(self, message_id: str) -> dict[str, Any]:
        existing = self._seen(message_id)
        if existing:
            # Completed/failed command mail can be marked read. Messages that were
            # merely false-positive Gmail search candidates must keep their inbox
            # state untouched.
            if existing.get("status") != "ignored":
                try:
                    await asyncio.to_thread(self.gmail.mark_read, message_id)
                except Exception:
                    pass
            return {"id": message_id, "status": "duplicate", "stored_status": existing.get("status")}

        message = await asyncio.to_thread(self.gmail.get_message, message_id)
        details = self.gmail.message_details(message)
        subject_target, subject_tail = self._subject_target(details["subject"])
        if subject_target is None:
            # Gmail subject search is token-based and can match e.g. "Agent
            # Manager V4" alerts. Remember the immutable message id so we do not
            # repeatedly fetch/parse the same false positive, but do not change
            # its unread/read state.
            self.store.execute(
                """
                INSERT OR IGNORE INTO mail_commands(
                  message_id,thread_id,sender,subject,target,command_text,status,received_at,processed_at
                ) VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    details["id"],
                    details.get("thread_id", ""),
                    details.get("sender", ""),
                    details.get("subject", ""),
                    "ignored",
                    "",
                    "ignored",
                    utcnow(),
                    utcnow(),
                ),
            )
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

        command = str(details.get("body") or "").strip()
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

        explicit_target = subject_target or ""
        target_label = explicit_target or "auto"
        self._insert_processing(details, target_label, command)

        artifacts: list[dict[str, Any]] = []
        total_bytes = 0
        try:
            for attachment in details.get("attachments") or []:
                raw = await asyncio.to_thread(self.gmail.attachment_bytes, message_id, attachment)
                total_bytes += len(raw)
                if total_bytes > MAX_EMAIL_ARTIFACT_BYTES:
                    raise RuntimeError(
                        f"Combined attachments exceed {MAX_EMAIL_ARTIFACT_BYTES} bytes."
                    )
                metadata = {
                    "gmail_attachment_id": str(attachment.get("attachment_id") or ""),
                    "content_id": str(attachment.get("content_id") or ""),
                    "content_disposition": str(attachment.get("content_disposition") or ""),
                }
                artifacts.append(
                    self.bus.artifacts.save_bytes(
                        source="gmail",
                        source_id=message_id,
                        filename=str(attachment.get("filename") or "attachment.bin"),
                        mime_type=str(attachment.get("mime_type") or "application/octet-stream"),
                        data=raw,
                        metadata=metadata,
                    )
                )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            self.store.action(
                "gmail-command-v4",
                "attachment_ingest_failed",
                message_id,
                "failed",
                {"error": error[:1200]},
            )
            reply_id = ""
            try:
                reply_id = await asyncio.to_thread(
                    self.gmail.send,
                    f"[AGENT RESULT] {target_label.upper()} — FAILED",
                    self._reply_body(target_label, command, "failed", error=error),
                    sender,
                )
            except Exception:
                pass
            self._finish(message_id, "failed", error=error, reply_message_id=reply_id or None)
            await asyncio.to_thread(self.gmail.mark_read, message_id)
            return {"id": message_id, "status": "failed", "target": target_label, "error": error}

        self.store.action(
            "gmail-command-v4",
            "command_received",
            target_label,
            "processing",
            {
                "message_id": message_id,
                "sender": sender,
                "router": "subject" if explicit_target else "universal-planner-v2",
                "subject": details["subject"],
                "attachments": len(artifacts),
            },
        )

        try:
            result = await self.bus.execute(
                command,
                source="gmail",
                source_id=message_id,
                explicit_target=explicit_target,
                artifacts=artifacts,
            )
            final_status = str(result.get("status") or "completed")
            ok = final_status == "completed"
            reply_id = await asyncio.to_thread(
                self.gmail.send,
                f"[AGENT RESULT] {target_label.upper()} — {final_status.upper()}",
                self._reply_body(target_label, command, final_status, result=result),
                sender,
            )
            self._finish(message_id, final_status, result=result, reply_message_id=reply_id)
            await asyncio.to_thread(self.gmail.mark_read, message_id)
            self.store.action(
                "gmail-command-v4",
                "command_completed" if ok else "command_partial",
                target_label,
                final_status,
                {
                    "message_id": message_id,
                    "reply_message_id": reply_id,
                    "job_id": result.get("job_id"),
                    "attachments": len(artifacts),
                },
            )
            return {
                "id": message_id,
                "status": final_status,
                "target": target_label,
                "job_id": result.get("job_id"),
                "reply_message_id": reply_id,
                "artifacts": len(artifacts),
            }
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            reply_id = ""
            try:
                reply_id = await asyncio.to_thread(
                    self.gmail.send,
                    f"[AGENT RESULT] {target_label.upper()} — FAILED",
                    self._reply_body(target_label, command, "failed", error=error),
                    sender,
                )
            except Exception:
                pass
            self._finish(message_id, "failed", error=error, reply_message_id=reply_id or None)
            await asyncio.to_thread(self.gmail.mark_read, message_id)
            self.store.action(
                "gmail-command-v4",
                "command_failed",
                target_label,
                "failed",
                {"message_id": message_id, "error": error[:1500], "attachments": len(artifacts)},
            )
            return {"id": message_id, "status": "failed", "target": target_label, "error": error}

    async def cycle(self) -> dict[str, Any]:
        if not self.enabled:
            self.last = {"ok": True, "enabled": False}
            return self.last
        if self.gmail.auth_state() != "CONFIGURED":
            self.last = {"ok": False, "enabled": True, "gmail_state": self.gmail.auth_state()}
            return self.last

        # Do not depend on Gmail UNREAD state: an operator may open a command on
        # their phone before the 30s poll. Gmail only narrows candidates; exact
        # [AGENT ...] validation and message-id idempotency happen locally.
        rows = await asyncio.to_thread(
            self.gmail.list_messages,
            'newer_than:7d subject:AGENT -subject:"[AGENT RESULT]" -subject:"Agent Manager V4"',
            100,
        )
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
