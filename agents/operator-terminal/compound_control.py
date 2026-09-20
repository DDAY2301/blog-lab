from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parents[2]
CONTROL = BASE / "data/agent-control.json"
CATCHUP_LOG = BASE / "data/catchup-requests.json"
OWNER = "DDAY2301"
REPO = "blog-lab"
PUBLISHER_WORKFLOW = "agent-blog-lab-publisher.yml"
DEFAULT_SCHEDULE = {
    "timezone": "Europe/Ljubljana",
    "slots": [
        {"time": "08:17", "category": "sport"},
        {"time": "13:27", "category": "politika"},
        {"time": "19:43", "category": "aktualno"},
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def fold(value: str) -> str:
    replacements = str(value or "").lower()
    table = str.maketrans({"č": "c", "š": "s", "ž": "z", "ć": "c", "đ": "d"})
    replacements = replacements.translate(table)
    replacements = re.sub(r"[^a-z0-9]+", " ", replacements)
    return " ".join(replacements.split())


def read_json(path: Path, default):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def has_schedule_intent(text: str) -> bool:
    return (
        "3 na dan" in text
        or "3x na dan" in text
        or "tri krat na dan" in text
        or "trikrat na dan" in text
        or "po casovnici" in text
        or "po urniku" in text
        or "schedule" in text
    ) and any(term in text for term in ["objav", "clank", "article", "post"])


def has_catchup_intent(text: str) -> bool:
    article = any(term in text for term in ["clank", "article", "objav", "post", "novic"])
    missed = any(term in text for term in [
        "spustil", "spustili", "zamudil", "zamudili", "izpustil", "izpustili",
        "nadoknad", "catch up", "catchup", "missed", "skipped",
    ])
    now = any(term in text for term in ["zdaj", "sedaj", "now", "takoj", "napisi vse", "write all"])
    repair_context = any(term in text for term in ["popravk", "strani", "site", "page", "guardian", "deploy"])
    return article and (missed or (now and repair_context))


def should_handle(command: str) -> bool:
    text = fold(command)
    return has_schedule_intent(text) or has_catchup_intent(text)


def ensure_schedule(command: str, actor: str) -> dict:
    ctl = read_json(CONTROL, {})
    if not isinstance(ctl, dict):
        ctl = {}
    ctl.update({
        "enabled": True,
        "publish_mode": "automatic",
        "schedule_profile": "default-3x-daily",
        "schedule": DEFAULT_SCHEDULE,
        "last_terminal_schedule_update": {
            "at": utc_now(),
            "actor": actor or "terminal",
            "command": command[:500],
        },
    })
    write_json(CONTROL, ctl)
    return ctl


def append_log(payload: dict, dispatched: list[str], handled_reason: str) -> None:
    log = read_json(CATCHUP_LOG, [])
    if not isinstance(log, list):
        log = []
    log.append({
        "id": str(payload.get("request_id") or "manual"),
        "created_at": utc_now(),
        "actor": str(payload.get("actor") or "terminal"),
        "command": str(payload.get("command") or "")[:1000],
        "handled_reason": handled_reason,
        "publisher_dispatches": dispatched,
    })
    log = log[-80:]
    write_json(CATCHUP_LOG, log)


def dispatch_publisher(category: str) -> None:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GITHUB_TOKEN missing; cannot dispatch publisher catch-up workflow.")
    body = json.dumps({
        "ref": "main",
        "inputs": {
            "category": category,
            "dry_run": False,
            "force": True,
            "catch_up": False,
        },
    }).encode("utf-8")
    req = Request(
        f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{PUBLISHER_WORKFLOW}/dispatches",
        data=body,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "BlogLabCompoundControl/1.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=40) as response:
            if response.status not in (204, 201, 200):
                raise RuntimeError(f"Publisher dispatch returned HTTP {response.status}")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[-500:]
        raise RuntimeError(f"Publisher dispatch failed for {category}: HTTP {exc.code} {detail}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Publisher dispatch failed for {category}: {exc}") from exc


def set_output(path: str | None, key: str, value: str) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Handle deterministic compound terminal commands before AI routing.")
    parser.add_argument("--command-file", required=True)
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    parser.add_argument("--dispatch", action="store_true")
    args = parser.parse_args()

    payload = read_json(Path(args.command_file), {})
    if not isinstance(payload, dict):
        raise SystemExit("Invalid terminal command payload.")
    command = str(payload.get("command") or "").strip()
    if not should_handle(command):
        set_output(args.github_output, "handled", "false")
        print("COMPOUND_CONTROL_SKIPPED")
        return 78

    actor = str(payload.get("actor") or "terminal")
    ensure_schedule(command, actor)
    text = fold(command)
    dispatched: list[str] = []
    if has_catchup_intent(text):
        for category in ("sport", "politika", "aktualno"):
            dispatch_publisher(category)
            dispatched.append(category)

    reason = "schedule_and_article_catchup" if dispatched else "schedule_only"
    append_log(payload, dispatched, reason)
    set_output(args.github_output, "handled", "true")
    set_output(args.github_output, "reason", reason)
    set_output(args.github_output, "dispatched", str(len(dispatched)))
    print(f"COMPOUND_CONTROL_HANDLED reason={reason} dispatched={len(dispatched)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
