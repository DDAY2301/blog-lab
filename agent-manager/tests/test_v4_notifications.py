from pathlib import Path

from manager.db_v3 import StoreV3
from manager.notifications_v4 import NotificationCenterV4


def test_notification_persists(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_DESKTOP_NOTIFICATIONS", "0")
    store = StoreV3(tmp_path / "state.db")
    n = NotificationCenterV4(store)
    n.send("P2", "Test", "body", "unit")
    rows = n.recent()
    assert rows[0]["title"] == "Test"
    assert rows[0]["source"] == "unit"
