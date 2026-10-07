from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .autofix_v3 import AutoFixV3
from .db_v3 import StoreV3
from .discovery_v3 import DiscoveryEngineV3
from .health_v3 import system_resources
from .incidents_v3 import IncidentEngineV3
from .maintenance_v4 import MaintenanceLoopV4
from .monitor_v3 import MonitorLoopV3
from .policy_v3 import evaluate
from .reporting_v3 import ReporterV3
from .settings_v3 import SettingsV3

VERSION = "4.0.0"
s = SettingsV3()
store = StoreV3(s.db_path)
discovery = DiscoveryEngineV3(store)
incidents = IncidentEngineV3(store)
reporter = ReporterV3(s, store)
monitor = MonitorLoopV3(s, store)
maintenance = MaintenanceLoopV4(s, store)
autofix = AutoFixV3(store)

_tasks: list[asyncio.Task] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    discovery.discover_roots(s.roots())
    _tasks.append(asyncio.create_task(monitor.run(), name="system-monitor"))
    _tasks.append(asyncio.create_task(maintenance.run(), name="maintenance-v4"))
    yield
    monitor.stop()
    maintenance.stop()
    for task in _tasks:
        task.cancel()
    for task in _tasks:
        try:
            await task
        except BaseException:
            pass


app = FastAPI(
    title="Agent Manager V4",
    version=VERSION,
    description="24/7 local multi-agent maintenance center with Colibri/Ollama routing.",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    store.heartbeat("manager", "running")
    return {
        "ok": True,
        "version": VERSION,
        "mode": "24x7-maintenance",
        "write_enabled": s.write_enabled,
        "gmail": reporter.auth_state(),
        "open_incidents": len(incidents.open()),
        "resources": system_resources(),
        "last_system_cycle": monitor.last,
        "last_maintenance_cycle": maintenance.last,
    }


@app.get("/system-map")
async def system_map():
    return discovery.system_map(s.roots())


@app.post("/discover")
async def discover():
    return discovery.system_map(s.roots())


@app.get("/agents")
async def agents():
    return {
        "local_registry": store.query("SELECT * FROM agents ORDER BY name"),
        "managed_targets": maintenance.supervisor.status_rows(),
    }


@app.get("/managed-agents")
async def managed_agents():
    return {
        "configured": [x.__dict__ for x in maintenance.supervisor.targets()],
        "status": maintenance.supervisor.status_rows(),
    }


@app.post("/managed-agents/check")
async def managed_agents_check():
    return {"targets": await maintenance.supervisor.check_all()}


@app.post("/managed-agents/{target_id}/repair")
async def repair_managed_agent(target_id: str):
    target = next((x for x in maintenance.supervisor.targets() if x.id == target_id), None)
    if not target:
        raise HTTPException(404, "managed target not found")
    result = maintenance.supervisor.repair(target)
    store.action("operator", "manual_repair", target_id, "completed", result)
    return result


@app.get("/providers")
async def providers():
    return await maintenance.ai.status()


@app.get("/incidents")
async def incident_list():
    return {"incidents": store.query("SELECT * FROM incidents ORDER BY last_seen DESC LIMIT 200")}


@app.post("/incidents/{incident_id}/diagnose")
async def diagnose_incident(incident_id: str):
    rows = store.query("SELECT * FROM incidents WHERE id=?", (incident_id,))
    if not rows:
        raise HTTPException(404, "incident not found")
    return await maintenance.diagnose_incident(rows[0])


@app.get("/events")
async def events():
    return {"events": store.query("SELECT * FROM events ORDER BY id DESC LIMIT 200")}


@app.get("/notifications")
async def notifications():
    return {"notifications": maintenance.notify.recent(200)}


@app.get("/summary")
async def summary():
    targets = await maintenance.supervisor.check_all()
    providers = await maintenance.ai.status()
    return maintenance.summary.build(targets, providers)


@app.get("/connections")
async def connections():
    providers = await maintenance.ai.status()
    return {
        "project_visibility": monitor.last.get("project_visibility"),
        "ollama": monitor.last.get("ollama"),
        "colibri": providers.get("colibri"),
        "ai_priority": providers.get("priority"),
        "gmail": reporter.auth_state(),
        "managed_agents": maintenance.supervisor.status_rows(),
    }


class ManagedTargetInput(BaseModel):
    id: str
    name: str
    kind: str
    enabled: bool = True
    health_url: str = ""
    repo: str = ""
    branch: str = "main"
    workflows: list[str] | None = None
    repair_adapter: str = ""
    local_root_env: str = ""
    process_match: str = ""
    interval_seconds: int = 60


@app.put("/managed-agents/{target_id}")
async def upsert_managed_agent(target_id: str, item: ManagedTargetInput):
    payload = item.model_dump()
    payload["id"] = target_id
    try:
        target = maintenance.supervisor.save_target(payload)
    except (TypeError, ValueError) as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"ok": True, "target": target.__dict__}


@app.delete("/managed-agents/{target_id}")
async def delete_managed_agent(target_id: str):
    removed = maintenance.supervisor.remove_target(target_id)
    if not removed:
        raise HTTPException(404, "managed target not found")
    return {"ok": True, "removed": target_id}


class ActionRequest(BaseModel):
    action: str
    incident_id: str | None = None


@app.post("/policy/evaluate")
async def policy(req: ActionRequest):
    p = evaluate(req.action)
    return {"decision": p.decision.value, "risk": p.risk, "reason": p.reason}


