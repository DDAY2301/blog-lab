from pathlib import Path

from manager.discovery import RepositoryScanner
from manager.evaluator import deterministic_health
from manager.registry import AgentRegistry


def test_registry_keeps_previous_score(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# demo\n", encoding="utf-8")

    snapshot = RepositoryScanner().scan(repo)
    health = deterministic_health(snapshot)

    state = tmp_path / "state.json"
    registry = AgentRegistry(str(state))
    first = registry.upsert(snapshot, health)

    (repo / "tests").mkdir()
    (repo / "tests" / "test_demo.py").write_text(
        "def test_ok(): assert True\n",
        encoding="utf-8",
    )

    snapshot2 = RepositoryScanner().scan(repo)
    health2 = deterministic_health(snapshot2)
    second = registry.upsert(snapshot2, health2)

    assert first.id == second.id
    assert second.previous_score == first.health_score
    assert second.health_score >= first.health_score
    assert len(registry.list()) == 1
