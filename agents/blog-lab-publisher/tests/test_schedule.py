from datetime import datetime
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from schedule import resolve_due_slot

TZ = ZoneInfo("Europe/Ljubljana")
CONTROL = {
    "enabled": True,
    "publish_mode": "automatic",
    "schedule": {
        "timezone": "Europe/Ljubljana",
        "slots": [
            {"time": "08:17", "category": "sport"},
            {"time": "13:27", "category": "politika"},
            {"time": "19:43", "category": "aktualno"},
        ],
    },
}


def at(hour: int, minute: int):
    return datetime(2026, 9, 20, hour, minute, tzinfo=TZ)


def test_nothing_due_before_first_slot():
    result = resolve_due_slot(CONTROL, {}, at(8, 10))
    assert result["run"] is False
    assert result["reason"] == "nothing_due"


def test_missed_morning_slot_is_caught_up_later():
    result = resolve_due_slot(CONTROL, {"posts_date": "2026-09-20"}, at(9, 0))
    assert result["run"] is True
    assert result["category"] == "sport"
    assert result["slot"] == "2026-09-20|08:17|sport"


def test_completed_slot_is_not_repeated():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_slots_done": ["2026-09-20|08:17|sport"],
    }
    result = resolve_due_slot(CONTROL, state, at(9, 30))
    assert result["run"] is False


def test_next_due_slot_runs_after_previous_is_done():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_slots_done": ["2026-09-20|08:17|sport"],
    }
    result = resolve_due_slot(CONTROL, state, at(14, 0))
    assert result["run"] is True
    assert result["category"] == "politika"
    assert result["slot"] == "2026-09-20|13:27|politika"


def test_old_counter_migrates_to_first_completed_slots():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_posts_today": 1,
    }
    result = resolve_due_slot(CONTROL, state, at(14, 0))
    assert result["run"] is True
    assert result["category"] == "politika"


def test_all_due_slots_done_returns_nothing_due():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_slots_done": [
            "2026-09-20|08:17|sport",
            "2026-09-20|13:27|politika",
            "2026-09-20|19:43|aktualno",
        ],
    }
    result = resolve_due_slot(CONTROL, state, at(22, 0))
    assert result["run"] is False


def test_disabled_or_nonautomatic_does_not_run():
    disabled = {**CONTROL, "enabled": False}
    review = {**CONTROL, "publish_mode": "review"}
    assert resolve_due_slot(disabled, {}, at(9, 0))["run"] is False
    assert resolve_due_slot(review, {}, at(9, 0))["run"] is False


def test_slot_marked_done_without_scheduled_post_is_reopened():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_posts_today": 0,
        "scheduled_slots_done": ["2026-09-20|08:17|sport"],
    }
    result = resolve_due_slot(CONTROL, state, at(9, 40))
    assert result["run"] is True
    assert result["category"] == "sport"
    assert result["slot"] == "2026-09-20|08:17|sport"
