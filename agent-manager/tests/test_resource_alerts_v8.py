import asyncio

from manager.db_v3 import StoreV3
from manager.monitor_v3 import MonitorLoopV3
from manager.settings_v3 import SettingsV3


def test_ram_and_disk_alerts_resolve_after_recovery(tmp_path, monkeypatch):
    from manager import monitor_v3
    store = StoreV3(tmp_path / "manager.db")
    monitor = MonitorLoopV3(SettingsV3(supervisor_only=True), store)
    current = {"ram_percent": 95, "disk_percent": 97}
    monkeypatch.setattr(monitor_v3, "system_resources", lambda: current.copy())

    async def healthy(*args, **kwargs):
        return {"ok": True}
    monkeypatch.setattr(monitor_v3, "http_health", healthy)

    asyncio.run(monitor.cycle())
    rows = store.query("SELECT title,status FROM incidents WHERE component='system'")
    assert {x["title"] for x in rows} == {"RAM critical", "RAM elevated", "Disk critical"}
    assert all(x["status"] == "open" for x in rows)

    current.update(ram_percent=71, disk_percent=70)
    asyncio.run(monitor.cycle())
    rows = store.query("SELECT title,status FROM incidents WHERE component='system'")
    assert all(x["status"] == "resolved" for x in rows)


def test_missing_resource_metrics_do_not_resolve_existing_incidents(tmp_path, monkeypatch):
    from manager import monitor_v3
    store = StoreV3(tmp_path / "manager.db")
    monitor = MonitorLoopV3(SettingsV3(supervisor_only=True), store)
    monitor.inc.raise_or_update("system", "RAM critical", "P1", ["previous"])
    monkeypatch.setattr(monitor_v3, "system_resources", lambda: {"error": "psutil unavailable"})

    async def healthy(*args, **kwargs):
        return {"ok": True}
    monkeypatch.setattr(monitor_v3, "http_health", healthy)
    asyncio.run(monitor.cycle())
    assert store.query(
        "SELECT status FROM incidents WHERE title='RAM critical'"
    )[0]["status"] == "open"
