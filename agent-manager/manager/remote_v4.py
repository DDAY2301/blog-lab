from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from .db_v3 import StoreV3
from .settings_v3 import SettingsV3

ROOT = Path(__file__).resolve().parents[1]
SESSION_COOKIE = "agent_fleet_session"
SESSION_TTL_SECONDS = 60 * 60 * 12
MANAGER_BASE = "http://127.0.0.1:8787"
PROJECT_BASE = "http://127.0.0.1:8000"
BLOG_LAB_BASE = os.getenv("BLOG_LAB_WORKER_URL", "https://blog-lab.dan-grmusa.workers.dev").rstrip("/")
store = StoreV3(SettingsV3().db_path)

_login_failures: dict[str, list[float]] = {}


def _secret(name: str) -> str:
    return os.getenv(name, "").strip()


def _remote_password() -> str:
    return _secret("FLEET_REMOTE_PASSWORD")


def _session_key() -> bytes:
    pwd = _remote_password()
    return hashlib.sha256(("agent-manager-fleet-v1\n" + pwd).encode("utf-8")).digest()


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * ((4 - len(value) % 4) % 4))


def _make_session() -> str:
    payload = json.dumps(
        {"exp": int(time.time()) + SESSION_TTL_SECONDS, "role": "operator"},
        separators=(",", ":"),
    ).encode("utf-8")
    body = _b64(payload)
    sig = _b64(hmac.new(_session_key(), body.encode("ascii"), hashlib.sha256).digest())
    return f"{body}.{sig}"


