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
from .roles_v8 import EmailRolesV8
from .readonly_schedules_v8 import ReadonlySchedulesV8, SCHEDULE_RE, UNSCHEDULE_RE


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
        self.v8_enabled = self.bus.v8_enabled
        self.roles = EmailRolesV8(os.getenv("GMAIL_COMMAND_OWNER_EMAIL", gmail.recipient or ""))
        self.schedules = ReadonlySchedulesV8(store, self.bus, gmail)
        # One slow remote job must not block incoming STATUS or CANCEL mails.
        self._active: dict[str, asyncio.Task] = {}
        self.max_inflight = max(1, min(3, int(os.getenv("GMAIL_COMMAND_MAX_INFLIGHT", "2"))))
    def recover_interrupted(self) -> None:
        # Called only when the real Manager service starts, never during
        # imports or diagnostics against an already-running Manager.
        self.store.execute(
            "UPDATE command_jobs SET status='interrupted',updated_at=? "
            "WHERE status='running' AND source='gmail'", (utcnow(),),
        )
        self.store.execute(
            "UPDATE mail_commands SET status='interrupted',processed_at=? "
            "WHERE status='processing'", (utcnow(),),
        )
        self.schedules.recover_interrupted()

    def stop(self) -> None:
        self._stop.set()
        for task in list(self._active.values()):
            task.cancel()

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "email_control_version": "v8-preview" if self.v8_enabled else "v7-compat",
            "poll_seconds": self.interval,
            "inflight": len(self._active),
            "max_inflight": self.max_inflight,
            "role_configuration_valid": not bool(self.roles.config_error),
            "allowed_senders": sorted(self.allowed_senders),
            "require_authenticated_sender": os.getenv("GMAIL_COMMAND_REQUIRE_AUTH", "1") != "0",
            "last": self.last,
        }

    @staticmethod
    def _subject_target(subject: str) -> tuple[str | None, str]:
        text = re.sub(r"(?i)^\s*re:\s*", "", str(subject or "").strip())
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

    def _deny(self, details: dict[str, Any], reason: str) -> dict[str, Any]:
        # Keep rejected messages unread, but do not repeatedly process them.
        # Never send rejection details to a potentially spoofed From address.
        self.store.execute(
            """
            INSERT OR IGNORE INTO mail_commands(
              message_id,thread_id,sender,subject,target,command_text,status,received_at,processed_at,error
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                details["id"], details.get("thread_id", ""),
                details.get("sender", ""), details.get("subject", ""),
                "denied", "", "denied", utcnow(), utcnow(), reason[:200],
            ),
        )
        return {"id": details["id"], "status": "denied", "reason": reason}

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

    async def _schedule_operator(
        self, mid: str, sender: str, target: str, original: str, line: str,
    ) -> dict[str, Any]:
        status, error, result = "completed", "", None
        try:
            item = SCHEDULE_RE.fullmatch(line)
            cancelled = UNSCHEDULE_RE.fullmatch(line)
            if item:
                result = self.schedules.create(sender, item.group(1), item.group(2).strip())
            elif cancelled:
                result = self.schedules.cancel(sender, cancelled.group(1).upper())
            else:
                result = {"schedules": self.schedules.list_owned(sender)}
        except Exception as exc:
            status, error = "failed", f"{type(exc).__name__}: {exc}"
        reply_id = None
        try:
            reply_id = await asyncio.to_thread(
                self.gmail.send,
                f"[AGENT SCHEDULE RESULT] {status.upper()}",
                self._reply_body(target, original, status, result, error),
                sender,
            )
        except Exception as exc:
            if not error:
                status, error = "reply_failed", str(exc)
        self._finish(mid, status, result=result, error=error,
                     reply_message_id=reply_id)
        try:
            await asyncio.to_thread(self.gmail.mark_read, mid)
        except Exception:
            pass
        return {"id": mid, "status": status, "result": result}

    async def _handle_job_control(
        self, message_id: str, sender: str, target: str,
        explicit_target: str, original: str, parsed: tuple[str, str, str],
    ) -> dict[str, Any]:
        action, job_id, text = parsed
        result: dict[str, Any] | None = None
        status, error = "completed", ""
        try:
            controls = self.bus.controls
            if action == "STATUS":
                result = controls.inspect(job_id, sender)
            elif action == "CANCEL":
                result = controls.cancel(job_id, sender)
            elif action in {"REVIEW", "REJECT", "APPROVE"}:
                result = controls.review(job_id, sender, action)
            elif action in {"RETRY", "CONTINUE", "REVISE"}:
                previous = controls.previous(job_id, sender)
                if action == "RETRY":
                    if previous["status"] not in {
                        "failed", "partial", "interrupted", "cancelled"
                    } or not self.bus._simple_operator_target(previous["request_text"]):
                        raise ValueError("Retry is limited to failed read-only jobs.")
                    next_command = previous["request_text"]
                else:
                    next_command = text.strip()
                    if not next_command:
                        raise ValueError("Include new instructions after the job ID.")
                prior_steps = self.store.query(
                    "SELECT DISTINCT target FROM command_steps WHERE job_id=?",
                    (job_id,),
                )
                original_targets = {r["target"] for r in prior_steps}
                if len(original_targets) != 1 or not original_targets <= {
                    "manager", "project_visibility", "bloglab"
                }:
                    raise ValueError(
                        "Cannot safely resume an ambiguous multi-agent job. "
                        "Start a new email with an explicit [AGENT PV] or "
                        "[AGENT BLOGLAB] subject."
                    )
                original_target = next(iter(original_targets))
                result = await self.bus.execute(
                    next_command, source="gmail", source_id=message_id,
                    explicit_target=original_target,
                )
                if result.get("job_id"):
                    self.store.execute(
                        "UPDATE job_control_v8 SET parent_id=?,updated_at=? "
                        "WHERE job_id=?",
                        (job_id, utcnow(), result["job_id"]),
                    )
            else:
                raise ValueError("Unsupported job control command.")
        except Exception as exc:
            status, error = "failed", f"{type(exc).__name__}: {exc}"
        reply_id = None
        reply_job_id = (result or {}).get("job_id") if isinstance(result, dict) else None
        if not reply_job_id and len(job_id) == 36:
            reply_job_id = job_id
        subject = (
            f"[AGENT RESULT] JOB {reply_job_id} - {status.upper()}"
            if reply_job_id else f"[AGENT RESULT] {action} - {status.upper()}"
        )
        try:
            reply_id = await asyncio.to_thread(
                self.gmail.send,
                subject,
                self._reply_body(target, original, status, result, error),
                sender,
            )
        except Exception as exc:
            if not error:
                status, error = "reply_failed", str(exc)
        self._finish(message_id, status, result=result, error=error,
                     reply_message_id=reply_id)
        try:
            await asyncio.to_thread(self.gmail.mark_read, message_id)
        except Exception:
            pass
        return {"id": message_id, "status": status, "action": action, "result": result}

    async def process_one(self, message_id: str) -> dict[str, Any]:
        existing = self._seen(message_id)
        if existing:
            # Completed/failed command mail can be marked read. Messages that were
            # merely false-positive Gmail search candidates must keep their inbox
            # state untouched.
            if existing.get("status") not in {"ignored", "denied"}:
                try:
                    await asyncio.to_thread(self.gmail.mark_read, message_id)
                except Exception:
                    pass
            return {"id": message_id, "status": "duplicate", "stored_status": existing.get("status")}

        message = await asyncio.to_thread(self.gmail.get_message, message_id)
        details = self.gmail.message_details(message)
        raw_subject = details.get("subject", "")
        reply_job = re.match(
            r"(?i)^\s*re:\s*\[AGENT RESULT\]\s+JOB\s+"
            r"([0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})(?:\s|$)",
            raw_subject,
        )
        subject_target, subject_tail = self._subject_target(raw_subject)
        if self.v8_enabled and reply_job:
            subject_target, subject_tail = "manager", ""
        if details.get("agent_generated") or (
            not reply_job and re.match(r"(?i)^\s*\[AGENT RESULT\]", raw_subject)
        ):
            subject_target = None
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
        if self.v8_enabled and self.roles.config_error:
            return self._deny(details, "role_configuration_invalid")
        auth_required = os.getenv("GMAIL_COMMAND_REQUIRE_AUTH", "1") != "0"
        if sender not in self.allowed_senders or (
            auth_required and not details.get("sender_authenticated", False)
        ):
            self.store.action(
                "gmail-command-v4",
                "reject_sender",
                message_id,
                "denied",
                {
                    "sender": sender,
                    "subject": details["subject"],
                    "reason": "sender_not_allowed" if sender not in self.allowed_senders else "authentication_not_verified",
                    "authentication_method": details.get("authentication_method", "unverified"),
                },
            )
            # Reject spoofed or otherwise unverified mail without executing a
            # command or erasing the message. Keep available for manual review.
            return self._deny(
                details,
                "sender_not_allowed" if sender not in self.allowed_senders else "authentication_not_verified",
            )

        command = str(details.get("body") or "").strip()
        # Quoted replies/forwarded chains can contain old commands. Only
        # current unquoted text is eligible for command execution.
        command = re.split(
            r"(?im)^\s*(?:On .+ wrote:|From:\s+\S+|-----Original Message-----)",
            command,
            maxsplit=1,
        )[0]
        command = "\n".join(
            line for line in command.splitlines() if not line.lstrip().startswith(">")
        ).strip()
        if self.v8_enabled and reply_job and command and not self.bus.controls.parse(command):
            command = f"CONTINUE JOB {reply_job.group(1).lower()} : {command}"
        if subject_tail:
            # A short read-only subject like [AGENT] STATUS takes precedence
            # over phone signatures and boilerplate in the email body.
            job_subject = self.bus.controls.parse(subject_tail) if self.v8_enabled else None
            if job_subject:
                if job_subject[0] in {"CONTINUE", "REVISE"} and not job_subject[2]:
                    command = f"{subject_tail} : {command}".strip()
                else:
                    command = subject_tail
            elif self.bus._simple_operator_target(subject_tail):
                command = subject_tail
            else:
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
        if len(command) > 4000:
            self.store.action("gmail-command-v4", "reject_oversized_command",
                              message_id, "denied", {"length": len(command)})
            return self._deny(details, "command_too_long")
        parsed_control = self.bus.controls.parse(command)
        if self.v8_enabled and not parsed_control and not self.roles.allowed(sender, explicit_target or "all", command):
            return self._deny(details, "role_not_permitted")
        if self.v8_enabled and parsed_control and self.roles.role(sender) != "owner":
            return self._deny(details, "job_control_requires_owner")
        schedule_line = command.splitlines()[0].strip()
        is_schedule = bool(
            SCHEDULE_RE.fullmatch(schedule_line) or
            UNSCHEDULE_RE.fullmatch(schedule_line) or schedule_line.upper() == "SCHEDULES"
        )
        if self.v8_enabled and is_schedule and self.roles.role(sender) != "owner":
            return self._deny(details, "scheduling_requires_owner")
        self._insert_processing(details, target_label, command)
        if self.v8_enabled and is_schedule:
            return await self._schedule_operator(
                message_id, sender, target_label, command, schedule_line
            )

        parsed = self.bus.controls.parse(command)
        if self.v8_enabled and parsed:
            return await self._handle_job_control(
                message_id, sender, target_label, explicit_target, command, parsed
            )

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
                (f"[AGENT RESULT] JOB {result.get('job_id')} - {final_status.upper()}"
                 if self.v8_enabled else
                 f"[AGENT RESULT] {target_label.upper()} - {final_status.upper()}"),
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

    def _background_done(self, key: str, completed: asyncio.Task) -> None:
        self._active.pop(key, None)
        if completed.cancelled():
            return
        try:
            completed.result()
        except Exception as exc:
            self.store.event(
                "gmail_background_error", "gmail-command-v4", "error",
                {"message_id": key, "error": str(exc)[:1000]},
            )

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
        query = 'newer_than:7d subject:AGENT -subject:"Agent Manager V4"'
        if not self.v8_enabled:
            query += ' -subject:"[AGENT RESULT]"'
        rows = await asyncio.to_thread(
            self.gmail.list_messages,
            query,
            100,
        )
        results: list[dict[str, Any]] = []
        if not self.v8_enabled:
            for row in reversed(rows):
                results.append(await self.process_one(row["id"]))
            self.last = {
                "ok": not any(x.get("status") == "failed" for x in results),
                "enabled": True, "candidates": len(rows),
                "processed": results, "ts": utcnow(),
            }
            self.store.heartbeat("gmail-command-loop", "running")
            return self.last
        for row in reversed(rows):
            mid = row["id"]
            if mid in self._active or self._seen(mid):
                continue
            if len(self._active) >= self.max_inflight:
                break
            task = asyncio.create_task(self.process_one(mid))
            self._active[mid] = task
            task.add_done_callback(lambda done, key=mid: self._background_done(key, done))
            results.append({"id": mid, "status": "accepted"})
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
                if self.v8_enabled:
                    await self.schedules.run_due()
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
