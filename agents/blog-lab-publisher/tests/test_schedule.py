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
        "scheduled_posts_today": 1,
        "scheduled_slots_done": ["2026-09-20|08:17|sport"],
    }
    result = resolve_due_slot(CONTROL, state, at(9, 30))
    assert result["run"] is False


def test_next_due_slot_runs_after_previous_is_done():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_posts_today": 1,
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
        "scheduled_posts_today": 3,
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


def test_deferred_morning_slot_does_not_repeat_before_next_slot():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_posts_today": 0,
        "scheduled_slots_done": [],
        "scheduled_slots_deferred": ["2026-09-20|08:17|sport"],
    }
    result = resolve_due_slot(CONTROL, state, at(10, 30))
    assert result["run"] is False
    assert result["reason"] == "nothing_due"


def test_deferred_morning_slot_does_not_block_politics():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_posts_today": 0,
        "scheduled_slots_done": [],
        "scheduled_slots_deferred": ["2026-09-20|08:17|sport"],
    }
    result = resolve_due_slot(CONTROL, state, at(14, 0))
    assert result["run"] is True
    assert result["category"] == "politika"
    assert result["slot"] == "2026-09-20|13:27|politika"


def test_ai_unavailable_deferred_slot_is_retried():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_posts_today": 0,
        "scheduled_slots_done": [],
        "scheduled_slots_deferred": ["2026-09-20|08:17|sport"],
        "writer_mode": "unavailable",
        "last_error": "manual_ai_unavailable",
        "last_editorial_hold": {
            "slot": "2026-09-20|08:17|sport",
            "reason": "ai_unavailable",
            "at": "2026-09-20T09:00:00+02:00",
        },
    }
    result = resolve_due_slot(CONTROL, state, at(10, 30))
    assert result["run"] is True
    assert result["category"] == "sport"
    assert result["slot"] == "2026-09-20|08:17|sport"


def test_today_production_ai_unavailable_state_catches_first_missed_slot():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_posts_today": 0,
        "scheduled_slots_done": [],
        "scheduled_slots_deferred": [
            "2026-09-20|08:17|sport",
            "2026-09-20|13:27|politika",
        ],
        "writer_mode": "unavailable",
        "last_error": "manual_ai_unavailable",
        "last_editorial_hold": {
            "slot": "2026-09-20|13:27|politika",
            "reason": "ai_unavailable",
            "at": "2026-09-20T14:08:30+02:00",
        },
    }
    result = resolve_due_slot(CONTROL, state, at(16, 40))
    assert result["run"] is True
    assert result["category"] == "sport"
    assert result["slot"] == "2026-09-20|08:17|sport"


def test_deferred_slot_from_previous_day_is_ignored():
    state = {
        "posts_date": "2026-09-19",
        "scheduled_posts_today": 0,
        "scheduled_slots_deferred": ["2026-09-19|08:17|sport"],
    }
    result = resolve_due_slot(CONTROL, state, at(9, 0))
    assert result["run"] is True
    assert result["category"] == "sport"


def test_completed_count_migration_skips_deferred_slot():
    state = {
        "posts_date": "2026-09-20",
        "scheduled_posts_today": 1,
        "scheduled_slots_done": [],
        "scheduled_slots_deferred": ["2026-09-20|08:17|sport"],
    }
    result = resolve_due_slot(CONTROL, state, at(20, 0))
    assert result["run"] is True
    assert result["category"] == "aktualno"
