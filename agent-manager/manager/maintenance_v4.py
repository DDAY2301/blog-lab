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
        self.last = {
            "loop_id": loop_id,
            "targets": targets,
            "ai_providers": providers,
        }
        self.store.heartbeat("maintenance-v4", "running", loop_id)
        self.store.event("MAINTENANCE_CYCLE", "maintenance-v4", "info", self.last)
        return self.last

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
