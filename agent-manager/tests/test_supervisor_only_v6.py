import asyncio
from pathlib import Path

from manager.db_v3 import StoreV3
from manager.managed_agents_v4 import ManagedAgentSupervisorV4, ManagedTarget
from manager.monitor_v3 import MonitorLoopV3
from manager.settings_v3 import SettingsV3


def _default_targets_path():
    return Path(__file__).resolve().parents[1] / "data" / "managed_agents.json"


def test_supervisor_only_filters_only_local_production_targets(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    sup = ManagedAgentSupervisorV4(StoreV3(tmp_path / "agent.db"), _default_targets_path())
    ids = {target.id for target in sup.targets()}
    assert "project_visibility" not in ids
    assert "project_visibility_process" not in ids
    assert "project_visibility_github" in ids
    assert "bloglab_worker" in ids
    assert "bloglab_github" in ids
    assert "bloglab_live" in ids


def test_supervisor_mode_blocks_local_restart(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    sup = ManagedAgentSupervisorV4(StoreV3(tmp_path / "agent.db"), _default_targets_path())
    target = ManagedTarget(
        id="project_visibility",
        name="Project Visibility",
        kind="http",
        health_url="http://127.0.0.1:8000/health",
        repair_adapter="project_visibility_restart",
    )
    result = sup.repair(target)
    assert result["stage"] == "policy"
    assert not result["ok"]


def test_supervisor_monitor_skips_local_pv_and_resolves_obsolete_alert(tmp_path, monkeypatch):
    from manager import monitor_v3
    store = StoreV3(tmp_path / "agent.db")
    loop = MonitorLoopV3(SettingsV3(supervisor_only=True), store)
    loop.inc.raise_or_update(
        "project_visibility", "Health endpoint unreachable", "P1", ["old local outage"]
    )
    urls = []

    async def fake_health(url):
        urls.append(url)
        return {"ok": True}

    monkeypatch.setattr(monitor_v3, "http_health", fake_health)
    monkeypatch.setattr(
        monitor_v3, "system_resources",
        lambda: {"ram_percent": 50, "disk_percent": 30},
    )
    data = asyncio.run(loop.cycle())
    assert data["project_visibility"]["state"] == "not_applicable"
    assert "http://127.0.0.1:8000/health" not in urls
    assert any("/api/tags" in url for url in urls)
    old = store.query(
        "SELECT * FROM incidents WHERE component='project_visibility' AND title='Health endpoint unreachable'"
    )
    assert old and old[0]["status"] == "resolved"


def test_normal_monitor_keeps_local_probe(tmp_path, monkeypatch):
    from manager import monitor_v3
    store = StoreV3(tmp_path / "agent.db")
    loop = MonitorLoopV3(SettingsV3(supervisor_only=False), store)
    urls = []

    async def fake_health(url):
        urls.append(url)
        return {"ok": True}

    monkeypatch.setattr(monitor_v3, "http_health", fake_health)
    monkeypatch.setattr(
        monitor_v3, "system_resources",
        lambda: {"ram_percent": 50, "disk_percent": 30},
    )
    data = asyncio.run(loop.cycle())
    assert data["project_visibility"]["ok"] is True
    assert "http://127.0.0.1:8000/health" in urls



def test_supervisor_check_resolves_only_old_local_pv_incidents(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    store = StoreV3(tmp_path / "agent.db")
    sup = ManagedAgentSupervisorV4(store, _default_targets_path())
    for target_id, title in (
        ("project_visibility", "Project Visibility health degraded"),
        ("project_visibility_process", "Project Visibility Local Process health degraded"),
        ("project_visibility_github", "Project Visibility GitHub health degraded"),
    ):
        sup.incidents.raise_or_update(target_id, title, "P1", ["historic"])
    # No unrelated remote incident may be marked healthy by disabling local PV.
    async def fake_check(target):
        return {"id": target.id, "name": target.name, "ok": False, "error": "unverified remote"}
    monkeypatch.setattr(sup, "check", fake_check)
    asyncio.run(sup.check_all())
    rows = {
        row["component"]: row["status"]
        for row in store.query("SELECT * FROM incidents")
        if row["title"].startswith("Project Visibility")
    }
    assert rows["project_visibility"] == "resolved"
    assert rows["project_visibility_process"] == "resolved"
    assert rows["project_visibility_github"] == "open"
