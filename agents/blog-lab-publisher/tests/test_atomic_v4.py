"""Atomic V4 regression: durability, uniqueness and event fanout."""
from pathlib import Path
import json
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "agents/blog-lab-publisher"))
from services.publisher import publish_to_app
import agent


def _sample(article_id="new-v4-guide"):
    return {
        "id": article_id, "title": "Slovenski gorski vodič",
        "excerpt": "Izlet po slovenskih gorah",
        "seoDescription": "Izlet po Sloveniji",
        "content": "Slovenski vodič o naravi z neposrednimi preverljivimi viri.",
        "category": "Gore & traili", "tags": ["gore"],
        "sources": [{"url": "https://example.si/poti", "label": "Vir"}],
    }


def test_v4_article_is_atomic_and_never_edits_legacy_app(tmp_path, monkeypatch):
    app = tmp_path / "App.jsx"
    original = '''
const atomicPublishedArticles = Object.values(import.meta.glob("./articles/published/*.json", { eager: true, import: "default" }));
const starterArticles = [
  ...atomicPublishedArticles,
  { id: "old-article", title: "Stari članek" }
];
'''
    app.write_text(original, encoding="utf-8")
    publish_to_app(str(app), _sample(), "Blog Lab")
    new_path = tmp_path / "articles" / "published" / "new-v4-guide.json"
    assert new_path.exists()
    stored = json.loads(new_path.read_text(encoding="utf-8"))
    assert stored["id"] == "new-v4-guide"
    assert stored["sources"][0]["url"] == "https://example.si/poti"
    assert app.read_text(encoding="utf-8") == original
    with pytest.raises(RuntimeError, match="podvojen ID"):
        publish_to_app(str(app), _sample(), "Blog Lab")
    monkeypatch.setattr(agent, "APP", app)
    assert "slovenski gorski vodič" in agent.existing_titles()


def test_v4_rejects_path_traversal_and_old_ids(tmp_path):
    app = tmp_path / "App.jsx"
    app.write_text('const starterArticles = [\n{id: "existing-id"}];\nconst atomicPublishedArticles = Object.values(import.meta.glob("./articles/published/*.json", { eager:true }));',
                   encoding="utf-8")
    with pytest.raises(ValueError):
        publish_to_app(str(app), _sample("../escape"), "Blog Lab")
    with pytest.raises(RuntimeError, match="podvojen ID"):
        publish_to_app(str(app), _sample("existing-id"), "Blog Lab")


def test_guardian_and_selfheal_do_not_repeat_success_workflows():
    def triggers(filename):
        value = yaml.load(
            (ROOT / ".github/workflows" / filename).read_text(encoding="utf-8"),
            Loader=yaml.BaseLoader,
        )
        return value["on"]
    guardian = triggers("production-guardian.yml")
    selfheal = triggers("self-heal.yml")
    assert "workflow_run" not in guardian
    assert "push" in guardian and "pull_request" in guardian
    assert guardian["schedule"] == [{"cron": "17 */3 * * *"}]
    assert "push" not in selfheal
    assert "workflow_run" in selfheal
    assert "Blog Lab Health Check" in selfheal["workflow_run"]["workflows"]
    assert selfheal["schedule"] == [{"cron": "11 */3 * * *"}]


def test_v4_publisher_detects_and_stages_new_atomic_files():
    workflow = (ROOT / ".github/workflows/agent-blog-lab-publisher.yml").read_text(encoding="utf-8")
    assert "git status --porcelain -- src/App.jsx src/articles/published" in workflow
    assert "git add -A -- src/App.jsx src/articles/published" in workflow
