"""Regression tests for autonomous publisher source freshness and visual truthfulness."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent
import autonomous_fallback as fallback
from services.media_library import _location_filter, commons_image_matches_topic
from services.validator import validate


def _source(title, path, fingerprint):
    return {
        "title": title,
        "summary": "Slovenska dediščina: preverljiva zgodovina kraja in muzejske zbirke.",
        "url": f"https://fresh-sources.example.si/{path}",
        "hash": fingerprint,
        "source_name": "Lokalni vir",
        "provider": "google-news-si",
    }


def test_only_fresh_normalized_urls_eligible_for_fallback(monkeypatch):
    monkeypatch.setattr(fallback, "learning_source_ok", lambda *_: True)
    monkeypatch.setattr(fallback, "rank_sources_with_learning", lambda x, *_: x)
    used = _source("Grad Grad na Goričkem odpira razstavo", "grad-grad", "old")
    fresh = _source("Ptuj živi skozi muzejske zbirke", "ptuj", "fresh")
    processed = [{"url": used["url"] + "?utm_source=feed", "hash": "previous-hash"}]
    pools = fallback._fresh_story_pools([used, fresh], processed, "dediscina")
    assert pools
    assert all(used["url"] not in [s["url"] for s in pool] for pool in pools)
    assert pools[0][0]["url"] == fresh["url"]


def test_never_recycle_sources_when_all_are_used(monkeypatch):
    monkeypatch.setattr(fallback, "learning_source_ok", lambda *_: True)
    used = _source("Grad Grad na Goričkem odpira razstavo", "grad-grad", "old")
    assert fallback._fresh_story_pools([used], [{"url": used["url"]}], "dediscina") == []


def test_distinct_castles_are_separate_story_attempts(monkeypatch):
    monkeypatch.setattr(fallback, "learning_source_ok", lambda *_: True)
    monkeypatch.setattr(fallback, "rank_sources_with_learning", lambda x, *_: x)
    a = _source("Grad Grad na Goričkem predstavlja zbirko", "grad-grad", "a")
    b = _source("Ptujski grad predstavlja muzejske dogodke", "ptuj", "b")
    pools = fallback._fresh_story_pools([a, b], [], "dediscina")
    assert len(pools) == 2
    assert [pool[0]["url"] for pool in pools] == [a["url"], b["url"]]


def test_run_retries_a_second_fresh_story_before_publication(monkeypatch, tmp_path):
    monkeypatch.setattr(fallback, "HERE", tmp_path)
    monkeypatch.setattr(fallback, "BASE", tmp_path)
    monkeypatch.setattr(fallback, "STATE", tmp_path / "data/state.json")
    monkeypatch.setattr(fallback, "PROCESSED", tmp_path / "data/processed.json")
    monkeypatch.setattr(fallback, "APP", tmp_path / "src/App.jsx")
    (tmp_path / "config.yaml").write_text(
        "agent_name: Test Agent\nmaximum_outputs_per_day: 3\nmin_article_chars: 100\nmax_article_chars: 10000\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(fallback, "enabled", lambda *_: True)
    monkeypatch.setattr(fallback, "existing_titles", lambda: set())
    monkeypatch.setattr(fallback, "learning_source_ok", lambda *_: True)
    monkeypatch.setattr(fallback, "rank_sources_with_learning", lambda x, *_: x)
    first = _source("Grad Grad na Goričkem odpira razstavo", "grad-grad", "a")
    second = _source("Ptujski grad razkriva zgodovino", "ptuj", "b")
    monkeypatch.setattr(fallback, "collect_automatic_sources", lambda *_: [first, second])

    def make_candidate(pool, _category):
        lead = pool[0]
        return {
            "title": lead["title"],
            "excerpt": "Razstava lokalne dediščine.",
            "seoDescription": "Preverljiva dediščina.",
            "content": "Preverjena zgodba z neposredno referenco.",
            "sources": [{"label": "Vir", "url": lead["url"]}],
            "source_urls": [lead["url"]],
            "tags": ["dediščina"],
        }

    monkeypatch.setattr(fallback, "build_digest", make_candidate)
    monkeypatch.setattr(fallback, "prepare_article_candidate", lambda article, *_: {**article, "heroImage": {"url": "https://example.com/verified.jpg"}})
    monkeypatch.setattr(fallback, "validate", lambda a, *_: ["uredniski_hold"] if a["title"] == first["title"] else [])
    monkeypatch.setattr(fallback, "validate_automatic_story", lambda *_: [])
    monkeypatch.setattr(fallback, "optimize_commons_hero", lambda article, *_: article)
    published = []
    monkeypatch.setattr(fallback, "publish_to_app", lambda _app, article, _name: published.append(article))
    assert fallback.run("dediscina", scheduled_slot="test-slot") == 0
    assert [a["title"] for a in published] == [second["title"]]
    state = fallback.load_json(str(fallback.STATE), {})
    assert state["scheduled_posts_today"] == 1
    assert not state["last_error"]


def test_commons_image_requires_matching_geographic_metadata():
    article_title = "Grad Grad na Goričkem: slovenska dediščina"
    assert "gorick" in _location_filter(article_title)
    wrong_image = {
        "alt": "Tuštanj Castle memorial plaque",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Tustanj_Castle.jpg",
        "caption": "Photo / Wikimedia Commons / CC BY-SA",
    }
    correct_image = {
        "alt": "Goričko castle, Slovenia",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Grad_Grad_Goricko.jpg",
        "caption": "Photo / Wikimedia Commons / CC BY-SA",
    }
    assert not commons_image_matches_topic(article_title, wrong_image)
    assert commons_image_matches_topic(article_title, correct_image)


def test_automatic_preparation_replaces_wrong_castle_photo(monkeypatch):
    wrong = {
        "url": "https://example.com/tustanj.jpg",
        "alt": "Tuštanj castle, Slovenia",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Tustanj.jpg",
        "caption": "Wikimedia Commons · CC BY-SA",
    }
    good = {
        "url": "https://example.com/goricko.jpg",
        "alt": "Goričko castle, Slovenia",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Goricko.jpg",
        "caption": "Wikimedia Commons · CC BY-SA",
    }
    monkeypatch.setattr(agent, "commons_image_for", lambda *_: good)
    prepared = agent.prepare_article_candidate(
        {"title": "Grad Grad na Goričkem", "heroImage": wrong, "gallery": [wrong]},
        [],
        "",
        "Dediščina",
    )
    assert prepared["heroImage"]["url"] == good["url"]
    assert prepared["gallery"] == []


def test_validation_detects_published_url_even_with_tracking_variants():
    url = "https://localnews.example.si/grad-grad"
    article = {
        "title": "Novi podatki",
        "excerpt": "Kratek povzetek",
        "seoDescription": "Opis",
        "content": "Preverljiva vsebina. " * 40,
        "category": "Novice",
        "tags": ["dediščina"],
        "sources": [{"label": "Lokalni vir", "url": url + "?utm_campaign=autumn"}],
    }
    assert "ze_uporabljen_vir" in validate(
        article, 100, 10000, set(), {url}, {url}
    )
