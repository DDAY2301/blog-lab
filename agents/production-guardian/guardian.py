from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parents[2]
GUARDIAN_VERSION = "guardian-v1.0-final"
PUBLIC_SITE_URL = "https://dday2301.github.io/blog-lab/"
WORKER_HEALTH_URL = "https://blog-lab.dan-grmusa.workers.dev/health"
TERMINAL_URL = "https://blog-lab.dan-grmusa.workers.dev/"

REQUIRED_FILES = (
    "package.json",
    "package-lock.json",
    "src/App.jsx",
    "public/terminal-config.json",
    "terminal/worker/src/index.js",
    "wrangler.jsonc",
    "terminal/worker/wrangler.jsonc",
    ".github/workflows/health-check.yml",
    ".github/workflows/external-smoke.yml",
    ".github/workflows/full-e2e-audit.yml",
    ".github/workflows/self-heal.yml",
    ".github/workflows/operator-terminal.yml",
    ".github/workflows/agent-blog-lab-publisher.yml",
)

RECOMMENDED_PACKAGE_SCRIPTS = {
    "guardian:check": "python agents/production-guardian/guardian.py check --report logs/guardian-report.json",
    "guardian:repair": "python agents/production-guardian/guardian.py repair",
    "test:guardian": "python -m pytest -q agents/production-guardian/tests",
}

SECRET_PATTERNS = (
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}", re.I),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}", re.I),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}", re.I),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{24,}", re.I),
)

SCAN_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".py", ".json", ".yml", ".yaml", ".css", ".html", ".md"}
SCAN_SKIP_DIRS = {".git", "node_modules", "dist", ".wrangler", ".vite"}


@dataclass
class Finding:
    id: str
    status: str
    severity: str
    message: str
    evidence: str = ""
    repair: str = ""


def redact(value: str) -> str:
    text = str(value or "")
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    text = re.sub(r"([A-Za-z0-9+/=_-]{80,})", "[REDACTED-LONG-VALUE]", text)
    return text


def read_text(rel: str) -> str:
    return (BASE / rel).read_text(encoding="utf-8", errors="replace")


def read_json(rel: str) -> dict:
    return json.loads(read_text(rel))


def write_if_changed(rel: str, content: str) -> bool:
    path = BASE / rel
    old = path.read_text(encoding="utf-8", errors="replace") if path.exists() else None
    if old == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def add_finding(findings: list[Finding], **kwargs) -> None:
    findings.append(Finding(**kwargs))


def check_required_files(findings: list[Finding]) -> None:
    missing = [rel for rel in REQUIRED_FILES if not (BASE / rel).exists()]
    if missing:
        add_finding(
            findings,
            id="required-files",
            status="fail",
            severity="critical",
            message="Manjkajo obvezne produkcijske datoteke.",
            evidence=", ".join(missing),
            repair="Obnovi manjkajoče datoteke ali zaženi guardian repair.",
        )
    else:
        add_finding(
            findings,
            id="required-files",
            status="pass",
            severity="info",
            message="Vse obvezne produkcijske datoteke so prisotne.",
        )


def desired_package_json(current: dict) -> tuple[str, bool]:
    next_value = json.loads(json.dumps(current))
    scripts = dict(next_value.get("scripts") or {})
    changed = False
    for name, command in RECOMMENDED_PACKAGE_SCRIPTS.items():
        if scripts.get(name) != command:
            scripts[name] = command
            changed = True
    if changed:
        next_value["scripts"] = scripts
    text = json.dumps(next_value, ensure_ascii=False, indent=2) + "\n"
    return text, changed


def check_package_scripts(findings: list[Finding]) -> None:
    try:
        package = read_json("package.json")
    except Exception as exc:
        add_finding(
            findings,
            id="package-json",
            status="fail",
            severity="critical",
            message="package.json ni veljaven JSON.",
            evidence=str(exc),
            repair="Popravi JSON sintakso v package.json.",
        )
        return
    scripts = package.get("scripts") or {}
    missing = [name for name in ("dev", "build", "preview") if name not in scripts]
    missing += [name for name in RECOMMENDED_PACKAGE_SCRIPTS if name not in scripts]
    if missing:
        add_finding(
            findings,
            id="package-scripts",
            status="warn",
            severity="medium",
            message="Manjkajo priporočeni produkcijski/guardian npm skripti.",
            evidence=", ".join(missing),
            repair="Zaženi guardian repair, ki varno doda manjkajoče skripte.",
        )
    else:
        add_finding(
            findings,
            id="package-scripts",
            status="pass",
            severity="info",
            message="package.json vsebuje build/dev/preview in guardian skripte.",
        )


