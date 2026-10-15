import sys
import time
from pathlib import Path

import psutil

from manager.db_v3 import StoreV3
from manager.managed_agents_v4 import ManagedAgentSupervisorV4, ManagedTarget


def test_safe_local_process_restart_uses_argv_and_verifies_process(tmp_path: Path):
    store = StoreV3(tmp_path / "state.db")
    config = tmp_path / "targets.json"
    config.write_text('{"version":1,"targets":[]}', encoding="utf-8")
    sup = ManagedAgentSupervisorV4(store, config)

    script = tmp_path / "agent_manager_v4_test_worker.py"
    script.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
    target = ManagedTarget(
        id="worker",
        name="Worker",
        kind="process",
        process_match=script.name,
        repair_adapter="local_process_restart",
        executable=sys.executable,
        arguments=[str(script)],
        working_dir=str(tmp_path),
    )

    result = sup._restart_local_process(target)
    assert result["ok"] is True
    assert result["stage"] == "verified_restart"
    pid = result["pid"]
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)
    except psutil.NoSuchProcess:
        pass


def test_local_process_restart_rejects_relative_executable(tmp_path: Path):
    store = StoreV3(tmp_path / "state.db")
    config = tmp_path / "targets.json"
    config.write_text('{"version":1,"targets":[]}', encoding="utf-8")
    sup = ManagedAgentSupervisorV4(store, config)

    try:
        sup.save_target(
            {
                "id": "bad",
                "name": "Bad",
                "kind": "process",
                "process_match": "bad-agent",
                "repair_adapter": "local_process_restart",
                "executable": "python.exe",
                "working_dir": str(tmp_path),
            }
        )
        assert False, "expected ValueError"
    except ValueError:
        pass
