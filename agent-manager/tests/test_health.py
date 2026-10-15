from pathlib import Path

from manager.discovery import RepositoryScanner
from manager.evaluator import deterministic_health


def test_repo_with_tests_and_workflow_scores_higher(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# demo\n", encoding="utf-8")
    (tmp_path / "agents" / "demo").mkdir(parents=True)
    (tmp_path / "agents" / "demo" / "agent.py").write_text(
        "def healthcheck(): return True\n",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_demo.py").write_text(
        "def test_ok(): assert True\n",
        encoding="utf-8",
    )
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\n",
        encoding="utf-8",
    )
    (tmp_path / "prompt.md").write_text("You are a test agent.", encoding="utf-8")

    snapshot = RepositoryScanner().scan(tmp_path)
    report = deterministic_health(snapshot)

    assert report.score >= 85
    assert report.status == "healthy"


def test_empty_repo_is_not_healthy(tmp_path: Path) -> None:
    snapshot = RepositoryScanner().scan(tmp_path)
    report = deterministic_health(snapshot)

    assert report.score < 70
    assert report.status in {"degraded", "critical"}
