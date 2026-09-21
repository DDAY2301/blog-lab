import json
import os
import time
import urllib.error
import urllib.request
import urllib.parse

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

status, root_headers, root = call("/")
require(status == 200, f"login page returned HTTP {status}")
require("Zasebni terminal" in root and 'id="login"' in root, "login page contract missing")
root_lower_headers = {str(k).lower(): str(v) for k, v in root_headers.items()}
require("frame-ancestors 'none'" in root_lower_headers.get("content-security-policy", ""), "login page CSP frame-ancestors missing")
require(root_lower_headers.get("x-frame-options", "").upper() == "DENY", "login page X-Frame-Options missing")

login_diagnostics_checked = 0
for email in ("dan.grmusa@gmail.com", "maj@klemenc.org"):
    status, _, body = call("/api/login-diagnostics?email=" + urllib.parse.quote(email))
    require(status == 200, f"login diagnostics for {email} returned HTTP {status}")
    data = json.loads(body)
    require(data.get("email_known") is True, f"{email} missing from authorized login diagnostics")
    require(data.get("user_secret_configured") is True, f"{email} secret is not configured")
    require(data.get("hint") == "EMAIL_CONFIGURED", f"{email} login diagnostics hint changed")
    login_diagnostics_checked += 1

status, headers, body = call("/api/login", method="POST", payload={
    "email": "dan.grmusa@gmail.com",
    "password": "__bloglab_invalid_test_password__"
})
require(status == 401, f"invalid password returned HTTP {status}, expected 401")
require("set-cookie" not in {str(k).lower() for k in headers}, "invalid login unexpectedly created a session cookie")

protected = [
    ("GET", "/api/commands", None),
    ("POST", "/api/chat", {"message": "test"}),
    ("POST", "/api/interpret", {"command": "test"}),
    ("POST", "/api/command", {"command": "test"}),
    ("GET", "/api/me", None),
    ("GET", "/api/history", None),
]

internal_protected = [
    ("POST", "/api/scheduler/catch-up", None),
    ("GET", "/api/ai/diagnostics", None),
    ("POST", "/api/ai/write", {"system_prompt": "x", "task_prompt": "x", "source_items": [{"x": 1}]}),
    ("POST", "/api/ai/review", {"system_prompt": "x", "user_prompt": "x"}),
    ("POST", "/api/ai/edit", {"system_prompt": "x", "request": "x", "context": [{"x": 1}]}),
    ("POST", "/api/ai/repair", {"system_prompt": "x", "request": "x", "context": [{"x": 1}]}),
]
for method, path, payload in protected:
    status, _, body = call(path, method=method, payload=payload)
    require(status == 401, f"{path} without session returned HTTP {status}, expected 401")
    require("Prijava" in body or "UNAUTHORIZED" in body, f"{path} unauthorized response contract changed")

for method, path, payload in internal_protected:
    status, _, body = call(path, method=method, payload=payload)
    require(status == 401, f"{path} without bearer token returned HTTP {status}, expected 401")
    require("UNAUTHORIZED" in body.upper() or "Nepooblaščen" in body, f"{path} internal authorization response contract changed")

print(json.dumps({
    "ok": True,
    "worker": health.get("worker"),
    "version": health.get("version"),
    "ready": health.get("ready"),
    "authorized_users_ready": health.get("authorized_users_ready"),
    "protected_routes_checked": len(protected),
    "internal_protected_routes_checked": len(internal_protected),
    "login_diagnostics_checked": login_diagnostics_checked,
    "invalid_login_rejected": True,
    "security_headers": "ok",
}, ensure_ascii=False, indent=2))
