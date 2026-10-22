"""Offline regression checks: source diversity, novelty, no editorial safety downgrade."""
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent
import autonomous_fallback as fallback
from services import source_discovery_v2 as discovery


def _story(title, url, *, provider="bing-web", fingerprint=""):
    return {
        "title": title,
        "url": url,
        "hash": fingerprint,
        "summary": "Slovenija, muzej in kulturna dediščina: preverjeno lokalno dogajanje " * 3,
        "provider": provider,
        "source_name": "Preverjen slovenski portal",
    }


def test_focus_lenses_rotate_and_cover_two_distinct_topics():
    today = date(2026, 10, 22)
    for category in ("kolesarstvo", "dediscina", "sezonsko", "gore", "gourmet"):
        q1 = discovery.focused_queries(category, day=today)
        q2 = discovery.focused_queries(category, day=date(2026, 10, 23))
        assert len(q1) == 2
        assert len(set(q1)) == 2
        assert q1 != q2
        assert all("Slovenija" in q for q in q1)
    assert discovery.focused_queries("nonexistent", day=today) == []


def test_tracking_duplicate_and_previously_published_headline_blocked():
    old = _story(
        "Novo odprtje arheološke zbirke na ptujskem gradu",
        "https://example.si/muzej/grad?utm_source=feed", fingerprint="old",
    )
    candidates = [
        _story(old["title"], "https://example.si/muzej/grad", fingerprint="renamed"),
        _story(old["title"], "https://different.si/repost", fingerprint="other"),
        _story("Povsem nova razstava v slovenskih muzejih", "https://news.si/muzej-nova", fingerprint="new"),
        _story("Povsem nova razstava v slovenskih muzejih", "https://news.si/muzej-nova?utm_campaign=launch", fingerprint="new2"),
    ]
    selected = discovery.unpublished_items(candidates, [old])
    assert len(selected) == 1
    assert selected[0]["hash"] == "new"


def test_only_unpublished_canonical_url_passes():
    original = _story("Slovenija museum original", "https://example.si/story#ref", fingerprint="old-hash")
    variants = [
        _story("A different title", "https://example.si/story?utm_source=blog"),
        _story("Another URL same fingerprint", "https://different.si/story", fingerprint="old-hash"),
        _story("An original new report", "https://good.si/new", fingerprint="new-hash"),
    ]
    assert [x["hash"] for x in discovery.unpublished_items(variants, [original])] == ["new-hash"]


def test_bounded_provider_diversity_and_independent_failure(monkeypatch):
    seen = []
    def specs(query, category):
        return [
            {"url": query + ":google", "category": category, "provider": "google-news-si"},
            {"url": query + ":bing", "category": category, "provider": "bing-web"},
        ]
    def feed(spec, *args):
        seen.append(spec["provider"])
        if spec["provider"] == "google-news-si":
            # Simulate a large aggregation that would previously occupy all slots.
            return [
                _story(f"Nov slovenski muzej: obnova dvorane {n} {spec['url']}",
                       f"https://news{n}.si/visit/{n}/{abs(hash(spec['url']))}",
                       provider="google-news-si", fingerprint=f"google-{spec['url']}-{n}")
                for n in range(14)
            ]
        return [
            _story(f"Nov ptujski grad: razstava {spec['url']}",
                   f"https://direct.si/visit/{abs(hash(spec['url']))}",
                   provider="bing-web", fingerprint=f"bing-{spec['url']}")
        ]
    monkeypatch.setattr(discovery.sources, "_topic_search_sources", specs)
    monkeypatch.setattr(discovery.sources, "fetch_feed", feed)
    monkeypatch.setattr(discovery.sources, "_duckduckgo_web", lambda *args: [
        _story(f"Slovenija arheologija: raziskave {args[0]}",
               f"https://ddg.si/story/{abs(hash(args[0]))}", provider="duckduckgo-web")
    ])
    monkeypatch.setattr(discovery.sources, "_enrich_direct_sources", lambda items, **k: items)

    found = discovery.collect_focused_sources("dediscina", max_items=14, day=date(2026, 10, 22))
    providers = {r["provider"] for r in found}
    assert len(seen) == 4  # 2 focused queries * 2 RSS indexes
    assert "google-news-si" in providers
    assert "bing-web" in providers
    assert "duckduckgo-web" in providers
    assert len(found) <= 14

    # A failed feed does not invalidate other sources or make us publish noise.
    monkeypatch.setattr(discovery.sources, "fetch_feed", lambda spec, *_: (
        (_ for _ in ()).throw(RuntimeError("503 from feed"))
        if spec["provider"] == "google-news-si" else feed(spec)
    ))
    recovered = discovery.collect_focused_sources("dediscina", max_items=12, day=date(2026, 10, 22))
    assert recovered and all(item["provider"] != "google-news-si" for item in recovered)


def test_fallback_searches_new_lens_after_used_baseline(monkeypatch, tmp_path):
    monkeypatch.setattr(fallback, "HERE", tmp_path)
    monkeypatch.setattr(fallback, "BASE", tmp_path)
    monkeypatch.setattr(fallback, "STATE", tmp_path / "data/agent-state.json")
    monkeypatch.setattr(fallback, "PROCESSED", tmp_path / "data/processed-items.json")
    monkeypatch.setattr(fallback, "APP", tmp_path / "src/App.jsx")
    (tmp_path / "config.yaml").write_text(
        "agent_name: Source V2 Test\nmaximum_outputs_per_day: 3\nmax_source_items: 30\n"
        "min_article_chars: 100\nmax_article_chars: 10000\n",
        encoding="utf-8",
    )
    old = _story("Grad Grad na Goričkem: muzejska zbirka", "https://source.si/old", fingerprint="used")
    fresh = _story("Nova muzejska zbirka dediščine v Mariboru", "https://source.si/new", fingerprint="fresh")
    fallback.atomic_json(str(fallback.PROCESSED), [old])
    monkeypatch.setattr(fallback, "enabled", lambda *_: True)
    monkeypatch.setattr(fallback, "collect_automatic_sources", lambda *_: [old])
    monkeypatch.setattr(fallback, "collect_focused_sources", lambda *_a, **_k: [fresh])
    monkeypatch.setattr(fallback, "automatic_source_usable", lambda *_a, **_k: True)
    monkeypatch.setattr(fallback, "learning_source_ok", lambda *_: True)
    monkeypatch.setattr(fallback, "rank_sources_with_learning", lambda xs, *_: xs)
    monkeypatch.setattr(fallback, "existing_titles", lambda: set())
    monkeypatch.setattr(fallback, "build_digest", lambda pool, *_: {
        "title": pool[0]["title"], "content": "Slovenska kulturna dediščina, nova razstava.",
        "sources": [{"label": "Vir", "url": pool[0]["url"]}],
    })
    monkeypatch.setattr(fallback, "prepare_article_candidate", lambda a, *_: a)
    monkeypatch.setattr(fallback, "validate", lambda *_a, **_k: [])
    monkeypatch.setattr(fallback, "validate_automatic_story", lambda *_a, **_k: [])
    monkeypatch.setattr(fallback, "optimize_commons_hero", lambda a, *_: a)
    published = []
    monkeypatch.setattr(fallback, "publish_to_app", lambda _path, a, _agent: published.append(a))
    assert fallback.run("dediscina") == 0
    assert len(published) == 1
    assert published[0]["sources"][0]["url"] == fresh["url"]
    assert old["url"] != published[0]["sources"][0]["url"]