def check_terminal_config(findings: list[Finding]) -> None:
    try:
        cfg = read_json("public/terminal-config.json")
    except Exception as exc:
        add_finding(
            findings,
            id="terminal-config",
            status="fail",
            severity="critical",
            message="public/terminal-config.json ni berljiv.",
            evidence=str(exc),
            repair="Obnovi terminal-config.json z veljavnim terminalUrl.",
        )
        return
    terminal_url = str(cfg.get("terminalUrl") or "")
    app = read_text("src/App.jsx") if (BASE / "src/App.jsx").exists() else ""
    if terminal_url.rstrip("/") != TERMINAL_URL.rstrip("/"):
        add_finding(
            findings,
            id="terminal-config",
            status="fail",
            severity="high",
            message="Terminal URL v public konfiguraciji ne kaže na produkcijski Worker.",
            evidence=terminal_url,
            repair="Zaženi guardian repair ali nastavi terminalUrl na produkcijski Worker URL.",
        )
    elif TERMINAL_URL not in app:
        add_finding(
            findings,
            id="terminal-config",
            status="warn",
            severity="medium",
            message="Produkcijski terminal URL ni jasno najden v src/App.jsx.",
            evidence="TERMINAL_URL konstanta ni usklajena ali se je struktura App.jsx spremenila.",
            repair="Preveri povezavo javnega gumba za prijavo.",
        )
    else:
        add_finding(
            findings,
            id="terminal-config",
            status="pass",
            severity="info",
            message="Javna stran in terminal config kažeta na isti produkcijski Worker.",
        )


def check_worker_source(findings: list[Finding]) -> None:
    rel = "terminal/worker/src/index.js"
    if not (BASE / rel).exists():
        add_finding(findings, id="worker-source", status="fail", severity="critical", message="Worker source manjka.")
        return
    source = read_text(rel)
    required_markers = [
        "sharedLoginPassword",
        "loginPasswordCandidates",
        "passwordMatchesLogin",
        "auth_self_test_ok",
        "SESSION_COOKIE",
        "Secure; SameSite=",
        "/api/interpret",
    ]
    missing = [marker for marker in required_markers if marker not in source]
    version = re.search(r'version:\s*"([^"]+)"', source)
    if missing:
        add_finding(
            findings,
            id="worker-source",
            status="fail",
            severity="critical",
            message="Worker nima vseh produkcijskih auth/terminal markerjev.",
            evidence=", ".join(missing),
            repair="Obnovi zadnjo cross-browser login in command-understanding implementacijo.",
        )
    else:
        add_finding(
            findings,
            id="worker-source",
            status="pass",
            severity="info",
            message="Worker vsebuje cross-browser login, auth self-test in command interpretacijo.",
            evidence=version.group(1) if version else "version marker missing",
        )


def check_workflows(findings: list[Finding]) -> None:
    workflow_checks = {
        ".github/workflows/self-heal.yml": ["Run autonomous repair engine", "Reject protected-path changes", "Reject credential-like changes"],
        ".github/workflows/health-check.yml": ["Test Worker auth on a fresh device", "Bundle Cloudflare Worker", "Scan tracked files"],
        ".github/workflows/full-e2e-audit.yml": ["E2E", "audit"],
        ".github/workflows/external-smoke.yml": ["smoke"],
    }
    missing: list[str] = []
    for rel, markers in workflow_checks.items():
        path = BASE / rel
        if not path.exists():
            missing.append(rel)
            continue
        content = read_text(rel).lower()
        for marker in markers:
            if marker.lower() not in content:
                missing.append(f"{rel}:{marker}")
    if missing:
        add_finding(
            findings,
            id="workflow-guards",
            status="fail",
            severity="high",
            message="Nekateri produkcijski workflow guardi manjkajo.",
            evidence=", ".join(missing),
            repair="Dopolni workflowe z health, self-heal in security gate koraki.",
        )
    else:
        add_finding(
            findings,
            id="workflow-guards",
            status="pass",
            severity="info",
            message="Health, smoke, E2E in self-heal workflow guardi so prisotni.",
        )


def iter_scannable_files() -> list[Path]:
    out: list[Path] = []
    for path in BASE.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.relative_to(BASE).parts)
        if parts & SCAN_SKIP_DIRS:
            continue
        if path.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        out.append(path)
    return out


