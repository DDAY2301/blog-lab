from pathlib import Path
from types import SimpleNamespace

from manager import reconcile_v4


class FakeProcess:
    def __init__(self, cwd: Path, command: list[str]):
        self._cwd = cwd
        self._command = command

    def cwd(self):
        return str(self._cwd)

    def cmdline(self):
        return self._command


def test_remote_process_requires_exact_root_and_known_service():
    root = reconcile_v4.ROOT
    remote_command = ["python.exe", "-m", "uvicorn", "manager.remote_v4:app",
                      "--host", "127.0.0.1", "--port", "8788"]
    assert reconcile_v4._is_owned_fleet_remote_process(FakeProcess(root, remote_command))
    assert not reconcile_v4._is_owned_fleet_remote_process(FakeProcess(
        root.parent / (root.name + "-lookalike"), remote_command))
    assert not reconcile_v4._is_owned_fleet_remote_process(FakeProcess(
        root, ["python.exe", "another_app.py"]))
    assert not reconcile_v4._is_owned_fleet_remote_process(FakeProcess(
        root, ["python.exe", "-m", "uvicorn", "unrelated:app", "--port", "8788"]))


def test_remote_reconciler_refuses_to_stop_foreign_port_owner(monkeypatch):
    stopped = []
    foreign = FakeProcess(Path("/unrelated"), ["python.exe", "-m", "uvicorn",
                                               "unrelated:app", "--port", "8788"])
    foreign.terminate = lambda: stopped.append("foreign")
    conn = SimpleNamespace(
        laddr=SimpleNamespace(port=8788),
        status=reconcile_v4.psutil.CONN_LISTEN,
        pid=123,
    )
    monkeypatch.setattr(reconcile_v4.psutil, "net_connections", lambda kind: [conn])
    monkeypatch.setattr(reconcile_v4.psutil, "Process", lambda pid: foreign)
    result, msg = reconcile_v4.stop_remote_listener()
    assert result is False
    assert "unrelated" in msg
    assert stopped == []
