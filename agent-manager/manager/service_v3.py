from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .autofix_v3 import AutoFixV3
from .db_v3 import StoreV3
from .discovery_v3 import DiscoveryEngineV3
from .health_v3 import system_resources
from .incidents_v3 import IncidentEngineV3
from .monitor_v3 import MonitorLoopV3
from .policy_v3 import evaluate
from .reporting_v3 import ReporterV3
from .settings_v3 import SettingsV3

VERSION="3.0.0"
s=SettingsV3(); store=StoreV3(s.db_path); discovery=DiscoveryEngineV3(store); incidents=IncidentEngineV3(store); reporter=ReporterV3(s,store); monitor=MonitorLoopV3(s,store); autofix=AutoFixV3(store)
_task=None

@asynccontextmanager
async def lifespan(app:FastAPI):
    global _task
    discovery.discover_roots(s.roots())
    _task=asyncio.create_task(monitor.run())
    yield
    monitor.stop()
    if _task:
        _task.cancel()
        try: await _task
        except BaseException: pass

app=FastAPI(title="Agent Manager V3",version=VERSION,description="Local-first autonomous operations center",lifespan=lifespan)

@app.get("/health")
async def health():
    store.heartbeat("manager","running")
    return {"ok":True,"version":VERSION,"mode":"maximum-local","write_enabled":s.write_enabled,"gmail":reporter.auth_state(),"open_incidents":len(incidents.open()),"resources":system_resources(),"last_cycle":monitor.last}

@app.get("/system-map")
async def system_map(): return discovery.system_map(s.roots())
@app.post("/discover")
async def discover(): return discovery.system_map(s.roots())
@app.get("/agents")
async def agents(): return {"agents":store.query("SELECT * FROM agents ORDER BY name")}
@app.get("/incidents")
async def incident_list(): return {"incidents":store.query("SELECT * FROM incidents ORDER BY last_seen DESC LIMIT 200")}
@app.get("/events")
async def events(): return {"events":store.query("SELECT * FROM events ORDER BY id DESC LIMIT 200")}
@app.get("/connections")
async def connections(): return {"project_visibility":monitor.last.get("project_visibility"),"ollama":monitor.last.get("ollama"),"gmail":reporter.auth_state()}

class ActionRequest(BaseModel):
    action:str
    incident_id:str|None=None

@app.post("/policy/evaluate")
async def policy(req:ActionRequest):
    p=evaluate(req.action); return {"decision":p.decision.value,"risk":p.risk,"reason":p.reason}

@app.post("/autofix/propose")
async def fix(req:ActionRequest):
    if not req.incident_id: raise HTTPException(400,"incident_id required")
    rows=store.query("SELECT * FROM incidents WHERE id=?",(req.incident_id,))
    if not rows: raise HTTPException(404,"incident not found")
    return autofix.propose(rows[0],req.action)

@app.post("/monitor/run-once")
async def run_once(): return await monitor.cycle()

@app.get("/control",response_class=HTMLResponse)
async def control():
    return HTMLResponse("""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>Agent Manager V3</title><style>body{font-family:system-ui;background:#0b0f14;color:#eaf0f6;margin:0}main{max-width:1200px;margin:auto;padding:28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}.card{background:#131a22;border:1px solid #263241;border-radius:14px;padding:18px}pre{white-space:pre-wrap;word-break:break-word;color:#b9c7d8}h1{margin-top:0}</style></head><body><main><h1>Agent Manager V3</h1><div class='grid'><div class='card'><h3>Health</h3><pre id='health'>loading</pre></div><div class='card'><h3>Connections</h3><pre id='connections'>loading</pre></div><div class='card'><h3>Incidents</h3><pre id='incidents'>loading</pre></div><div class='card'><h3>System Map</h3><pre id='map'>loading</pre></div></div></main><script>async function j(u){return(await fetch(u)).json()}async function refresh(){for(const [id,u] of [['health','/health'],['connections','/connections'],['incidents','/incidents'],['map','/system-map']]){try{document.getElementById(id).textContent=JSON.stringify(await j(u),null,2)}catch(e){document.getElementById(id).textContent=String(e)}}}refresh();setInterval(refresh,10000)</script></body></html>""")
