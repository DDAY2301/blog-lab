from pathlib import Path

from manager.db_v3 import StoreV3
from manager.notifications_v4 import NotificationCenterV4


def test_p1_notification_queues_email(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_DESKTOP_NOTIFICATIONS", "0")
    monkeypatch.setenv("GMAIL_REPORTING_ENABLED", "1")
    monkeypatch.setenv("REPORT_TO_EMAIL", "test@example.com")

    store = StoreV3(tmp_path / "state.db")
    notify = NotificationCenterV4(store)
    notify.send("P1", "Project Visibility down", "Health check failed.", "project_visibility")

    rows = store.query("SELECT * FROM email_queue WHERE kind='critical_alert'")
    assert len(rows) == 1
    assert rows[0]["recipient"] == "test@example.com"
    assert "[P1]" in rows[0]["subject"]
