"""Regression checks for Blog Lab's bounded workflow-trigger budget."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def triggers(path: str) -> dict:
    document = yaml.load((ROOT / path).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    return document["on"]


def test_article_learning_is_periodic_not_recursive():
    on = triggers(".github/workflows/publisher-learning.yml")
    assert set(on) == {"schedule", "workflow_dispatch"}
    assert on["schedule"] == [{"cron": "13 */6 * * *"}]


def test_publisher_guardian_has_bounded_hourly_catchup():
    on = triggers(".github/workflows/publisher-guardian.yml")
    assert set(on) == {"schedule", "workflow_dispatch"}
    assert on["schedule"] == [{"cron": "47 * * * *"}]


def test_normal_publisher_heartbeat_unchanged():
    on = triggers(".github/workflows/agent-blog-lab-publisher.yml")
    assert on["schedule"] == [{"cron": "7,22,37,52 * * * *"}]
