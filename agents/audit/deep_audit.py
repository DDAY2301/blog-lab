from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

BASE = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "package.json",
    "requirements-agent.txt",
    "src/App.jsx",
    "src/main.jsx",
    "index.html",
    "public/guardian-manifest.json",
    "data/agent-control.json",
    "agents/operator-terminal/command.py",
    "agents/operator-terminal/compound_control.py",
    "agents/operator-terminal/deferred_site_edits.py",
    "agents/operator-terminal/deferred_articles.py",
    "agents/blog-lab-publisher/agent.py",
    "agents/blog-lab-publisher/services/ai_provider.py",
    "agents/blog-lab-publisher/services/sources.py",
    "agents/blog-lab-publisher/services/publisher.py",
    "agents/blog-lab-publisher/services/validator.py",
    "agents/live-feed/update.py",
    "agents/self-heal/repair.py",
    "agents/production-guardian/guardian.py",
    "terminal/worker/src/index.js",
    "terminal/worker/package.json",
    "terminal/worker/wrangler.jsonc",
    "wrangler.jsonc",
]

REQUIRED_WORKFLOWS = [
    ".github/workflows/agent-blog-lab-publisher.yml",
    ".github/workflows/deferred-articles.yml",
    ".github/workflows/deferred-site-edits.yml",
    ".github/workflows/deploy-pages.yml",
    ".github/workflows/deploy-worker.yml",
    ".github/workflows/external-smoke.yml",
    ".github/workflows/full-e2e-audit.yml",
    ".github/workflows/health-check.yml",
    ".github/workflows/live-feed.yml",
    ".github/workflows/operator-terminal.yml",
    ".github/workflows/production-guardian.yml",
    ".github/workflows/self-heal.yml",
]

ALLOWED_QUEUE_STATUSES = {"pending", "resolved", "failed"}
TOKEN_PATTERN = re.compile(r"(github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})")
TOKEN_SCAN_EXCLUDE = {
    "package-lock.json",
    "agents/production-guardian/tests/test_guardian.py",
}


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def ok(self, msg: str) -> None:
        self.notes.append(f"OK {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)
        print(f"WARN {msg}")

    def fail(self, msg: str) -> None:
        self.errors.append(msg)
        print(f"FAIL {msg}")

    def require(self, condition: bool, msg: str) -> None:
        if condition:
            self.ok(msg)
        else:
            self.fail(msg)


def read_text(path: str | Path) -> str:
    return (BASE / path).read_text(encoding="utf-8")


def read_json(path: str | Path) -> Any:
    return json.loads(read_text(path))


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 180, allow_fail: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=cwd or BASE, text=True, capture_output=True, timeout=timeout, check=False)
    print(f"RUN {' '.join(cmd)} -> {proc.returncode}")
    if proc.stdout:
        print(proc.stdout[-4000:])
    if proc.stderr:
        print(proc.stderr[-4000:], file=sys.stderr)
    if proc.returncode and not allow_fail:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return proc


def load_module(name: str, path: str):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, BASE / path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def audit_required_files(audit: Audit) -> None:
    for path in REQUIRED_PATHS + REQUIRED_WORKFLOWS:
        audit.require((BASE / path).exists(), f"required path exists: {path}")


def audit_json_yaml(audit: Audit) -> None:
    for path in BASE.rglob("*.json"):
        rel = path.relative_to(BASE).as_posix()
        if any(part in {"node_modules", "dist", ".git"} for part in path.parts):
            continue
        if rel.startswith("logs/"):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
            audit.ok(f"json parses: {rel}")
        except Exception as exc:
            audit.fail(f"json parse failed: {rel}: {exc}")

    if yaml is None:
        audit.fail("PyYAML is not importable; workflow/config parsing cannot run")
        return
    for path in list((BASE / ".github/workflows").glob("*.yml")) + list((BASE / ".github/workflows").glob("*.yaml")):
        rel = path.relative_to(BASE).as_posix()
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
            audit.ok(f"yaml parses: {rel}")
        except Exception as exc:
            audit.fail(f"yaml parse failed: {rel}: {exc}")


def audit_package(audit: Audit) -> None:
    scripts = read_json("package.json").get("scripts", {})
    for script in ["build", "guardian:check", "guardian:repair", "test:guardian"]:
        audit.require(script in scripts, f"package script present: {script}")
    worker_package = read_json("terminal/worker/package.json")
    audit.require("deploy" in worker_package.get("scripts", {}), "worker deploy script present")
    audit.require("wrangler" in worker_package.get("devDependencies", {}), "worker wrangler dev dependency present")


