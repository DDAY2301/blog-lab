from __future__ import annotations
from dataclasses import asdict
from .db_v3 import StoreV3
from .policy_v3 import evaluate
class AutoFixV3:
    SAFE={"restart_worker","retry_job","clear_stale_cache","reconnect_local_service"}
    def __init__(self,store:StoreV3): self.store=store
    def propose(self,incident:dict,action:str)->dict:
        pol=evaluate(action); payload={"incident_id":incident.get("id"),"action":action,"policy":{"decision":pol.decision.value,"risk":pol.risk,"reason":pol.reason}}
        self.store.action("autofix","propose",incident.get("component"),pol.decision.value,payload); return payload
    def execute_safe(self,incident:dict,action:str)->dict:
        pol=evaluate(action)
        if pol.decision.value!="ALLOW" or action not in self.SAFE: return {"ok":False,"stage":"policy","decision":pol.decision.value,"reason":pol.reason}
        return {"ok":False,"stage":"adapter_required","decision":"ALLOW","reason":"Safe action authorized; explicit target adapter must be registered before execution."}
