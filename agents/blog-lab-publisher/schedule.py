from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parents[2]
CONTROL = BASE / "data/agent-control.json"
STATE = BASE / "data/agent-state.json"
TZ = ZoneInfo("Europe/Ljubljana")


def _load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _slot_id(day: str, slot: dict) -> str:
    return f"{day}|{slot.get('time','')}|{slot.get('category','')}"


def resolve_due_slot(control: dict, state: dict, current: datetime | None = None) -> dict:
    current = current or datetime.now(TZ)
    if current.tzinfo is None:
        current = current.replace(tzinfo=TZ)
    else:
        current = current.astimezone(TZ)

    if control.get("enabled", True) is not True:
        return {"run": False, "reason": "disabled"}
    if str(control.get("publish_mode", "automatic")).lower() != "automatic":
        return {"run": False, "reason": "not_automatic"}

    schedule = control.get("schedule") or {}
    slots = schedule.get("slots") or []
    today = current.date().isoformat()
    done = set(state.get("scheduled_slots_done") or [])
    deferred = set(state.get("scheduled_slots_deferred") or []) if state.get("posts_date") == today else set()

    # completed slot IDs represent actual successful scheduled publications.
    # Reconcile any legacy/bad state where a slot was marked done without a
    # corresponding scheduled post count.
    if state.get("posts_date") == today:
        actual_count = max(0, int(state.get("scheduled_posts_today") or 0))
        ordered_today = [_slot_id(today, slot) for slot in slots]
        trusted = [slot_id for slot_id in ordered_today if slot_id in done][:actual_count]
        done = set(trusted)

        # Migration safety: before scheduled_slots_done existed, preserve the
        # meaning of scheduled_posts_today by treating the first N slots as done.
        if actual_count and len(done) < actual_count:
            eligible = [slot_id for slot_id in ordered_today if slot_id not in deferred]
            done = set(eligible[:actual_count])

    now_minutes = current.hour * 60 + current.minute
    for slot in slots:
        raw_time = str(slot.get("time") or "")
        category = str(slot.get("category") or "").strip()
        try:
            hour, minute = [int(x) for x in raw_time.split(":", 1)]
        except Exception:
            continue
        if not category or not (0 <= hour <= 23 and 0 <= minute <= 59):
            continue
        sid = _slot_id(today, slot)
        if sid in done or sid in deferred:
            continue
        if now_minutes >= hour * 60 + minute:
            return {
                "run": True,
                "category": category,
                "slot": sid,
                "slot_time": raw_time,
                "reason": "due",
            }

    return {"run": False, "reason": "nothing_due"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--github-output", default="")
    args = ap.parse_args()

    result = resolve_due_slot(
        _load(CONTROL, {"enabled": True, "publish_mode": "automatic"}),
        _load(STATE, {}),
    )
    print(json.dumps(result, ensure_ascii=False))

    if args.github_output:
        out = Path(args.github_output)
        with out.open("a", encoding="utf-8") as fh:
            fh.write(f"run={'true' if result.get('run') else 'false'}\n")
            fh.write(f"category={result.get('category','')}\n")
            fh.write(f"slot={result.get('slot','')}\n")
            fh.write(f"slot_time={result.get('slot_time','')}\n")
            fh.write(f"reason={result.get('reason','')}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
