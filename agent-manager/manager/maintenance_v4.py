from __future__ import annotations

import asyncio
import os
import time
import uuid
from pathlib import Path
from typing import Any, Awaitable, Callable

from .ai_router_v4 import AIRouterV4
from .db_v3 import StoreV3
from .managed_agents_v4 import ManagedAgentSupervisorV4
from .notifications_v4 import NotificationCenterV4
from .settings_v3 import SettingsV3
from .summary_v4 import SummaryReporterV4
from .gmail_v4 import GmailV4
from .daily_email_v4 import DailyEmailReporterV4


class MaintenanceLoopV4:
    """Deterministic monitoring stays on schedule; AI work runs out-of-band."""

    def __init__(self, settings: SettingsV3, store: StoreV3) -> None:
        self.settings = settings
        self.store = store
        config = Path(os.getenv("AGENT_MANAGER_TARGETS", "./data/managed_agents.json")).expanduser()
        if not config.is_absolute():
            config = Path(__file__).resolve().parents[1] / config
        self.supervisor = ManagedAgentSupervisorV4(store, config)
        self.ai = AIRouterV4()
        self.notify = NotificationCenterV4(store)
        self.summary = SummaryReporterV4(store, self.notify)
        self.gmail = GmailV4(store)
        self.daily_email = DailyEmailReporterV4(store, self.gmail)
        self.interval = max(30, int(os.getenv("AGENT_MANAGER_MAINTENANCE_INTERVAL", "60")))
        self.running = False
        self.last: dict[str, Any] = {}
        self._background: set[asyncio.Task] = set()
        self._inflight: set[str] = set()
        self._last_ai_at: dict[str, float] = {}
        self.ai_cooldown = max(120, int(os.getenv("AGENT_MANAGER_AI_DIAGNOSIS_COOLDOWN", "300")))

    async def cycle(self) -> dict[str, Any]:
        loop_id = uuid.uuid4().hex[:10]
        targets = await self.supervisor.check_all()

        try:
            providers = await asyncio.wait_for(self.ai.status(), timeout=5.0)
        except Exception as exc:
            providers = {"ok": False, "error": str(exc)}

        self._schedule_ai_work(targets)
        summary = self.summary.emit(targets, providers)
        live_report = self.summary.build(targets, providers)
        live_report["targets"] = targets
        self.daily_email.queue_if_due(live_report)
        gmail_flush = await asyncio.to_thread(self.gmail.flush_queue)
        self.daily_email.mark_sent_if_complete()

        self.last = {
            "loop_id": loop_id,
            "targets": targets,
            "ai_providers": providers,
            "ai_jobs_pending": len(self._background),
            "summary": summary,
            "gmail": {
                "state": self.gmail.auth_state(),
                "recipient": self.gmail.recipient or None,
                "flush": gmail_flush,
            },
        }
        self.store.heartbeat("maintenance-v4", "running", loop_id)
        self.store.event("MAINTENANCE_CYCLE", "maintenance-v4", "info", self.last)
        return self.last

    def _spawn(self, key: str, factory: Callable[[], Awaitable[Any]]) -> None:
        if key in self._inflight:
            return
        self._inflight.add(key)

        async def runner() -> None:
            try:
                await factory()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.store.event(
                    "AI_BACKGROUND_FAILURE",
                    "maintenance-v4",
                    "warning",
                    {"key": key, "error": str(exc)},
                )
            finally:
                self._inflight.discard(key)

        task = asyncio.create_task(runner(), name=f"maintenance-ai:{key}")
        self._background.add(task)
        task.add_done_callback(self._background.discard)

    def _schedule_ai_work(self, targets: list[dict[str, Any]]) -> None:
        now = time.time()

        for target in targets:
            if target.get("ok") or target.get("cached"):
                continue
            target_id = str(target.get("id") or target.get("name") or "unknown")
            key = f"triage:{target_id}"
            if now - self._last_ai_at.get(key, 0) >= self.ai_cooldown:
                self._last_ai_at[key] = now
                self._spawn(key, lambda target=target: self._triage_one(target))

        rows = self.store.query(
            "SELECT * FROM incidents WHERE status!='resolved' AND severity IN ('P0','P1') ORDER BY last_seen DESC LIMIT 5"
        )
        for incident in rows:
            incident_id = str(incident["id"])
            done = self.store.query(
                "SELECT id FROM actions WHERE actor='maintenance-v4' AND action='ai_diagnosis' AND target=? LIMIT 1",
                (incident_id,),
            )
            if done:
                continue
            self._spawn(f"diagnose:{incident_id}", lambda incident=incident: self._diagnose_one(incident))

    async def _triage_one(self, target: dict[str, Any]) -> None:
        state = str(target)[:8000]
        try:
            triage_timeout = max(30.0, float(os.getenv("AGENT_MANAGER_COLIBRI_TRIAGE_TIMEOUT", "120")))
            decision = await asyncio.wait_for(self.ai.triage(state), timeout=triage_timeout)
        except asyncio.TimeoutError:
            self.store.event(
                "COLIBRI_TRIAGE_TIMEOUT",
                "maintenance-v4",
                "warning",
                {"target_id": target.get("id")},
            )
            return
        if decision:
            self.store.action(
                "maintenance-v4",
                "colibri_triage",
                str(target.get("id", "")),
                "completed",
                {"result": decision},
            )

    async def _diagnose_one(self, incident: dict[str, Any]) -> None:
        try:
            await asyncio.wait_for(self.diagnose_incident(incident), timeout=120.0)
        except asyncio.TimeoutError:
            self.store.event(
                "AI_DIAGNOSIS_TIMEOUT",
                "maintenance-v4",
                "warning",
                {"incident_id": incident.get("id")},
            )

    async def diagnose_incident(self, incident: dict[str, Any]) -> dict[str, Any]:
        system = (
            "You are the local Agent Manager maintenance engineer. "
            "Use evidence only. Return JSON with summary, likely_cause, safe_actions, confidence. "
            "Do not propose destructive actions, credential bypasses, or direct production edits."
        )
        user = (
            "Diagnose this incident and propose reversible recovery steps.\n"
            + str(incident)[:12000]
        )
        model, result = await self.ai.chat_json(system, user)
        self.store.action(
            "maintenance-v4",
            "ai_diagnosis",
            str(incident.get("id", "")),
            "completed",
            {"provider": model, "result": result},
        )
        return {"provider": model, "diagnosis": result}

    async def run(self) -> None:
        self.running = True
        while self.running:
            try:
                await self.cycle()
            except Exception as exc:
                self.store.event(
                    "MAINTENANCE_FAILURE",
                    "maintenance-v4",
                    "error",
                    {"error": str(exc)},
                )
            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        self.running = False
        for task in list(self._background):
            task.cancel()
