import asyncio
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from manager.db_v3 import StoreV3
from manager.readonly_schedules_v8 import ReadonlySchedulesV8


class FakeBus:
    @staticmethod
    def _simple_operator_target(command):
        return "manager" if command.lower() in {"status", "incidenti"} else ""

    async def execute(self, command, **kwargs):
        return {"status": "completed", "job_id": "test-job"}


def test_schedule_is_timezone_aware_and_owner_scoped(tmp_path):
    store = StoreV3(tmp_path / "manager.sqlite")
    runner = ReadonlySchedulesV8(store, FakeBus(), None)
    dt = (datetime.now(timezone.utc) + timedelta(hours=2)).astimezone(
        ZoneInfo("Europe/Ljubljana")
    ).strftime("%Y-%m-%dT%H:%M")
    result = runner.create("Owner@Example.com", dt, "status")
    assert result["status"] == "pending"
    assert result["schedule_id"].startswith("SCH-")
    assert len(runner.list_owned("owner@example.com")) == 1
    assert not runner.list_owned("other@example.com")
    assert not runner.cancel("other@example.com", result["schedule_id"])["cancelled"]
    assert runner.cancel("owner@example.com", result["schedule_id"])["cancelled"]


def test_schedule_does_not_allow_mutation_or_past(tmp_path):
    store = StoreV3(tmp_path / "manager.sqlite")
    runner = ReadonlySchedulesV8(store, FakeBus(), None)
    with pytest.raises(ValueError, match="read-only"):
        runner.create("owner@example.com", "2026-11-01T10:00", "publish site")
    with pytest.raises(ValueError, match="future"):
        runner.create("owner@example.com", "2020-01-01T10:00", "status")


def test_due_schedule_executes_once_and_queues_email(tmp_path):
    store = StoreV3(tmp_path / "manager.sqlite")
    runner = ReadonlySchedulesV8(store, FakeBus(), None)
    dt = (datetime.now(timezone.utc) + timedelta(hours=2)).astimezone(
        ZoneInfo("Europe/Ljubljana")
    ).strftime("%Y-%m-%dT%H:%M")
    sid = runner.create("owner@example.com", dt, "status")["schedule_id"]
    store.execute(
        "UPDATE readonly_schedules_v8 SET run_at_utc=? WHERE schedule_id=?",
        ((datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(), sid),
    )
    first = asyncio.run(runner.run_due())
    second = asyncio.run(runner.run_due())
    assert first == [{"schedule_id": sid, "status": "completed"}]
    assert second == []
    assert store.query(
        "SELECT * FROM email_queue WHERE subject LIKE ?", (f"%{sid}%",)
    )


def test_reboot_does_not_repeat_inflight_schedules(tmp_path):
    store = StoreV3(tmp_path / "manager.sqlite")
    runner = ReadonlySchedulesV8(store, FakeBus(), None)
    dt = (datetime.now(timezone.utc) + timedelta(hours=2)).astimezone(
        ZoneInfo("Europe/Ljubljana")
    ).strftime("%Y-%m-%dT%H:%M")
    sid = runner.create("owner@example.com", dt, "status")["schedule_id"]
    store.execute(
        "UPDATE readonly_schedules_v8 SET status='running' WHERE schedule_id=?",
        (sid,),
    )
    restarted = ReadonlySchedulesV8(store, FakeBus(), None)
    assert runner.list_owned("owner@example.com")[0]["status"] == "running"
    restarted.recover_interrupted()
    assert runner.list_owned("owner@example.com")[0]["status"] == "interrupted"
