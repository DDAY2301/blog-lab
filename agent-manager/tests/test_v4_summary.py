from pathlib import Path

from manager.db_v3 import StoreV3
from manager.notifications_v4 import NotificationCenterV4
from manager.summary_v4 import SummaryReporterV4


def test_summary_healthy(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_DESKTOP_NOTIFICATIONS", "0")
    store = StoreV3(tmp_path / "state.db")
    notify = NotificationCenterV4(store)
    summary = SummaryReporterV4(store, notify)
    result = summary.build([{"id": "a", "name": "A", "ok": True}], {"ollama": {"ok": True}})
    assert result["state"] == "HEALTHY"
    assert result["managed_ok"] == 1
    assert result["managed_failing"] == 0


def test_summary_degraded_on_failed_target(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_DESKTOP_NOTIFICATIONS", "0")
    store = StoreV3(tmp_path / "state.db")
    notify = NotificationCenterV4(store)
    summary = SummaryReporterV4(store, notify)
    result = summary.build([{"id": "a", "name": "A", "ok": False, "error": "down"}], {})
    assert result["state"] == "DEGRADED"
    assert result["managed_failing"] == 1