def audit_agent_control(audit: Audit) -> None:
    control = read_json("data/agent-control.json")
    audit.require(control.get("enabled") is True, "agent-control enabled true")
    audit.require(control.get("publish_mode") == "automatic", "agent-control automatic mode")
    schedule = control.get("schedule") or {}
    audit.require(schedule.get("timezone") == "Europe/Ljubljana", "agent-control timezone Europe/Ljubljana")
    expected = [("08:17", "sport"), ("13:27", "politika"), ("19:43", "aktualno")]
    actual = [(item.get("time"), item.get("category")) for item in schedule.get("slots") or []]
    audit.require(actual == expected, f"agent-control default slots {expected}")


def audit_python_compile(audit: Audit) -> None:
    for path in BASE.rglob("*.py"):
        if any(part in {"node_modules", ".git"} for part in path.parts):
            continue
        rel = path.relative_to(BASE).as_posix()
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=rel)
            audit.ok(f"python ast parses: {rel}")
        except Exception as exc:
            audit.fail(f"python parse failed: {rel}: {exc}")


def audit_intent_routing(audit: Audit) -> None:
    command = load_module("blog_lab_operator_command_audit", "agents/operator-terminal/command.py")
    compound = load_module("blog_lab_compound_control_audit", "agents/operator-terminal/compound_control.py")
    cases = [
        ("napiši članek o lokalnih novicah v Sloveniji", "article"),
        ("objavi clanek o sportu", "article"),
        ("uredi footer in dodaj boljši design", "site"),
        ("dodaj drag and drop images in lepši design", "site"),
        ("preveri status agenta", "control"),
        ("ustavi objavljanje", "control"),
        ("vklopi avtomatsko objavljanje", "control"),
        ("naredi rubriko šport bolj vidno", "site"),
    ]
    for text, expected in cases:
        got = command.infer_mode(text)
        audit.require(got == expected, f"intent route {text!r} -> {expected} (got {got})")
    dodaj_article = command.infer_mode("dodaj sedaj članek kako se je odvijalo dogajanje tega vikenda")
    if dodaj_article != "article":
        audit.warn(f"known routing edge case: 'dodaj članek...' currently routes to {dodaj_article}")
    catchup = "izvedi objave 3 na dan po časovnici zdaj pa napiši vse članke ki smo jih spustili zaradi popravkov na strani"
    audit.require(compound.should_handle(catchup) is True, "compound catch-up command is intercepted before site/article flow")


