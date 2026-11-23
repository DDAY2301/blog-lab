from datetime import datetime, timedelta
from pathlib import Path

from manager.daily_email_v4 import PeriodicEmailReporterV4
from manager.db_v3 import StoreV3


class FakeGmail:
    def __init__(self):
        self.recipient = "test@example.com"

    def auth_state(self):
        return "CONFIGURED"


def test_periodic_email_queues_once_then_waits(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_EMAIL_INTERVAL_HOURS", "3")
    store = StoreV3(tmp_path / "state.db")
    reporter = PeriodicEmailReporterV4(store, FakeGmail())

    report = {
        "state": "HEALTHY",
        "managed_total": 1,
        "managed_ok": 1,
        "managed_failing": 0,
        "open_incidents": [],
        "providers": {"ollama": {"ok": True, "model": "demo"}, "colibri": {"ok": False}},
        "targets": [{"id": "pv", "name": "Project Visibility", "ok": True}],
    }

    assert reporter.queue_if_due(report) is True
    assert reporter.queue_if_due(report) is False

    rows = store.query("SELECT * FROM email_queue WHERE kind='periodic_status'")
    assert len(rows) == 1
    assert rows[0]["recipient"] == "test@example.com"


def test_periodic_email_due_after_interval(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_EMAIL_INTERVAL_HOURS", "3")
    store = StoreV3(tmp_path / "state.db")
    reporter = PeriodicEmailReporterV4(store, FakeGmail())

    old = (datetime.now() - timedelta(hours=4)).isoformat()
    store.execute(
        "INSERT INTO email_queue(created_at,kind,priority,recipient,subject,body,status) "
        "VALUES(?,?,?,?,?,?,'sent')",
        (old, "periodic_status", 50, "test@example.com", "old", "body"),
    )

    report = {
        "state": "HEALTHY",
        "managed_total": 1,
        "managed_ok": 1,
        "managed_failing": 0,
        "open_incidents": [],
        "providers": {},
        "targets": [],
    }

    assert reporter.queue_if_due(report) is True
