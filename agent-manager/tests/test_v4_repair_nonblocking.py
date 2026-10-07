import asyncio
import time
from pathlib import Path

from manager.db_v3 import StoreV3
from manager.managed_agents_v4 import ManagedAgentSupervisorV4, ManagedTarget


def test_automatic_repair_is_scheduled_without_blocking_event_loop(tmp_path: Path, monkeypatch):
    store = StoreV3(tmp_path / "state.db")
    config = tmp_path / "targets.json"
    config.write_text('{"version":1,"targets":[]}', encoding="utf-8")
    supervisor = ManagedAgentSupervisorV4(store, config)
    target = ManagedTarget(
        id="demo",
        name="Demo",
        kind="process",
        process_match="demo-worker",
        repair_adapter="local_process_restart",
    )

    def slow_repair(_target):
        time.sleep(0.35)
        return {"ok": True, "summary": "recovered"}

    monkeypatch.setattr(supervisor, "repair", slow_repair)

    async def run():
        failure = {"id": "demo", "name": "Demo", "ok": False, "error": "down"}
        await supervisor._incident_and_repair(target, failure)
        started = time.perf_counter()
        await supervisor._incident_and_repair(target, failure)
        elapsed = time.perf_counter() - started
        task = supervisor._repair_tasks.get("demo")
        assert task is not None
        assert elapsed < 0.15
        await task

    asyncio.run(run())
