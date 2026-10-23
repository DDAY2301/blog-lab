from pathlib import Path

from manager import reconcile_v4


class FakeProcess:
    def __init__(self, cwd: Path, cmdline: list[str]):
        self._cwd = cwd
        self._cmdline = cmdline

    def cwd(self):
        return str(self._cwd)

    def cmdline(self):
        return self._cmdline


def test_manager_process_requires_exact_root_component():
    root = reconcile_v4.ROOT
    lookalike = root.parent / (root.name + "-old")
    assert reconcile_v4._is_owned_manager_process(FakeProcess(lookalike, ["python", "run.py"])) is False
    assert reconcile_v4._is_owned_manager_process(FakeProcess(root, ["python", "run.py"])) is True
