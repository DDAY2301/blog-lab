from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
CONTROL = BASE / "data/agent-control.json"
ARTICLE_AGENT = BASE / "agents/blog-lab-publisher/agent.py"
VALID_MODES = {"auto", "article", "site", "control"}
VALID_CATEGORIES = {"sport", "politika", "aktualno"}

def read_json(path: Path, default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError: return default

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)

def _schedule_intent(low: str) -> bool:
    schedule_terms = [
        "urnik", "termin objav", "termini objav", "termin objave", "termini objave",
        "trikrat na dan", "tri krat na dan", "3x na dan", "3 x na dan", "3 krat na dan",
        "samostojna objava", "samodejna objava", "avtomatska objava",
        "samostojno objavljanje", "samodejno objavljanje", "avtomatsko objavljanje",
    ]
    return any(term in low for term in schedule_terms)

def infer_mode(command: str) -> str:
    low = command.lower()
    if (
        any(x in low for x in ["ustavi", "pavza", "zaustavi", "nadaljuj", "vklopi", "izklopi", "resume", "pause"])
        or _schedule_intent(low)
    ):
        return "control"
    if any(x in low for x in ["članek", "clanek", "objavi", "napiši o", "napisi o", "prispevek"]):
        return "article"
    return "site"

def control_command(command: str) -> None:
    ctl = read_json(CONTROL, {"enabled": True, "publish_mode": "automatic"})
    low = command.lower()
    schedule_requested = _schedule_intent(low)

    if any(x in low for x in ["ustavi", "zaustavi", "izklopi", "pause", "pavza"]):
        ctl["enabled"] = False
    elif any(x in low for x in ["nadaljuj", "vklopi", "resume", "začni", "zacni"]) or schedule_requested:
        ctl["enabled"] = True

    if "draft" in low or "osnut" in low:
        ctl["publish_mode"] = "draft"
    elif "review" in low or "pregled" in low:
        ctl["publish_mode"] = "review"
    elif (
        "automatic" in low or "avtomats" in low or "samodejn" in low
        or "samostojn" in low or schedule_requested
    ):
        ctl["publish_mode"] = "automatic"

    if schedule_requested:
        ctl["schedule_profile"] = "default-3x-daily"
        ctl["schedule"] = {
            "timezone": "Europe/Ljubljana",
            "slots": [
                {"time": "08:17", "category": "sport"},
                {"time": "13:27", "category": "politika"},
                {"time": "19:43", "category": "aktualno"},
            ],
        }

    write_json(CONTROL, ctl)
    print(
        "CONTROL_OK "
        f"enabled={str(ctl.get('enabled', True)).lower()} "
        f"publish_mode={ctl.get('publish_mode', 'automatic')} "
        f"schedule_profile={ctl.get('schedule_profile', 'unchanged')}"
    )

def _sha256(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def article_command(command: str, category: str) -> None:
    app = BASE / "src/App.jsx"
    before = _sha256(app)
    cmd = [sys.executable, str(ARTICLE_AGENT), "--category", category, "--topic", command, "--force"]
    result = subprocess.run(cmd, cwd=BASE, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    after = _sha256(app)
    if not after or after == before:
        raise SystemExit("Manual article request completed without publishing a new article")

def _safe_agent_log(value: str, limit: int = 3500) -> str:
    text = str(value or "")
    text = re.sub(r"(github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+|Bearer\\s+[A-Za-z0-9._-]+)", "[REDACTED]", text, flags=re.I)
    return text[-limit:].strip()

def builtin_site_command(command: str) -> bool:
    low = command.lower()
    live_intent = (
        ("pol ure" in low or "30 min" in low or "30 minut" in low)
        and ("mini" in low or "tekoč" in low or "aktual" in low)
        and ("stolpec" in low or "stran" in low or "lev" in low)
    )
    if live_intent:
        required = [
            BASE / "src/LivePulse.jsx",
            BASE / "agents/live-feed/update.py",
            BASE / ".github/workflows/live-feed.yml",
            BASE / "public/live-feed.json",
        ]
        if all(path.exists() for path in required):
            print("BUILTIN_SITE_OK live-pulse already installed")
            return True
    return False

def site_command(command: str) -> None:
    if builtin_site_command(command):
        return
    if not shutil.which("copilot"):
        raise SystemExit("Copilot CLI is not installed")
    prompt = """You are the authenticated repository editor for DDAY2301/blog-lab. Execute the operator request below by editing the existing repository, preserving working functionality and design. Do not merely explain. You may edit normal website files under src/, public/, and the Blog Lab publisher prompts/config when relevant. The site has a structured multimedia article system in src/ArticleMedia.jsx: hero images, inline images, YouTube/direct video, galleries and structured sources. When the operator supplies media URLs, integrate them into that system instead of inventing replacements. NEVER edit .github/, terminal/, agents/operator-terminal/, AGENTS.md, requirements-agent.txt, secrets, authentication, permissions, or security controls. Do not use shell commands or network tools. Do not reveal tokens or environment variables. Keep changes minimal and production-ready.\n\nOPERATOR REQUEST:\n""" + command
    excluded = "bash,powershell,web_fetch,task,write_agent,ask_user"
    proc = subprocess.run(
        ["copilot", "-s", "-p", prompt, "--no-ask-user", "--no-custom-instructions", "--disable-builtin-mcps", f"--excluded-tools={excluded}", "--no-auto-update", "--no-remote", "--no-remote-export"],
        cwd=BASE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=240,
        check=False,
    )
    if proc.returncode != 0:
        diagnostic = _safe_agent_log((proc.stderr or "") + "\n" + (proc.stdout or ""))
        if diagnostic:
            print("COPILOT_DIAGNOSTIC_BEGIN", file=sys.stderr)
            print(diagnostic, file=sys.stderr)
            print("COPILOT_DIAGNOSTIC_END", file=sys.stderr)
        auth_hint = ""
        if os.environ.get("COPILOT_PERSONAL_TOKEN_CONFIGURED", "").lower() != "true":
            auth_hint = " Personal repositories may require repository secret COPILOT_GITHUB_TOKEN with Copilot Requests permission."
        raise SystemExit(f"Copilot edit failed with exit code {proc.returncode}.{auth_hint}")

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--command-file", required=True); args = ap.parse_args()
    payload = json.loads(Path(args.command_file).read_text(encoding="utf-8"))
    command = str(payload.get("command", "")).strip()
    mode = str(payload.get("mode", "auto")).lower()
    category = str(payload.get("category", "aktualno")).lower()
    if not command or len(command) > 4000: raise SystemExit("invalid command")
    if mode not in VALID_MODES: mode = "auto"
    if category not in VALID_CATEGORIES: category = "aktualno"
    if mode == "auto": mode = infer_mode(command)
    if mode == "control": control_command(command)
    elif mode == "article": article_command(command, category)
    elif mode == "site": site_command(command)
    return 0
if __name__ == "__main__": raise SystemExit(main())
