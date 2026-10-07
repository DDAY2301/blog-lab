from pathlib import Path

from manager.daily_email_v4 import DailyEmailReporterV4
from manager.db_v3 import StoreV3


class FakeGmail:
    def __init__(self):
        self.recipient = "test@example.com"

    def auth_state(self):
        return "CONFIGURED"


def test_daily_email_queues_once(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_DAILY_EMAIL_HOUR", "0")
    store = StoreV3(tmp_path / "state.db")
    reporter = DailyEmailReporterV4(store, FakeGmail())

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
    rows = store.query("SELECT * FROM email_queue WHERE kind='daily_status'")
    assert len(rows) == 1
    assert rows[0]["recipient"] == "test@example.com"