@app.post("/autofix/propose")
async def fix(req: ActionRequest):
    if not req.incident_id:
        raise HTTPException(400, "incident_id required")
    rows = store.query("SELECT * FROM incidents WHERE id=?", (req.incident_id,))
    if not rows:
        raise HTTPException(404, "incident not found")
    return autofix.propose(rows[0], req.action)


@app.post("/monitor/run-once")
async def run_once():
    return await monitor.cycle()


@app.post("/maintenance/run-once")
async def maintenance_once():
    return await maintenance.cycle()


@app.get("/control", response_class=HTMLResponse)
async def control():
    return HTMLResponse(
        """<!doctype html>
<html>
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Agent Manager V4</title>
<style>
:root{color-scheme:dark}body{font-family:Inter,system-ui;background:#091018;color:#eef5fb;margin:0}
main{max-width:1450px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;gap:16px;align-items:center}
.badge{padding:6px 10px;border-radius:999px;background:#143326;color:#85e6a9;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:14px;margin-top:18px}
.card{background:#111b26;border:1px solid #263a4c;border-radius:16px;padding:18px;box-shadow:0 8px 30px #0004}
pre{white-space:pre-wrap;word-break:break-word;color:#bed0df;max-height:420px;overflow:auto}
h1{margin:0}h3{margin-top:0;color:#fff}.muted{color:#8ea3b5}
button{background:#1e6f50;color:#fff;border:0;border-radius:10px;padding:9px 12px;cursor:pointer}
input,select{width:100%;box-sizing:border-box;background:#0d151e;color:#eef5fb;border:1px solid #2d4356;border-radius:9px;padding:9px;margin:5px 0 9px}
label{font-size:12px;color:#9db0bf}.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.wide{grid-column:1/-1}.msg{font-size:13px;color:#9fdcb8;margin-top:8px}
</style>
</head>
<body><main>
<div class="top"><div><h1>Agent Manager V4</h1><div class="muted">24/7 maintenance · Colibri/Ollama · Project Visibility · BlogLab</div></div><div class="badge">LOCAL CONTROL CENTER</div></div>
<div style="margin-top:14px"><button onclick="refresh()">Refresh</button> <button onclick="post('/maintenance/run-once')">Run maintenance now</button></div>
<div class="grid">
<div class="card"><h3>Health</h3><pre id="health">loading</pre></div>
<div class="card"><h3>AI Providers</h3><pre id="providers">loading</pre></div>
<div class="card"><h3>Managed Agents</h3><pre id="agents">loading</pre>
<details><summary>Add / update monitored agent</summary>
<div class="formgrid" style="margin-top:10px">
<div><label>ID</label><input id="a_id" placeholder="my-agent"></div>
<div><label>Name</label><input id="a_name" placeholder="My Agent"></div>
<div><label>Type</label><select id="a_kind"><option value="http">HTTP health</option><option value="github_repo">GitHub workflows</option><option value="hybrid">Hybrid</option><option value="process">Local process</option></select></div>
<div><label>Check interval (sec)</label><input id="a_interval" type="number" min="30" max="3600" value="60"></div>
<div class="wide"><label>Health URL</label><input id="a_url" placeholder="http://127.0.0.1:9000/health"></div>
<div><label>GitHub repo</label><input id="a_repo" placeholder="owner/repo"></div>
<div><label>Branch</label><input id="a_branch" value="main"></div>
<div class="wide"><label>Process contains</label><input id="a_process" placeholder="agent.py or executable name"></div>
<div class="wide"><button onclick="saveAgent()">Save monitored agent</button><div id="agentmsg" class="msg"></div></div>
</div></details></div>
<div class="card"><h3>Incidents</h3><pre id="incidents">loading</pre></div>
<div class="card"><h3>Notifications</h3><pre id="notifications">loading</pre></div>
<div class="card"><h3>System Map</h3><pre id="map">loading</pre></div>
</div>
</main>
<script>
async function j(u){return(await fetch(u)).json()}
async function post(u){await fetch(u,{method:'POST'});setTimeout(refresh,700)}
async function saveAgent(){
 const id=document.getElementById('a_id').value.trim();
 const name=document.getElementById('a_name').value.trim();
 if(!id||!name){document.getElementById('agentmsg').textContent='ID and name are required.';return}
 const body={
  id,name,kind:document.getElementById('a_kind').value,enabled:true,
  health_url:document.getElementById('a_url').value.trim(),
  repo:document.getElementById('a_repo').value.trim(),
  branch:document.getElementById('a_branch').value.trim()||'main',
  workflows:null,repair_adapter:'',local_root_env:'',
  process_match:document.getElementById('a_process').value.trim(),
  interval_seconds:Number(document.getElementById('a_interval').value||60)
 };
 const r=await fetch('/managed-agents/'+encodeURIComponent(id),{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 let d={};try{d=await r.json()}catch{}
 document.getElementById('agentmsg').textContent=r.ok?'Saved. Monitoring begins automatically.':(d.detail||'Could not save target.');
 if(r.ok) setTimeout(refresh,500);
}
async function refresh(){
 for(const [id,u] of [['health','/health'],['providers','/providers'],['agents','/managed-agents'],['incidents','/incidents'],['notifications','/notifications'],['map','/system-map']]){
  try{document.getElementById(id).textContent=JSON.stringify(await j(u),null,2)}
  catch(e){document.getElementById(id).textContent=String(e)}
 }
}
refresh();setInterval(refresh,15000)
</script></body></html>"""
    )