def check_secret_scan(findings: list[Finding]) -> None:
    hits: list[str] = []
    for path in iter_scannable_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = path.relative_to(BASE).as_posix()
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                hits.append(rel)
                break
    if hits:
        add_finding(
            findings,
            id="secret-scan",
            status="fail",
            severity="critical",
            message="Najden je credential-like tekst v sledljivih datotekah.",
            evidence=", ".join(sorted(set(hits))[:20]),
            repair="Odstrani skrivnosti iz repozitorija in jih prestavi v GitHub/Cloudflare secrets.",
        )
    else:
        add_finding(
            findings,
            id="secret-scan",
            status="pass",
            severity="info",
            message="Osnovni scan ni našel očitnih ključev ali tokenov.",
        )


def http_get(url: str, *, timeout: int = 15) -> tuple[int, str, str]:
    req = Request(url, headers={"User-Agent": f"BlogLabProductionGuardian/{GUARDIAN_VERSION}"})
    try:
        with urlopen(req, timeout=timeout) as response:
            body = response.read(120000).decode("utf-8", errors="replace")
            return int(response.status), body, ""
    except HTTPError as exc:
        body = exc.read(4000).decode("utf-8", errors="replace") if exc.fp else ""
        return int(exc.code), body, str(exc)
    except (URLError, TimeoutError, OSError) as exc:
        return 0, "", str(exc)


def check_remote_health(findings: list[Finding], *, strict_remote: bool = False) -> None:
    public_status, public_body, public_error = http_get(PUBLIC_SITE_URL)
    if public_status != 200 or "Blog Lab" not in public_body:
        add_finding(
            findings,
            id="public-site-live",
            status="fail" if strict_remote else "warn",
            severity="high" if strict_remote else "medium",
            message="Javna stran ni dosegljiva ali ne renderira Blog Lab markerja.",
            evidence=redact(f"status={public_status} error={public_error}"),
            repair="Preveri GitHub Pages deploy-pages workflow in Vite build.",
        )
    else:
        add_finding(findings, id="public-site-live", status="pass", severity="info", message="Javna stran je dosegljiva.")

    worker_status, worker_body, worker_error = http_get(WORKER_HEALTH_URL)
    if worker_status != 200:
        add_finding(
            findings,
            id="worker-live",
            status="fail" if strict_remote else "warn",
            severity="high" if strict_remote else "medium",
            message="Worker /health ni dosegljiv.",
            evidence=redact(f"status={worker_status} error={worker_error}"),
            repair="Zaženi wrangler deploy oziroma preveri Cloudflare secrets in deploy nastavitev.",
        )
        return
    try:
        health = json.loads(worker_body)
    except json.JSONDecodeError as exc:
        add_finding(
            findings,
            id="worker-live",
            status="fail" if strict_remote else "warn",
            severity="high" if strict_remote else "medium",
            message="Worker /health ne vrača veljavnega JSON.",
            evidence=str(exc),
            repair="Preveri Worker health endpoint.",
        )
        return
    source = read_text("terminal/worker/src/index.js") if (BASE / "terminal/worker/src/index.js").exists() else ""
    match = re.search(r'version:\s*"([^"]+)"', source)
    expected_version = match.group(1) if match else ""
    actual_version = str(health.get("version") or "")
    problems = []
    if health.get("ready") is not True:
        problems.append("ready=false")
    if expected_version and actual_version != expected_version:
        problems.append(f"version drift source={expected_version} live={actual_version}")
    if health.get("auth_self_test_ok") is not True:
        problems.append("auth_self_test_ok=false")
    if int(health.get("authorized_users_ready") or 0) < 1:
        problems.append("authorized_users_ready<1")
    if problems:
        add_finding(
            findings,
            id="worker-live",
            status="fail" if strict_remote else "warn",
            severity="high" if strict_remote else "medium",
            message="Worker je dosegljiv, vendar ni popolnoma produkcijsko usklajen.",
            evidence="; ".join(problems),
            repair="Redeploy Worker in preveri LOGIN_PASSWORD/DAN_LOGIN_PASSWORD/MAJ_LOGIN_PASSWORD ter TERMINAL_COMMAND_KEY.",
        )
    else:
        add_finding(
            findings,
            id="worker-live",
            status="pass",
            severity="info",
            message="Worker /health je dosegljiv, pripravljen in auth self-test uspe.",
            evidence=actual_version,
        )


