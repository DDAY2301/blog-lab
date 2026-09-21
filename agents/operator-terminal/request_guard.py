from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[2]
LEDGER = BASE / "data" / "terminal-request-ledger.json"
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)
MAX_ENTRIES = 250


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def valid_request_id(value: str) -> str:
    value = str(value or "").strip().lower()
    if not UUID_RE.fullmatch(value):
        raise SystemExit("Invalid terminal request ID.")
    return value


def load_ledger() -> list[dict]:
    try:
        data = json.loads(LEDGER.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_ledger(items: list[dict]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    compact = items[-MAX_ENTRIES:]
    tmp = LEDGER.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(compact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(LEDGER)


def is_processed(request_id: str) -> bool:
    rid = valid_request_id(request_id)
    return any(str(item.get("id") or "").lower() == rid for item in load_ledger() if isinstance(item, dict))


def set_output(path: str | None, key: str, value: str) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{key}={value}\n")


def check(request_id: str, github_output: str = "") -> int:
    rid = valid_request_id(request_id)
    duplicate = is_processed(rid)
    set_output(github_output, "duplicate", "true" if duplicate else "false")
    print(f"TERMINAL_REQUEST_GUARD id={rid} duplicate={str(duplicate).lower()}")
    return 0


def mark(request_id: str) -> int:
    rid = valid_request_id(request_id)
    items = load_ledger()
    if any(str(item.get("id") or "").lower() == rid for item in items if isinstance(item, dict)):
        print(f"TERMINAL_REQUEST_ALREADY_MARKED id={rid}")
        return 0
    items.append({
        "id": rid,
        "processed_at": utc_now(),
        "workflow_run_id": str(os.environ.get("GITHUB_RUN_ID") or ""),
        "workflow_run_attempt": str(os.environ.get("GITHUB_RUN_ATTEMPT") or ""),
    })
    save_ledger(items)
    print(f"TERMINAL_REQUEST_MARKED id={rid} ledger_entries={len(load_ledger())}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Idempotency guard for private terminal workflow requests.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    chk = sub.add_parser("check")
    chk.add_argument("--request-id", required=True)
    chk.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))

    mrk = sub.add_parser("mark")
    mrk.add_argument("--request-id", required=True)

    args = parser.parse_args()
    if args.cmd == "check":
        return check(args.request_id, args.github_output)
    if args.cmd == "mark":
        return mark(args.request_id)
    raise SystemExit("unknown request guard command")


if __name__ == "__main__":
    raise SystemExit(main())
