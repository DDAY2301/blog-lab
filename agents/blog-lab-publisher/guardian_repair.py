from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
sys.path.insert(0, str(HERE))

from autonomous_fallback import run as fallback_run  # noqa: E402
from agent import STATE, CONTROL, load_json, atomic_json, now  # noqa: E402

TZ = ZoneInfo("Europe/Ljubljana")


def _slot_id(day: str, slot: dict) -> str:
    return f"{day}|{slot.get('time')}|{slot.get('category')}"


def _minutes(value: str) -> int | None:
    try:
        hour, minute = str(value or "").split(":", 1)
        return int(hour) * 60 + int(minute)
    except Exception:
        return None


def _state_reset_for_day(state: dict, today: str) -> dict:
    if state.get("posts_date") != today:
        state["posts_date"] = today
        state["posts_today"] = 0
        state["scheduled_posts_today"] = 0
        state["manual_posts_today"] = 0
        state["scheduled_slots_done"] = []
        state["scheduled_slots_deferred"] = []
        state["last_editorial_hold"] = None
    state.setdefault("scheduled_slots_done", [])
    state.setdefault("scheduled_slots_deferred", [])
    state.setdefault("scheduled_posts_today", 0)
    state.setdefault("manual_posts_today", 0)
    state.setdefault("posts_today", 0)
    return state


def due_repairs(current: datetime | None = None) -> list[tuple[str, str]]:
    current = current or now()
    today = current.date().isoformat()
    now_minutes = current.hour * 60 + current.minute
    control = load_json(str(CONTROL), {})
    state = _state_reset_for_day(load_json(str(STATE), {}), today)

    if control.get("enabled", True) is not True:
        print("GUARDIAN_SKIP disabled")
        return []
    if str(control.get("publish_mode", "automatic")).lower() != "automatic":
        print("GUARDIAN_SKIP not_automatic")
        return []

    slots = (control.get("schedule") or {}).get("slots") or []
    done = set(state.get("scheduled_slots_done") or [])
    deferred = set(state.get("scheduled_slots_deferred") or [])
    repairs: list[tuple[str, str]] = []

    for slot in slots:
        if not isinstance(slot, dict):
            continue
        slot_time = str(slot.get("time") or "").strip()
        category = str(slot.get("category") or "aktualno").strip().lower()
        slot_minutes = _minutes(slot_time)
        if slot_minutes is None or not category:
            continue
        sid = _slot_id(today, slot)
        if sid in done:
            continue
        # Missed or deferred slots are repair candidates once their time has passed.
        if now_minutes >= slot_minutes or sid in deferred:
            repairs.append((category, sid))

    return repairs


def main() -> int:
    repairs = due_repairs()
    if not repairs:
        print("GUARDIAN_NO_REPAIR_NEEDED")
        return 0

    # Repair one slot per run to avoid over-publishing and to keep logs simple.
    category, slot_id = repairs[0]
    print(f"GUARDIAN_REPAIR category={category} slot={slot_id}")
    rc = fallback_run(category, slot_id, dry_run=False)

    state = load_json(str(STATE), {})
    state["publisher_guardian_last_run"] = now().isoformat(timespec="seconds")
    state["publisher_guardian_last_action"] = {
        "category": category,
        "slot": slot_id,
        "remaining_repairs": max(0, len(repairs) - 1),
    }
    atomic_json(str(STATE), state)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
