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

def infer_mode(command: str) -> str:
    low = command.lower()
    if any(x in low for x in ["ustavi", "pavza", "zaustavi", "nadaljuj", "vklopi", "izklopi", "resume", "pause"]): return "control"
    if any(x in low for x in ["članek", "clanek", "objavi", "napiši o", "napisi o", "prispevek"]): return "article"
    return "site"

def control_command(command: str) -> None:
    ctl = read_json(CONTROL, {"enabled": True})
    low = command.lower()
    if any(x in low for x in ["ustavi", "zaustavi", "izklopi", "pause", "pavza"]): ctl["enabled"] = False
    elif any(x in low for x in ["nadaljuj", "vklopi", "resume", "začni", "zacni"]): ctl["enabled"] = True
    if "draft" in low or "osnut" in low: ctl["publish_mode"] = "draft"
    elif "review" in low or "pregled" in low: ctl["publish_mode"] = "review"
    elif "automatic" in low or "avtomats" in low or "samodejn" in low: ctl["publish_mode"] = "automatic"
    write_json(CONTROL, ctl)

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

def site_command(command: str) -> None:
    if not shutil.which("copilot"):
        raise SystemExit("Copilot CLI is not installed")
    prompt = """You are the authenticated repository editor for DDAY2301/blog-lab. Execute the operator request below by editing the existing repository, preserving working functionality and design. Do not merely explain. You may edit normal website files under src/, public/, and the Blog Lab publisher prompts/config when relevant. NEVER edit .github/, terminal/, agents/operator-terminal/, AGENTS.md, requirements-agent.txt, secrets, authentication, permissions, or security controls. Do not use shell commands or network tools. Do not reveal tokens or environment variables. Keep changes minimal and production-ready.\n\nOPERATOR REQUEST:\n""" + command
    excluded = "bash,powershell,web_fetch,task,write_agent,ask_user"
    proc = subprocess.run(["copilot", "-s", "-p", prompt, "--no-ask-user", "--no-custom-instructions", "--disable-builtin-mcps", f"--excluded-tools={excluded}", "--no-auto-update", "--no-remote", "--no-remote-export"], cwd=BASE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=240, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"Copilot edit failed with exit code {proc.returncode}")

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
