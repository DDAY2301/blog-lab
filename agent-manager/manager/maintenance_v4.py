from __future__ import annotations

import asyncio
import os
import uuid
from pathlib import Path
from typing import Any

from .ai_router_v4 import AIRouterV4
from .db_v3 import StoreV3
from .managed_agents_v4 import ManagedAgentSupervisorV4
from .notifications_v4 import NotificationCenterV4
from .settings_v3 import SettingsV3


class MaintenanceLoopV4:
    def __init__(self, settings: SettingsV3, store: StoreV3) -> None:
        self.settings = settings
        self.store = store
        config = Path(os.getenv("AGENT_MANAGER_TARGETS", "./data/managed_agents.json")).expanduser()
        if not config.is_absolute():
            config = Path(__file__).resolve().parents[1] / config
        self.supervisor = ManagedAgentSupervisorV4(store, config)
        self.ai = AIRouterV4()
        self.notify = NotificationCenterV4(store)
        self.interval = max(30, int(os.getenv("AGENT_MANAGER_MAINTENANCE_INTERVAL", "60")))
        self.running = False
        self.last: dict[str, Any] = {}

    async def cycle(self) -> dict[str, Any]:
        loop_id = uuid.uuid4().hex[:10]
        targets = await self.supervisor.check_all()
        providers = await self.ai.status()
        triage = await self._colibri_triage_targets(targets)
        diagnoses = await self._auto_diagnose_open_incidents()
        self.last = {
            "loop_id": loop_id,
            "targets": targets,
            "ai_providers": providers,
            "colibri_triage": triage,
            "automatic_diagnoses": diagnoses,
        }
        self.store.heartbeat("maintenance-v4", "running", loop_id)
        self.store.event("MAINTENANCE_CYCLE", "maintenance-v4", "info", self.last)
        return self.last

    async def _colibri_triage_targets(self, targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for target in targets:
            if target.get("ok"):
                continue
            state = str(target)[:8000]
            decision = await self.ai.triage(state)
            if decision:
                out.append({"target_id": target.get("id"), "decision": decision})
                self.store.action("maintenance-v4", "colibri_triage", str(target.get("id","")), "completed", {"result": decision})
        return out

    async def _auto_diagnose_open_incidents(self) -> list[dict[str, Any]]:
        rows = self.store.query(
            "SELECT * FROM incidents WHERE status!='resolved' AND severity IN ('P0','P1') ORDER BY last_seen DESC LIMIT 5"
        )
        out: list[dict[str, Any]] = []
        for incident in rows:
            done = self.store.query(
                "SELECT id FROM actions WHERE actor='maintenance-v4' AND action='ai_diagnosis' AND target=? LIMIT 1",
                (incident["id"],),
            )
            if done:
                continue
            try:
                out.append({"incident_id": incident["id"], **(await self.diagnose_incident(incident))})
            except Exception as exc:
                self.store.event("AI_DIAGNOSIS_FAILED", "maintenance-v4", "warning", {"incident_id": incident["id"], "error": str(exc)})
        return out

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
        self.store.action("maintenance-v4", "ai_diagnosis", str(incident.get("id","")), "completed", {"provider": model, "result": result})
        return {"provider": model, "diagnosis": result}

    async def run(self) -> None:
        self.running = True
        while self.running:
            try:
                await self.cycle()
            except Exception as exc:
                self.store.event("MAINTENANCE_FAILURE", "maintenance-v4", "error", {"error": str(exc)})
            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        self.running = False
