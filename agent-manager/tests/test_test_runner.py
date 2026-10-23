import json
from pathlib import Path

from manager.test_runner import detect_test_commands


def test_detects_agent_manager_suite(tmp_path: Path) -> None:
    (tmp_path / "agent-manager").mkdir()
    (tmp_path / "agent-manager" / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    commands = detect_test_commands(
        tmp_path,
        ["agent-manager/manager/service.py"],
    )

    names = [item.name for item in commands]
    assert "agent-manager tests" in names
    assert "agent-manager FastAPI smoke" in names


def test_detects_npm_build(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"build": "vite build"}}),
        encoding="utf-8",
    )

    commands = detect_test_commands(tmp_path, ["src/App.jsx"])
    assert any(item.name == "npm build" for item in commands)
