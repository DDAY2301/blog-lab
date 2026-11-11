from __future__ import annotations
import hashlib,json,socket
from pathlib import Path
from .db_v3 import StoreV3,utcnow
MARKERS=("pyproject.toml","requirements.txt","package.json","docker-compose.yml","compose.yaml","README.md")
def stable_id(kind:str,value:str)->str: return f"{kind}-{hashlib.sha256(value.lower().encode()).hexdigest()[:12]}"
class DiscoveryEngineV3:
    def __init__(self,store:StoreV3): self.store=store
    def discover_roots(self,roots:list[Path])->list[dict]:
        out=[]
        for raw in roots:
            p=raw.resolve() if raw.exists() else raw
            if not p.exists() or not p.is_dir(): out.append({"root":str(p),"status":"missing"}); continue
            git=(p/".git").exists(); markers=[m for m in MARKERS if (p/m).exists()]; aid=stable_id("project",str(p)); now=utcnow()
            self.store.execute("INSERT INTO agents(id,name,kind,root,status,health,metadata,first_seen,last_seen) VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status,metadata=excluded.metadata,last_seen=excluded.last_seen",(aid,p.name,"project",str(p),"ready",100,json.dumps({"git":git,"markers":markers}),now,now))
            out.append({"id":aid,"name":p.name,"root":str(p),"status":"ready","git":git,"markers":markers})
        return out
    def discover_processes(self)->list[dict]:
        try:
            import psutil
            wanted={"python","python.exe","ollama","ollama.exe","cloudflared","cloudflared.exe","node","node.exe","git","git.exe"}; rows=[]
            for p in psutil.process_iter(["pid","name","cmdline"]):
                try:
                    if (p.info.get("name") or "").lower() in wanted: rows.append({"pid":p.info["pid"],"name":p.info["name"],"cmdline":(p.info.get("cmdline") or [])[:6]})
                except Exception: pass
            return rows
        except Exception: return []
    def port_open(self,host:str,port:int,timeout:float=.4)->bool:
        try:
            with socket.create_connection((host,port),timeout=timeout): return True
        except OSError: return False
    def system_map(self,roots:list[Path])->dict:
        return {"projects":self.discover_roots(roots),"processes":self.discover_processes(),"ports":{"manager":self.port_open("127.0.0.1",8787),"project_visibility":self.port_open("127.0.0.1",8000),"ollama":self.port_open("127.0.0.1",11434)}}
