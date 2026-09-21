import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
worker = root / "terminal" / "worker" / "src" / "index.js"
text = worker.read_text(encoding="utf-8")

required_markers = [
    'url.pathname === "/api/chat"',
    'url.pathname === "/api/command"',
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
]

missing = [marker for marker in required_markers if marker not in text]
if missing:
    raise SystemExit("Missing terminal hardening markers: " + ", ".join(missing))

suite_path = root / "data" / "terminal-command-test-suite.json"
suite = json.loads(suite_path.read_text(encoding="utf-8"))
commands = suite.get("commands") or []
if len(commands) < 6:
    raise SystemExit("Terminal command suite is too small")

expected = {item.get("expected_path") for item in commands}
for path in ["operational_publication_check", "operational_terminal_diagnostics", "operational_domain_dns", "github_workflow_dispatch"]:
    if path not in expected:
        raise SystemExit(f"Missing command suite path: {path}")

bad = [item for item in commands if not item.get("text") or len(item.get("text", "")) < 12]
if bad:
    raise SystemExit("Invalid short command cases: " + ", ".join(item.get("name", "?") for item in bad))

# Prevent old one-shot repair workflows from coming back and making every push red.
obsolete = root / ".github" / "workflows" / "one-shot-terminal-operational-chat.yml"
if obsolete.exists():
    raise SystemExit("Obsolete one-shot terminal workflow still exists")

print(json.dumps({
    "ok": True,
    "checked_markers": len(required_markers),
    "command_cases": len(commands),
    "suite_version": suite.get("version")
}, ensure_ascii=False, indent=2))
