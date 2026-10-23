from __future__ import annotations
import hashlib,json,uuid
from .db_v3 import StoreV3,utcnow
class IncidentEngineV3:
    def __init__(self,store:StoreV3): self.store=store
    @staticmethod
    def fingerprint(component:str,title:str)->str: return hashlib.sha256(f"{component}|{title}".lower().encode()).hexdigest()[:24]
    def raise_or_update(self,component:str,title:str,severity:str,evidence:list[str]|None=None)->dict:
        fp=self.fingerprint(component,title); now=utcnow(); rows=self.store.query("SELECT * FROM incidents WHERE fingerprint=?",(fp,))
        if rows:
            iid=rows[0]["id"]; self.store.execute("UPDATE incidents SET severity=?,status='open',occurrence_count=occurrence_count+1,last_seen=?,evidence=? WHERE id=?",(severity,now,json.dumps(evidence or []),iid))
        else:
            iid=f"INC-{uuid.uuid4().hex[:10].upper()}"; self.store.execute("INSERT INTO incidents(id,fingerprint,severity,status,component,title,evidence,first_seen,last_seen) VALUES(?,?,?,?,?,?,?,?,?)",(iid,fp,severity,"open",component,title,json.dumps(evidence or []),now,now))
        self.store.execute("INSERT INTO incident_events(incident_id,ts,state,payload) VALUES(?,?,?,?)",(iid,now,"detected",json.dumps({"severity":severity,"evidence":evidence or []})))
        return self.store.query("SELECT * FROM incidents WHERE id=?",(iid,))[0]
    def resolve(self,incident_id:str,payload:dict|None=None):
        now=utcnow(); self.store.execute("UPDATE incidents SET status='resolved',resolved_at=?,last_seen=? WHERE id=?",(now,now,incident_id))
        self.store.execute("INSERT INTO incident_events(incident_id,ts,state,payload) VALUES(?,?,?,?)",(incident_id,now,"resolved",json.dumps(payload or {})))
    def resolve_matching(self, component: str, title: str, payload: dict | None = None) -> bool:
        fp = self.fingerprint(component, title)
        rows = self.store.query("SELECT id FROM incidents WHERE fingerprint=? AND status!='resolved'", (fp,))
        if not rows:
            return False
        self.resolve(rows[0]["id"], payload or {"reason": "health restored"})
        return True

    def open(self): return self.store.query("SELECT * FROM incidents WHERE status!='resolved' ORDER BY last_seen DESC")