def build_report(*, strict_remote: bool = False, skip_remote: bool = False) -> dict:
    findings: list[Finding] = []
    check_required_files(findings)
    check_package_scripts(findings)
    check_terminal_config(findings)
    check_worker_source(findings)
    check_workflows(findings)
    check_secret_scan(findings)
    if skip_remote or os.environ.get("GUARDIAN_SKIP_REMOTE") == "1":
        add_finding(findings, id="remote-health", status="skip", severity="info", message="Remote health checks skipped.")
    else:
        check_remote_health(findings, strict_remote=strict_remote)

    status_order = {"fail": 3, "warn": 2, "skip": 1, "pass": 0}
    worst = max((status_order.get(item.status, 0) for item in findings), default=0)
    overall = "fail" if worst >= 3 else "warn" if worst == 2 else "pass"
    return {
        "name": "Blog Lab Production Guardian",
        "version": GUARDIAN_VERSION,
        "checkedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "overall": overall,
        "counts": {
            "pass": sum(1 for x in findings if x.status == "pass"),
            "warn": sum(1 for x in findings if x.status == "warn"),
            "fail": sum(1 for x in findings if x.status == "fail"),
            "skip": sum(1 for x in findings if x.status == "skip"),
        },
        "findings": [asdict(item) for item in findings],
    }


def manifest_json() -> str:
    manifest = {
        "name": "Blog Lab Production Guardian",
        "version": GUARDIAN_VERSION,
        "mode": "safe-autoupdate",
        "principle": "Detect problems automatically, repair only through validated tests and pull requests unless a human enables direct deployment credentials.",
        "production": {
            "publicSite": PUBLIC_SITE_URL,
            "privateTerminal": TERMINAL_URL,
            "workerHealth": WORKER_HEALTH_URL,
        },
        "capabilities": [
            "repository structure checks",
            "public site smoke check",
            "Cloudflare Worker health/version drift detection",
            "cross-browser login readiness check",
            "terminal command-understanding readiness check",
            "credential-like text scan",
            "deterministic repo hygiene repair",
            "AI-assisted self-heal with protected-path and secret gates",
            "validated pull-request based auto-update",
            "manual workflow_dispatch emergency check",
        ],
        "protectedPaths": [
            ".github/",
            "agents/operator-terminal/",
            "agents/self-heal/",
            "AGENTS.md",
            "requirements-agent.txt",
            ".env*",
        ],
        "workflows": [
            "Blog Lab Health Check",
            "Blog Lab External Smoke Test",
            "Blog Lab Full E2E Audit",
            "Blog Lab Self Heal",
            "Blog Lab Production Guardian",
        ],
    }
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def repair_repo() -> dict:
    changed: list[str] = []

    if (BASE / "package.json").exists():
        package = read_json("package.json")
        new_package, package_changed = desired_package_json(package)
        if package_changed and write_if_changed("package.json", new_package):
            changed.append("package.json")

    if write_if_changed("public/guardian-manifest.json", manifest_json()):
        changed.append("public/guardian-manifest.json")

    if write_if_changed("logs/.gitkeep", "# Guardian runtime reports are generated by CI and kept out of source control.\n"):
        changed.append("logs/.gitkeep")

    return {"changed": changed, "changedCount": len(changed)}


def markdown_report(report: dict) -> str:
    lines = [
        "# Blog Lab Production Guardian Report",
        "",
        f"- Version: `{report['version']}`",
        f"- Checked: `{report['checkedAt']}`",
        f"- Overall: **{report['overall'].upper()}**",
        f"- Counts: pass={report['counts']['pass']}, warn={report['counts']['warn']}, fail={report['counts']['fail']}, skip={report['counts']['skip']}",
        "",
        "| Check | Status | Severity | Message | Evidence |",
        "|---|---:|---:|---|---|",
    ]
    for item in report["findings"]:
        evidence = str(item.get("evidence") or "").replace("|", "\\|")[:500]
        lines.append(
            f"| `{item['id']}` | {item['status']} | {item['severity']} | {item['message'].replace('|', '\\|')} | {evidence} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Blog Lab production guardian")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check")
    check.add_argument("--report")
    check.add_argument("--markdown")
    check.add_argument("--strict-remote", action="store_true")
    check.add_argument("--skip-remote", action="store_true")
    check.add_argument("--fail-on-warning", action="store_true")

    repair = sub.add_parser("repair")
    repair.add_argument("--json", action="store_true")

    manifest = sub.add_parser("manifest")
    manifest.add_argument("--write", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "repair":
        result = repair_repo()
        output = json.dumps(result, ensure_ascii=False, indent=2)
        print(output if args.json else f"Production guardian repair: {output}")
        return 0

    if args.command == "manifest":
        content = manifest_json()
        if args.write:
            changed = write_if_changed("public/guardian-manifest.json", content)
            print(json.dumps({"changed": changed}, ensure_ascii=False))
        else:
            print(content, end="")
        return 0

    report = build_report(strict_remote=args.strict_remote, skip_remote=args.skip_remote)
    report_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(report_text)
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding="utf-8")
    if args.markdown:
        md_path = Path(args.markdown)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(markdown_report(report), encoding="utf-8")
    if report["overall"] == "fail":
        return 1
    if args.fail_on_warning and report["overall"] == "warn":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
