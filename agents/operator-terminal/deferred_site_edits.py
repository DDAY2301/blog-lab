from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parents[2]
QUEUE = BASE / "data/deferred-site-edits.json"
COMMAND = BASE / "agents/operator-terminal/command.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_queue() -> list[dict]:
    try:
        data = json.loads(QUEUE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def compact_queue(items: list[dict], history_limit: int = 120) -> list[dict]:
    pending = [item for item in items if item.get("status") == "pending"]
    finished = [item for item in items if item.get("status") != "pending"]
    return pending + finished[-max(20, history_limit):]


def save_queue(items: list[dict]) -> None:
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    tmp = QUEUE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(compact_queue(items), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(QUEUE)


def read_payload(command_file: str) -> dict:
    data = json.loads(Path(command_file).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Deferred command payload must be a JSON object.")
    return data


def compact_reason(value: str, limit: int = 1400) -> str:
    text = " ".join(str(value or "").split())
    return text[-limit:]


def is_capacity_log(value: str) -> bool:
    low = str(value or "").lower()
    return (
        "site_ai_capacity_unavailable" in low
        or "ai capacity unavailable" in low
        or "workers ai kvota" in low
        or "workers ai quota" in low
        or "daily free allocation" in low
        or ("workers ai" in low and "capacity" in low)
    )


def append_deferred(command_file: str, request_id: str, reason: str) -> int:
    payload = read_payload(command_file)
    command = str(payload.get("command") or "").strip()
    if not command:
        raise SystemExit("Cannot defer an empty site command.")

    request_id = str(request_id or payload.get("request_id") or "manual").strip() or "manual"
    items = load_queue()
    existing = next((item for item in items if item.get("id") == request_id), None)
    entry = existing if existing is not None else {}
    entry.update({
        "id": request_id,
        "status": "pending",
        "command": command,
        "mode": "site",
        "category": str(payload.get("category") or "aktualno"),
        "actor": str(payload.get("actor") or "terminal"),
        "created_at": entry.get("created_at") or utc_now(),
        "updated_at": utc_now(),
        "attempts": int(entry.get("attempts") or 0),
        "reason": compact_reason(reason),
    })
    if existing is None:
        items.append(entry)
    save_queue(items)
    print(f"DEFERRED_SITE_EDIT_QUEUED id={request_id} pending={sum(1 for item in items if item.get('status') == 'pending')}")
    return 0


def command_file_for(entry: dict, workdir: Path) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)
    path = workdir / f"deferred-{entry.get('id', 'site')}.json"
    payload = {
        "request_id": entry.get("id"),
        "command": entry.get("command"),
        "mode": "site",
        "category": entry.get("category") or "aktualno",
        "actor": entry.get("actor") or "deferred-site-edits",
        "created_at": entry.get("created_at") or utc_now(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def replay(max_items: int) -> int:
    items = load_queue()
    pending = [item for item in items if item.get("status") == "pending" and str(item.get("command") or "").strip()]
    if not pending:
        print("DEFERRED_SITE_EDIT_NONE")
        return 0

    workdir = Path(os.environ.get("RUNNER_TEMP") or (BASE / ".tmp")) / "deferred-site-edits"
    processed = 0
    resolved = 0
    still_pending = 0

    for entry in pending[: max(1, max_items)]:
        processed += 1
        entry["attempts"] = int(entry.get("attempts") or 0) + 1
        entry["last_attempt_at"] = utc_now()
        command_file = command_file_for(entry, workdir)
        try:
            proc = subprocess.run(
                [sys.executable, str(COMMAND), "--command-file", str(command_file)],
                cwd=BASE,
                text=True,
                capture_output=True,
                check=False,
                timeout=900,
            )
        except subprocess.TimeoutExpired:
            entry["status"] = "pending"
            entry["reason"] = "Transient site-edit timeout; will retry later."
            entry["updated_at"] = utc_now()
            still_pending += 1
            print(f"DEFERRED_SITE_EDIT_TIMEOUT id={entry.get('id')} attempts={entry.get('attempts')}")
            continue
        log = compact_reason((proc.stdout or "") + "\n" + (proc.stderr or ""), limit=2400)
        entry["last_log"] = log
        entry["updated_at"] = utc_now()
        if proc.returncode == 0:
            entry["status"] = "resolved"
            entry["resolved_at"] = utc_now()
            resolved += 1
            print(f"DEFERRED_SITE_EDIT_RESOLVED id={entry.get('id')} attempts={entry.get('attempts')}")
        elif proc.returncode == 64 and is_capacity_log(log):
            entry["status"] = "pending"
            entry["reason"] = "Workers AI capacity still unavailable; will retry later."
            still_pending += 1
            print(f"DEFERRED_SITE_EDIT_STILL_PENDING id={entry.get('id')} attempts={entry.get('attempts')}")
        else:
            entry["status"] = "failed"
            entry["failed_at"] = utc_now()
            entry["reason"] = log or f"command.py exited with {proc.returncode}"
            print(f"DEFERRED_SITE_EDIT_FAILED id={entry.get('id')} rc={proc.returncode}")

    save_queue(items)
    print(f"DEFERRED_SITE_EDIT_SUMMARY processed={processed} resolved={resolved} still_pending={still_pending}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Queue and replay Blog Lab site edits deferred by Workers AI capacity limits.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    append = sub.add_parser("append")
    append.add_argument("--command-file", required=True)
    append.add_argument("--request-id", required=True)
    append.add_argument("--reason", required=True)

    replay_cmd = sub.add_parser("replay")
    replay_cmd.add_argument("--max", type=int, default=2)

    args = parser.parse_args()
    if args.cmd == "append":
        return append_deferred(args.command_file, args.request_id, args.reason)
    if args.cmd == "replay":
        return replay(args.max)
    raise SystemExit("unknown command")


if __name__ == "__main__":
    raise SystemExit(main())
