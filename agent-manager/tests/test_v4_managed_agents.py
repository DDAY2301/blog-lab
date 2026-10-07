from pathlib import Path

from manager.db_v3 import StoreV3
from manager.managed_agents_v4 import ManagedAgentSupervisorV4


def test_managed_target_roundtrip(tmp_path: Path):
    store = StoreV3(tmp_path / "state.db")
    config = tmp_path / "targets.json"
    config.write_text('{"version":1,"targets":[]}', encoding="utf-8")
    sup = ManagedAgentSupervisorV4(store, config)

    target = sup.save_target(
        {
            "id": "demo",
            "name": "Demo",
            "kind": "http",
            "enabled": True,
            "health_url": "http://127.0.0.1:9999/health",
            "repo": "",
            "branch": "main",
            "workflows": None,
            "repair_adapter": "",
            "local_root_env": "",
        }
    )
    assert target.id == "demo"
    assert any(x.id == "demo" for x in sup.targets())
    assert sup.remove_target("demo") is True
    assert not sup.targets()


def test_reject_unknown_repair_adapter(tmp_path: Path):
    store = StoreV3(tmp_path / "state.db")
    config = tmp_path / "targets.json"
    config.write_text('{"version":1,"targets":[]}', encoding="utf-8")
    sup = ManagedAgentSupervisorV4(store, config)
    try:
        sup.save_target(
            {
                "id": "bad",
                "name": "Bad",
                "kind": "http",
                "health_url": "http://127.0.0.1/",
                "repair_adapter": "arbitrary_shell",
            }
        )
        assert False, "expected ValueError"
    except ValueError:
        pass
