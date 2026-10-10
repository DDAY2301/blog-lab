import asyncio
import time
from pathlib import Path

from manager.db_v3 import StoreV3
from manager.maintenance_v4 import MaintenanceLoopV4
from manager.settings_v3 import SettingsV3


def test_slow_ai_triage_does_not_block_health_cycle(tmp_path: Path, monkeypatch):
    settings = SettingsV3(db_path=tmp_path / "state.db")
    store = StoreV3(settings.db_path)
    loop = MaintenanceLoopV4(settings, store)

    async def checks():
        return [{"id": "demo", "name": "Demo", "ok": False, "error": "down"}]

    async def provider_status():
        return {"ollama": {"ok": True}}

    async def slow_triage(state):
        await asyncio.sleep(5)
        return {"answers": {}}

    monkeypatch.setattr(loop.supervisor, "check_all", checks)
    monkeypatch.setattr(loop.ai, "status", provider_status)
    monkeypatch.setattr(loop.ai, "triage", slow_triage)

    async def run():
        started = time.perf_counter()
        result = await loop.cycle()
        elapsed = time.perf_counter() - started
        loop.stop()
        await asyncio.sleep(0)
        return result, elapsed

    result, elapsed = asyncio.run(run())
    assert elapsed < 1.0
    assert result["ai_jobs_pending"] >= 1
