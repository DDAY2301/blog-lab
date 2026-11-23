from __future__ import annotations
import asyncio,uuid
from .db_v3 import StoreV3
from .health_v3 import http_health,system_resources
from .incidents_v3 import IncidentEngineV3
from .settings_v3 import SettingsV3
class MonitorLoopV3:
    def __init__(self,s:SettingsV3,store:StoreV3): self.s=s; self.store=store; self.inc=IncidentEngineV3(store); self.running=False; self.last={}
    async def cycle(self):
        loop_id=uuid.uuid4().hex[:10]; self.store.heartbeat("manager","running",loop_id)
        resources=system_resources()
        if self.s.supervisor_only:
            # The production PV agent intentionally runs elsewhere in this mode.
            # Remote code/workflow health is checked by ManagedAgentSupervisorV4.
            # An absent local port 8000 must never become a P1 outage.
            pv={"ok": None, "state": "not_applicable", "reason": "supervisor_only; monitored by GitHub managed target"}
            self.inc.resolve_matching(
                "project_visibility", "Health endpoint unreachable",
                {"reason": "Local PV health probe disabled in supervisor-only mode; not a remote service recovery"}
            )
        else:
            pv=await http_health(self.s.pv_health_url)
            if not pv.get("ok"):
                self.inc.raise_or_update("project_visibility","Health endpoint unreachable","P1",[str(pv)])
            else:
                self.inc.resolve_matching("project_visibility","Health endpoint unreachable",{"health": pv})
        ollama=await http_health(self.s.ollama_base_url+"/api/tags")
        self.last={"loop_id":loop_id,"resources":resources,"project_visibility":pv,"ollama":ollama}; self.store.event("HEALTH_CYCLE","manager","info",self.last)
        if not ollama.get("ok"):
            self.inc.raise_or_update("ollama","Local AI runtime unreachable","P2",[str(ollama)])
        else:
            self.inc.resolve_matching("ollama","Local AI runtime unreachable",{"health": ollama})
        # Hysteresis avoids noisy alert flapping and closes stale incidents
        # once resources genuinely recover (including after Ollama unload).
        ram = resources.get("ram_percent")
        disk = resources.get("disk_percent")
        if isinstance(ram, (int, float)):
            if ram >= 92:
                self.inc.raise_or_update("system", "RAM critical", "P1", [str(resources)])
            elif ram <= 88:
                self.inc.resolve_matching("system", "RAM critical", {"ram_percent": ram})
            if ram >= 85:
                self.inc.raise_or_update("system", "RAM elevated", "P2", [str(resources)])
            elif ram <= 80:
                self.inc.resolve_matching("system", "RAM elevated", {"ram_percent": ram})
        if isinstance(disk, (int, float)):
            if disk >= 95:
                self.inc.raise_or_update("system", "Disk critical", "P0", [str(resources)])
            elif disk <= 90:
                self.inc.resolve_matching("system", "Disk critical", {"disk_percent": disk})
        return self.last
    async def run(self):
        self.running=True
        while self.running:
            try: await self.cycle()
            except Exception as exc: self.store.event("MONITOR_FAILURE","manager","error",{"error":str(exc)})
            await asyncio.sleep(self.s.monitor_interval)
    def stop(self): self.running=False
