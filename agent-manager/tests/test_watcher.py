from manager.watcher import objective_from_failure


def test_objective_from_failure_is_bounded() -> None:
    row = {"workflowName": "CI"}
    log = "x" * 10000
    value = objective_from_failure(row, log)
    assert len(value) <= 3900
    assert "CI" in value
    assert "Do not weaken tests" in value
