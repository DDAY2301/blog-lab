from pathlib import Path

from manager.db_v3 import StoreV3
from manager.incidents_v3 import IncidentEngineV3
from manager.maintenance_v4 import MaintenanceLoopV4
from manager.settings_v3 import SettingsV3


def test_reopened_incident_is_diagnosed_again(tmp_path: Path, monkeypatch):
    target_file = tmp_path / "targets.json"
    target_file.write_text('{"version":1,"targets":[]}', encoding="utf-8")
    monkeypatch.setenv("AGENT_MANAGER_TARGETS", str(target_file))

    settings = SettingsV3(db_path=tmp_path / "state.db")
    store = StoreV3(settings.db_path)
    engine = IncidentEngineV3(store)

    incident = engine.raise_or_update("demo", "Repeated outage", "P1", ["first"])
    store.action(
        "maintenance-v4",
        "ai_diagnosis",
        incident["id"],
        "completed",
        {"old": True},
    )
    # Make the old diagnosis unambiguously older than the resolved occurrence.
    store.execute(
        "UPDATE actions SET ts='2000-01-01T00:00:00+00:00' WHERE action='ai_diagnosis' AND target=?",
        (incident["id"],),
    )
    engine.resolve(incident["id"], {"fixed": True})
    reopened = engine.raise_or_update("demo", "Repeated outage", "P1", ["again"])
    assert reopened["status"] == "open"
    assert reopened["resolved_at"] is not None

    loop = MaintenanceLoopV4(settings, store)
    scheduled = []
    monkeypatch.setattr(loop, "_spawn", lambda key, factory: scheduled.append(key))
    loop._schedule_ai_work([])

    assert f"diagnose:{incident['id']}" in scheduled
