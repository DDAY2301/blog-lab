import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
worker = root / "terminal" / "worker" / "src" / "index.js"
text = worker.read_text(encoding="utf-8")

required_markers = [
    'url.pathname === "/api/chat"',
    'url.pathname === "/api/command"',
    'url.pathname === "/api/interpret"',
    'terminalChatAssistant',
    'terminalOperationalAnswer',
    'operational_publication_check',
    'operational_terminal_diagnostics',
    'operational_domain_dns',
    'terminal_chat_ai_timeout',
    'dispatchPublisherCatchup',
    'GITHUB_WORKFLOW_DISPATCH_FAILED',
    'GitHub odgovor:',
    'readAgentSnapshot',
    'recentRuns',
    'SESSION_TTL_SECONDS',
    'HttpOnly; Secure; SameSite=Lax',
    '"cache-control": "no-store"',
    'content-security-policy',
    'internalWriterAuthorized',
    'TERMINAL_COMMAND_KEY',
    'GITHUB_DISPATCH_TOKEN',
]

missing = [marker for marker in required_markers if marker not in text]
if missing:
    raise SystemExit("Missing terminal hardening markers: " + ", ".join(missing))

suite_path = root / "data" / "terminal-command-test-suite.json"
suite = json.loads(suite_path.read_text(encoding="utf-8"))
commands = suite.get("commands") or []
if len(commands) < 25:
    raise SystemExit("Terminal command suite is too small; expected at least 25 behavioral cases")

allowed_paths = {
    "operational_publication_check",
    "operational_terminal_diagnostics",
    "operational_domain_dns",
    "local_agent_status",
    "github_workflow_dispatch",
}
allowed_modes = {"article", "site", "control"}
names = set()
for item in commands:
    name = item.get("name")
    if not name or name in names:
        raise SystemExit(f"Duplicate or missing command test name: {name!r}")
    names.add(name)
    if item.get("expected_path") not in allowed_paths:
        raise SystemExit(f"Unknown expected_path for {name}: {item.get('expected_path')}")
    if item.get("expected_mode") and item["expected_mode"] not in allowed_modes:
        raise SystemExit(f"Unknown expected_mode for {name}: {item['expected_mode']}")
    if not item.get("text") or len(item.get("text", "")) < 8:
        raise SystemExit(f"Invalid short command case: {name}")

expected = {item.get("expected_path") for item in commands}
for path in allowed_paths:
    if path not in expected:
        raise SystemExit(f"Missing command suite path: {path}")

# Security invariants: only the two intended operators are present in the allowlist.
authorized_block = re.search(r"const AUTHORIZED_USERS = Object\.freeze\(\{(.*?)\}\);", text, re.S)
if not authorized_block:
    raise SystemExit("AUTHORIZED_USERS block not found")
emails = set(re.findall(r'"([^"]+@[^"]+)"\s*:', authorized_block.group(1)))
expected_emails = {"dan.grmusa@gmail.com", "maj@klemenc.org"}
if emails != expected_emails:
    raise SystemExit(f"Authorized-user allowlist drifted: {sorted(emails)}")

# Internal AI/scheduler endpoints must remain bearer-protected.
for route in ["/api/scheduler/catch-up", "/api/ai/diagnostics", "/api/ai/write", "/api/ai/review", "/api/ai/edit", "/api/ai/repair"]:
    pos = text.find(f'url.pathname === "{route}"')
    if pos < 0:
        raise SystemExit(f"Protected route missing: {route}")
    window = text[pos:pos + 700]
    if "internalWriterAuthorized" not in window:
        raise SystemExit(f"Internal route lost bearer authorization: {route}")

# Public write/command APIs remain behind the authenticated-user gate.
gate = 'if (!user) return json({ error: "Prijava je potrebna." }, 401);'
gate_pos = text.find(gate)
if gate_pos < 0:
    raise SystemExit("Authenticated-user gate missing")
for route in ["/api/interpret", "/api/chat", "/api/media", "/api/status", "/api/history", "/api/command"]:
    route_pos = text.find(f'url.pathname === "{route}"')
    if route_pos < gate_pos:
        raise SystemExit(f"Authenticated route appears before auth gate: {route}")

# Prevent old one-shot repair workflows from returning and creating push loops.
obsolete = root / ".github" / "workflows" / "one-shot-terminal-operational-chat.yml"
if obsolete.exists():
    raise SystemExit("Obsolete one-shot terminal workflow still exists")

operator = (root / ".github" / "workflows" / "operator-terminal.yml").read_text(encoding="utf-8")
for marker in [
    "Reject edits to protected security paths",
    "Ensure no obvious credentials were written",
    "bounded recovery",
    "Destroy decrypted command",
]:
    if marker not in operator:
        raise SystemExit(f"Operator workflow safety marker missing: {marker}")

print(json.dumps({
    "ok": True,
    "checked_markers": len(required_markers),
    "command_cases": len(commands),
    "suite_version": suite.get("version"),
    "authorized_users": sorted(emails),
    "protected_internal_routes": 6,
    "authenticated_terminal_routes": 6,
}, ensure_ascii=False, indent=2))
