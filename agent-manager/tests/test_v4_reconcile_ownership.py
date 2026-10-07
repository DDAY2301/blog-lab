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


def test_project_visibility_requires_exact_root_and_server_command(tmp_path: Path):
    root = tmp_path / "Project-Visibility"
    root.mkdir()
    lookalike = tmp_path / "Project-Visibility-old"
    lookalike.mkdir()

    good = FakeProcess(root, ["python", "-m", "uvicorn", "api.server:app", "--port", "8000"])
    wrong_root = FakeProcess(lookalike, ["python", "-m", "uvicorn", "api.server:app", "--port", "8000"])
    wrong_command = FakeProcess(root, ["python", "-m", "http.server", "8000"])

    assert reconcile_v4._is_owned_project_visibility_process(good, root) is True
    assert reconcile_v4._is_owned_project_visibility_process(wrong_root, root) is False
    assert reconcile_v4._is_owned_project_visibility_process(wrong_command, root) is False