def _valid_session(token: str) -> bool:
    if not _remote_password() or "." not in token:
        return False
    try:
        body, sig = token.split(".", 1)
        expected = _b64(hmac.new(_session_key(), body.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return False
        payload = json.loads(_unb64(body))
        return payload.get("role") == "operator" and int(payload.get("exp", 0)) > int(time.time())
    except Exception:
        return False


def _client_ip(request: Request) -> str:
    return (
        request.headers.get("cf-connecting-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "unknown")
    )


def _rate_limited(request: Request) -> bool:
    ip = _client_ip(request)
    now = time.time()
    recent = [x for x in _login_failures.get(ip, []) if now - x < 60]
    _login_failures[ip] = recent
    return len(recent) >= 8


def _record_login_failure(request: Request) -> None:
    ip = _client_ip(request)
    _login_failures.setdefault(ip, []).append(time.time())


def _authorized(request: Request) -> bool:
    return _valid_session(request.cookies.get(SESSION_COOKIE, ""))


def _security_headers(response: Response) -> Response:
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


def _json(data: Any, status: int = 200) -> JSONResponse:
    return _security_headers(JSONResponse(data, status_code=status))


def _fold(value: str) -> str:
    text = str(value or "").lower()
    text = text.translate(str.maketrans({"č": "c", "š": "s", "ž": "z", "ć": "c", "đ": "d"}))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


async def _http(method: str, url: str, **kwargs) -> dict[str, Any]:
    timeout = kwargs.pop("timeout", 120.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.request(method, url, **kwargs)
    text = response.text
    try:
        data = response.json()
    except Exception:
        data = {"text": text[:3000]}
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP {response.status_code}: {data}")
    return data


async def _fleet_status() -> dict[str, Any]:
    async def grab(url: str):
        try:
            return {"ok": True, "data": await _http("GET", url, timeout=8)}
        except Exception as exc:
            return {"ok": False, "error": str(exc)[:1200]}

    manager, project, bloglab = await asyncio.gather(
        grab(f"{MANAGER_BASE}/health"),
        grab(f"{PROJECT_BASE}/health"),
        grab(f"{BLOG_LAB_BASE}/health"),
    )
    return {
        "ok": manager["ok"] and project["ok"] and bloglab["ok"],
        "manager": manager,
        "project_visibility": project,
        "bloglab": bloglab,
        "integrations": {
            "project_token_ready": bool(_secret("FLEET_LOCAL_TOKEN")),
            "bloglab_token_ready": bool(_secret("FLEET_AGENT_TOKEN")),
            "remote_password_ready": bool(_remote_password()),
        },
    }


async def _manager_command(command: str) -> dict[str, Any]:
    low = _fold(command)
    if low in {"status", "health", "stanje"} or "preveri status" in low:
        return {"action": "status", "result": await _http("GET", f"{MANAGER_BASE}/health", timeout=10)}
    if "email" in low and ("test" in low or "mail" in low):
        return {"action": "email_test", "result": await _http("POST", f"{MANAGER_BASE}/email/send-test", timeout=45)}
    if "incident" in low:
        return {"action": "incidents", "result": await _http("GET", f"{MANAGER_BASE}/incidents", timeout=10)}
    if "provider" in low or "model" in low:
        return {"action": "providers", "result": await _http("GET", f"{MANAGER_BASE}/providers", timeout=20)}
    if "check" in low or "preveri agente" in low or "preglej agente" in low:
        return {"action": "check_all", "result": await _http("POST", f"{MANAGER_BASE}/managed-agents/check", timeout=90)}
    if "restart project" in low or "restart visibility" in low or "ponovno zazeni project" in low:
        return {
            "action": "restart_project_visibility",
            "result": await _http("POST", f"{MANAGER_BASE}/managed-agents/project_visibility/repair", timeout=90),
        }
    if "maintenance" in low or "vzdrzevan" in low or "preglej in popravi" in low or "preveri in popravi" in low:
        return {"action": "maintenance", "result": await _http("POST", f"{MANAGER_BASE}/maintenance/run-once", timeout=180)}
    if "restart manager" in low or "ponovno zazeni manager" in low:
        script = ROOT / "scripts" / "restart-agent-manager.ps1"
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
        return {"action": "restart_manager", "accepted": True}
    raise RuntimeError(
        "Unsupported Agent Manager command. Use: status, maintenance/preglej in popravi, "
        "preveri agente, incidenti, modeli/providers, test email, restart Project Visibility, restart manager."
    )


async def _project_command(command: str) -> dict[str, Any]:
    token = _secret("FLEET_LOCAL_TOKEN")
    if not token:
        raise RuntimeError("FLEET_LOCAL_TOKEN is not configured.")
    return await _http(
        "POST",
        f"{PROJECT_BASE}/internal/fleet/command",
        headers={"x-fleet-token": token},
        json={"command": command},
        timeout=180,
    )


async def _bloglab_command(command: str) -> dict[str, Any]:
    token = _secret("FLEET_AGENT_TOKEN")
    if not token:
        raise RuntimeError("FLEET_AGENT_TOKEN is not configured.")
    return await _http(
        "POST",
        f"{BLOG_LAB_BASE}/api/fleet/command",
        headers={"authorization": f"Bearer {token}"},
        json={"command": command, "actor": "agent-manager-v4", "mode": "auto"},
        timeout=90,
    )


async def _dispatch(target: str, command: str) -> dict[str, Any]:
    if target == "manager":
        return await _manager_command(command)
    if target == "project_visibility":
        return await _project_command(command)
    if target == "bloglab":
        return await _bloglab_command(command)
    if target == "all":
        if _fold(command) in {"status", "health", "stanje"}:
            return await _fleet_status()
        results: dict[str, Any] = {}
        for name, fn in (
            ("manager", _manager_command),
            ("project_visibility", _project_command),
            ("bloglab", _bloglab_command),
        ):
            try:
                results[name] = {"ok": True, "result": await fn(command)}
            except Exception as exc:
                results[name] = {"ok": False, "error": str(exc)[:1600]}
        return {"targets": results}
    raise RuntimeError("Unknown fleet target.")


class LoginIn(BaseModel):
    password: str = Field(min_length=1, max_length=256)


class CommandIn(BaseModel):
    target: str = Field(pattern="^(manager|project_visibility|bloglab|all)$")
    command: str = Field(min_length=1, max_length=4000)


app = FastAPI(title="Agent Manager Fleet Remote", version="1.0.0")


@app.middleware("http")
async def secure_headers(request: Request, call_next):
    response = await call_next(request)
    return _security_headers(response)


@app.get("/health")
async def health():
    return {
        "ok": True,
        "service": "agent-manager-fleet-remote",
        "configured": bool(_remote_password()),
        "project_token_ready": bool(_secret("FLEET_LOCAL_TOKEN")),
        "bloglab_token_ready": bool(_secret("FLEET_AGENT_TOKEN")),
    }


@app.post("/api/login")
async def login(data: LoginIn, request: Request):
    if _rate_limited(request):
        raise HTTPException(429, "Too many login attempts")
    expected = _remote_password()
    if len(expected) < 16:
        raise HTTPException(503, "Remote control is not configured")
    if not hmac.compare_digest(data.password, expected):
        _record_login_failure(request)
        await asyncio.sleep(0.5)
        raise HTTPException(401, "Invalid password")
    response = _json({"ok": True})
    response.set_cookie(
        SESSION_COOKIE,
        _make_session(),
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/",
    )
    return response


@app.post("/api/logout")
async def logout():
    response = _json({"ok": True})
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response


@app.get("/api/status")
async def fleet_status(request: Request):
    if not _authorized(request):
        raise HTTPException(401, "Login required")
    return await _fleet_status()


@app.post("/api/command")
async def fleet_command(data: CommandIn, request: Request):
    if not _authorized(request):
        raise HTTPException(401, "Login required")
    started = time.time()
    try:
        result = await _dispatch(data.target, data.command)
        status = "completed"
        error = None
    except Exception as exc:
        result = None
        status = "failed"
        error = str(exc)[:1800]

    payload = {
        "target": data.target,
        "command": data.command[:1000],
        "duration_ms": round((time.time() - started) * 1000, 1),
        "client_ip": _client_ip(request),
        "error": error,
    }
    try:
        store.action("fleet-remote", "remote_command", data.target, status, payload)
    except Exception:
        pass

    if error:
        return _json({"ok": False, "target": data.target, "error": error}, 502)
    return _json({"ok": True, "target": data.target, "result": result})


LOGIN_HTML = """<!doctype html><html lang="sl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Fleet Control</title><style>
:root{font-family:Inter,system-ui;color:#eaf1f7;background:#081018}*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:radial-gradient(circle at 80% 10%,#173b56 0,transparent 34rem),#081018}
.card{width:min(430px,calc(100% - 28px));padding:28px;border:1px solid #26394a;border-radius:20px;background:#101c27;box-shadow:0 30px 80px #0008}.eyebrow{font-size:11px;letter-spacing:.16em;color:#83afd1}.card h1{font:700 32px Georgia,serif;margin:10px 0}.card p{color:#92a7b7;line-height:1.6;font-size:14px}input{width:100%;height:48px;margin-top:14px;border:1px solid #31506a;border-radius:11px;background:#09131c;color:#fff;padding:0 13px}button{width:100%;height:48px;margin-top:10px;border:0;border-radius:11px;background:#7fa9d1;color:#0a1721;font-weight:900;cursor:pointer}.err{min-height:20px;color:#ffb5b5;font-size:12px;margin-top:10px}
</style></head><body><form class="card" id="f"><div class="eyebrow">PRIVATE 24/7 CONTROL</div><h1>Agent Fleet</h1><p>BlogLab · Project Visibility · Agent Manager</p><input id="p" type="password" autocomplete="current-password" placeholder="Remote control password" required><button>PRIJAVA</button><div class="err" id="e"></div></form>
<script>f.onsubmit=async e=>{e.preventDefault();const r=await fetch('/api/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({password:p.value})});const d=await r.json().catch(()=>({}));if(r.ok)location.reload();else document.getElementById('e').textContent=d.detail||'Prijava ni uspela.'}</script></body></html>"""

DASHBOARD_HTML = """<!doctype html><html lang="sl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Agent Fleet Control</title><style>
:root{font-family:Inter,system-ui;color:#eaf1f7;background:#081018}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 80% 0,#173b56 0,transparent 34rem),#081018}.wrap{width:min(1180px,calc(100% - 28px));margin:auto;padding:26px 0 70px}.top{display:flex;justify-content:space-between;gap:14px;align-items:center}.brand h1{font:700 29px Georgia,serif;margin:0}.brand p{margin:4px 0;color:#8ca2b3;font-size:12px}.grid{display:grid;grid-template-columns:1.15fr .85fr;gap:16px;margin-top:18px}.card{border:1px solid #26394a;border-radius:18px;background:#101c27;box-shadow:0 22px 60px #0005;overflow:hidden}.card h2{font-size:14px;margin:0;padding:16px 18px;border-bottom:1px solid #26394a}.body{padding:18px}select,textarea{width:100%;border:1px solid #31506a;background:#09131c;color:#fff;border-radius:11px;padding:12px}textarea{min-height:190px;resize:vertical;margin-top:10px}button{border:0;border-radius:10px;background:#7fa9d1;color:#0a1721;padding:11px 14px;font-weight:900;cursor:pointer}.ghost{background:#182b3b;color:#b8d2e5}.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.quick button{font-size:11px;padding:8px 10px}.out{white-space:pre-wrap;word-break:break-word;font:12px/1.65 ui-monospace,Consolas,monospace;color:#b9c9d5;max-height:610px;overflow:auto}.status{display:grid;gap:8px}.pill{padding:10px 12px;border:1px solid #2b4356;border-radius:11px;background:#0d1822;color:#9eb5c6;font-size:12px}.pill.ok{border-color:#275941;color:#8fe0ad}.muted{color:#7890a2}.logout{background:#1b2c39;color:#b9c9d5}@media(max-width:800px){.grid{grid-template-columns:1fr}}
</style></head><body><main class="wrap"><div class="top"><div class="brand"><h1>Agent Fleet Control</h1><p>En varen terminal za tri agente — od kjerkoli.</p></div><button class="logout" id="logout">Odjava</button></div>
<div class="grid"><section class="card"><h2>Pošlji ukaz</h2><div class="body"><select id="target"><option value="all">VSI AGENTI</option><option value="manager">Agent Manager</option><option value="project_visibility">Project Visibility</option><option value="bloglab">BlogLab</option></select>
<div class="row quick"><button data-c="status">status</button><button data-c="preglej in popravi">preglej in popravi</button><button data-c="preflight">preflight</button><button data-c="preveri agente">preveri agente</button></div>
<textarea id="command" placeholder="Npr. 'preveri status', 'preglej in popravi', ali BlogLab: 'napiši članek o ...'"></textarea><div class="row"><button id="send">IZVEDI UKAZ</button><button class="ghost" id="refresh">OSVEŽI STATUS</button></div></div></section>
<section class="card"><h2>Fleet status</h2><div class="body"><div id="status" class="status"><div class="pill">Nalagam ...</div></div></div></section>
<section class="card" style="grid-column:1/-1"><h2>Rezultat</h2><div class="body out" id="out">Pripravljen.</div></section></div></main>
<script>
const q=id=>document.getElementById(id), out=q('out');
async function js(url,opt){const r=await fetch(url,opt);const d=await r.json().catch(()=>({}));if(r.status===401){location.reload();throw new Error('Prijava je potekla.')}if(!r.ok)throw new Error(d.error||d.detail||('HTTP '+r.status));return d}
async function status(){try{const d=await js('/api/status');const entries=[['Agent Manager',d.manager],['Project Visibility',d.project_visibility],['BlogLab',d.bloglab]];q('status').innerHTML=entries.map(([n,v])=>'<div class="pill '+(v.ok?'ok':'')+'"><b>'+n+'</b><br><span class="muted">'+(v.ok?'ONLINE':'OFFLINE / '+(v.error||'napaka'))+'</span></div>').join('')+'<div class="pill"><b>Integracije</b><br><span class="muted">PV token '+(d.integrations.project_token_ready?'OK':'MANJKA')+' · BlogLab token '+(d.integrations.bloglab_token_ready?'OK':'MANJKA')+'</span></div>'}catch(e){q('status').innerHTML='<div class="pill">'+e.message+'</div>'}}
q('send').onclick=async()=>{const command=q('command').value.trim();if(!command)return;out.textContent='Izvajam ...';q('send').disabled=true;try{const d=await js('/api/command',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({target:q('target').value,command})});out.textContent=JSON.stringify(d,null,2);status()}catch(e){out.textContent='NAPAKA: '+e.message}finally{q('send').disabled=false}}
q('refresh').onclick=status;q('logout').onclick=async()=>{await fetch('/api/logout',{method:'POST'});location.reload()};document.querySelectorAll('[data-c]').forEach(b=>b.onclick=()=>q('command').value=b.dataset.c);status();setInterval(status,30000);
</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if _authorized(request):
        return HTMLResponse(DASHBOARD_HTML)
    return HTMLResponse(LOGIN_HTML)