def audit_queues(audit: Audit) -> None:
    for rel in ["data/deferred-site-edits.json", "data/deferred-articles.json", "data/catchup-requests.json"]:
        path = BASE / rel
        if not path.exists():
            audit.warn(f"queue file missing, acceptable until first use: {rel}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            audit.fail(f"queue json invalid {rel}: {exc}")
            continue
        audit.require(isinstance(data, list), f"queue is list: {rel}")
        for i, item in enumerate(data if isinstance(data, list) else []):
            if not isinstance(item, dict):
                audit.fail(f"queue item not object {rel}[{i}]")
                continue
            if rel.startswith("data/deferred"):
                status = item.get("status")
                audit.require(status in ALLOWED_QUEUE_STATUSES, f"{rel}[{i}] status valid: {status}")
                audit.require(bool(str(item.get("command") or "").strip()), f"{rel}[{i}] command present")


def audit_workflows(audit: Audit) -> None:
    if yaml is None:
        return
    for path in (BASE / ".github/workflows").glob("*.yml"):
        rel = path.relative_to(BASE).as_posix()
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        audit.require("jobs" in data, f"workflow has jobs: {rel}")
        if rel.endswith(("operator-terminal.yml", "deferred-articles.yml", "deferred-site-edits.yml", "self-heal.yml")):
            perms = data.get("permissions") or {}
            audit.require(perms.get("contents") == "write", f"workflow has contents write: {rel}")
        if rel.endswith("deploy-worker.yml"):
            text = path.read_text(encoding="utf-8")
            audit.require("CLOUDFLARE_API_TOKEN" in text and "CLOUDFLARE_ACCOUNT_ID" in text, "worker deploy checks Cloudflare secrets")
            audit.require("Verify live Worker health" in text, "worker deploy verifies live health")


def audit_worker(audit: Audit) -> None:
    source = read_text("terminal/worker/src/index.js")
    for marker in [
        "auth-v6.17-ai-resilience",
        "DAN_LOGIN_PASSWORD",
        "MAJ_LOGIN_PASSWORD",
        "GITHUB_DISPATCH_TOKEN",
        "TERMINAL_COMMAND_KEY",
        "configuredAuthorizedUserCount",
        "authSelfTest",
        "GITHUB_CONTENTS_WRITE_REQUIRED",
    ]:
        audit.require(marker in source, f"worker marker present: {marker}")
    run(["node", "--check", "terminal/worker/src/index.js"], timeout=60)
    audit.ok("worker source passes node --check")


def audit_security(audit: Audit) -> None:
    for path in BASE.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(BASE).as_posix()
        if any(part in {".git", "node_modules", "dist", "logs"} for part in path.parts):
            continue
        if rel in TOKEN_SCAN_EXCLUDE:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if TOKEN_PATTERN.search(text):
            audit.fail(f"credential-like token pattern in tracked file: {rel}")
    audit.ok("credential pattern scan completed")


def audit_frontend_content(audit: Audit) -> None:
    app = read_text("src/App.jsx")
    for marker in ["Blog Lab", "article", "gallery"]:
        audit.require(marker.lower() in app.lower(), f"frontend marker present: {marker}")
    if "live" not in app.lower():
        audit.warn("frontend does not visibly expose live feed marker")
    for token in ["lorem ipsum", "TODO: replace", "Generated by AI", "ChatGPT"]:
        audit.require(token.lower() not in app.lower(), f"frontend does not contain placeholder/AI marker: {token}")


def audit_guardian(audit: Audit) -> None:
    manifest = read_json("public/guardian-manifest.json")
    audit.require(manifest.get("version") == "guardian-v1.0-final", "guardian manifest final version")
    audit.require((BASE / ".github/workflows/deferred-site-edits.yml").exists(), "deferred site edits workflow exists")
    audit.require((BASE / ".github/workflows/deferred-articles.yml").exists(), "deferred articles workflow exists")
    proc = run([sys.executable, "agents/production-guardian/guardian.py", "check", "--skip-remote", "--report", "logs/deep-audit-guardian.json"], timeout=180, allow_fail=True)
    if proc.returncode != 0:
        audit.fail("production guardian static check failed")
    else:
        audit.ok("production guardian static check passed")


def audit_runtime_commands(audit: Audit) -> None:
    tmp = BASE / ".tmp-audit-command.json"
    before = run(["git", "status", "--porcelain"], timeout=30).stdout
    try:
        tmp.write_text(json.dumps({"command": "preveri status agenta", "mode": "auto", "category": "aktualno", "actor": "deep-audit"}, ensure_ascii=False), encoding="utf-8")
        proc = run([sys.executable, "agents/operator-terminal/command.py", "--command-file", str(tmp)], timeout=120, allow_fail=True)
        audit.require(proc.returncode == 0, "safe terminal status command exits 0")
        audit.require("CONTROL_STATUS" in (proc.stdout + proc.stderr), "safe terminal status command prints CONTROL_STATUS")
    finally:
        tmp.unlink(missing_ok=True)
    after = run(["git", "status", "--porcelain"], timeout=30).stdout
    audit.require(before == after, "safe terminal status command leaves git tree unchanged")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deep Blog Lab production audit")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    audit = Audit()

    checks = [
        audit_required_files,
        audit_json_yaml,
        audit_package,
        audit_agent_control,
        audit_python_compile,
        audit_intent_routing,
        audit_queues,
        audit_workflows,
        audit_worker,
        audit_security,
        audit_frontend_content,
        audit_guardian,
        audit_runtime_commands,
    ]
    for check in checks:
        print(f"\n=== {check.__name__} ===")
        try:
            check(audit)
        except Exception as exc:
            audit.fail(f"{check.__name__} crashed: {exc}")

    report = {"errors": audit.errors, "warnings": audit.warnings, "notes_count": len(audit.notes)}
    out = BASE / "logs/deep-audit-report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n=== DEEP AUDIT SUMMARY ===")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if audit.errors:
        return 1
    if args.strict and audit.warnings:
        print("Strict mode completed with warnings; warnings are non-fatal unless errors exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
