import json
import os
import time
import urllib.error
import urllib.request

BASE = os.environ.get("WORKER_URL", "https://blog-lab.dan-grmusa.workers.dev").rstrip("/")
EXPECTED_VERSION = os.environ.get("EXPECTED_WORKER_VERSION", "").strip()

def call(path, method="GET", payload=None, timeout=20):
    data = None
    headers = {
        "User-Agent": "BlogLabTerminalLiveContract/2.0",
        "Accept": "application/json,text/plain,text/html,*/*",
        "Cache-Control": "no-cache",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status, dict(response.headers.items()), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers.items()), body

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def health_probe():
    status, headers, body = call("/health")
    require(status == 200, f"/health returned HTTP {status}")
    data = json.loads(body)
    require(data.get("ok") is True, "health ok != true")
    require(data.get("ready") is True, f"worker not ready: {data}")
    require(data.get("auth_self_test_ok") is True, "auth self-test failed")
    require(int(data.get("authorized_users_ready") or 0) >= 2, "both operator accounts are not ready")
    require(data.get("maj_login_ready") is True, "Maj login is not ready")
    require(data.get("dan_login_ready") is True, "Dan login is not ready")
    require(data.get("publisher_scheduler_ready") is True, "publisher scheduler token is not ready")
    if EXPECTED_VERSION:
        require(data.get("version") == EXPECTED_VERSION, f"version {data.get('version')} != {EXPECTED_VERSION}")
    lower_headers = {str(k).lower(): str(v) for k, v in headers.items()}
    require("no-store" in lower_headers.get("cache-control", "").lower(), "health cache-control is not no-store")
    require(lower_headers.get("x-content-type-options", "").lower() == "nosniff", "nosniff header missing")
    require(lower_headers.get("x-frame-options", "").upper() == "DENY", "frame protection missing")
    return data

attempts = 18 if EXPECTED_VERSION else 3
last_error = None
health = None
for attempt in range(1, attempts + 1):
    try:
        health = health_probe()
        break
    except Exception as exc:
        last_error = exc
        if attempt < attempts:
            time.sleep(5 if EXPECTED_VERSION else 2)
if health is None:
    raise SystemExit(f"Live health contract failed: {last_error}")

status, _, root = call("/")
require(status == 200, f"login page returned HTTP {status}")
require("Zasebni terminal" in root and 'id="login"' in root, "login page contract missing")

protected = [
    ("POST", "/api/chat", {"message": "test"}),
    ("POST", "/api/interpret", {"command": "test"}),
    ("POST", "/api/command", {"command": "test"}),
    ("GET", "/api/me", None),
    ("GET", "/api/history", None),
]
for method, path, payload in protected:
    status, _, body = call(path, method=method, payload=payload)
    require(status == 401, f"{path} without session returned HTTP {status}, expected 401")
    require("Prijava" in body or "UNAUTHORIZED" in body, f"{path} unauthorized response contract changed")

print(json.dumps({
    "ok": True,
    "worker": health.get("worker"),
    "version": health.get("version"),
    "ready": health.get("ready"),
    "authorized_users_ready": health.get("authorized_users_ready"),
    "protected_routes_checked": len(protected),
    "security_headers": "ok",
}, ensure_ascii=False, indent=2))
