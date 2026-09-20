from pathlib import Path
import sys, tempfile
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from services.publisher import slugify,publish_to_app
from services.validator import validate
def test_slugify(): assert slugify("Čudovita Šola Življenja")=="cudovita-sola-zivljenja"
def test_validator_rejects_short():
    a={"title":"T","excerpt":"E","seoDescription":"S","content":"premalo","category":"Novice","tags":["x"]}; assert "prekratek" in validate(a,100,1000,set(),set())
def test_publisher_inserts():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"App.jsx"; p.write_text("const starterArticles = [\n];",encoding="utf-8"); a={"id":"test-1","title":"Test","excerpt":"E","seoDescription":"S","content":"## Viri\nhttps://example.com","category":"Novice"}; publish_to_app(str(p),a,"Agent"); assert '"test-1"' in p.read_text(encoding="utf-8")


def test_topic_query_variants():
    from services.sources import _topic_queries
    queries = _topic_queries("Objavi članek o današnjih dogajanjih na cesti in kam priporočaš vikend izlet")
    assert queries
    assert any("cesti" in q.lower() for q in queries)
    assert any("vikend" in q.lower() and "izlet" in q.lower() for q in queries)
    assert len(queries) == len({q.lower() for q in queries})


def test_operator_media_parses_uploaded_images_and_video():
    from agent import operator_media
    image_url = "https://dday2301.github.io/blog-lab/media/uploads/20260918-test-photo.webp"
    video_url = "https://youtu.be/abc123"
    images, video = operator_media(
        f"Objavi članek z [naložena slika: {image_url}] in video {video_url}"
    )
    assert [item["url"] for item in images] == [image_url]
    assert video["url"] == video_url


def test_operator_media_handles_query_string_extensions():
    from agent import operator_media
    image_url = "https://example.com/photo.jpg?size=large"
    video_url = "https://example.com/clip.mp4?token=test"
    images, video = operator_media(f"{image_url} {video_url}")
    assert images[0]["url"] == image_url
    assert video["url"] == video_url


def test_operator_media_honors_explicit_hero_marker():
    from agent import operator_media
    gallery_url = "https://example.com/gallery.webp"
    hero_url = "https://example.com/hero.jpg"
    images, _ = operator_media(
        f"[naložena slika: {gallery_url}]\n[hero slika: {hero_url}]"
    )
    assert [item["url"] for item in images] == [hero_url, gallery_url]


def test_media_policy_uploaded_photo_overrides_generated_hero():
    from agent import apply_media_policy
    uploaded = "https://dday2301.github.io/blog-lab/media/uploads/operator.webp"
    article = {
        "heroImage": {"url": "https://example.com/ai.jpg"},
        "gallery": [{"url": "https://example.com/gallery.jpg"}],
        "video": None,
    }
    result = apply_media_policy(
        article,
        [{"image_url": "https://example.com/source.jpg", "title": "Vir", "source_name": "Test"}],
        f"[hero slika: {uploaded}]",
    )
    assert result["heroImage"]["url"] == uploaded
    gallery_urls = [item["url"] for item in result["gallery"]]
    assert "https://example.com/gallery.jpg" in gallery_urls
    assert "https://example.com/source.jpg" in gallery_urls


def test_media_policy_uses_verified_source_media_when_article_has_none():
    from agent import apply_media_policy
    article = {"heroImage": None, "gallery": [], "video": None}
    sources = [
        {
            "image_url": "https://example.com/one.jpg",
            "video_url": "",
            "title": "Prva zgodba",
            "source_name": "Vir A",
        },
        {
            "image_url": "https://example.com/two.webp",
            "video_url": "https://example.com/clip.mp4",
            "title": "Druga zgodba",
            "source_name": "Vir B",
        },
    ]
    result = apply_media_policy(article, sources)
    assert result["heroImage"]["url"] == "https://example.com/one.jpg"
    assert [item["url"] for item in result["gallery"]] == ["https://example.com/two.webp"]
    assert result["video"]["url"] == "https://example.com/clip.mp4"


def test_topic_query_ignores_structured_media_markers():
    from services.sources import _topic_queries
    queries = _topic_queries(
        "Objavi članek o Ljubljani [hero slika: https://example.com/hero.jpg] "
        "[naložena slika: https://example.com/extra.webp]"
    )
    joined = " ".join(queries).lower()
    assert "hero slika" not in joined
    assert "naložena slika" not in joined


def test_operator_media_preserves_uploaded_caption():
    from agent import operator_media
    hero = "https://example.com/hero.jpg"
    gallery = "https://example.com/gallery.webp"
    images, _ = operator_media(
        f"[naložena slika: {gallery} | Pogled z gradu]\n"
        f"[hero slika: {hero} | Naslovna fotografija]"
    )
    assert images[0]["url"] == hero
    assert images[0]["caption"] == "Naslovna fotografija"
    assert images[1]["url"] == gallery
    assert images[1]["caption"] == "Pogled z gradu"


def test_collect_topic_falls_back_to_english_google_news(monkeypatch):
    from services import sources

    calls = []

    def fake_fetch(source, *args, **kwargs):
        calls.append(source["url"])
        if "hl=en-US" in source["url"]:
            return [{
                "source_name": source["name"],
                "category": "aktualno",
                "title": "International topic result",
                "url": "https://example.com/story",
                "summary": "Verified summary",
                "published": "",
                "image_url": "",
                "video_url": "",
                "hash": "english-result",
            }]
        return []

    monkeypatch.setattr(sources, "fetch_feed", fake_fetch)
    monkeypatch.setattr(sources, "_gdelt_news", lambda *a, **k: [])
    monkeypatch.setattr(sources, "_duckduckgo_web", lambda *a, **k: [])
    items = sources.collect_topic("Objavi članek o orbitalni energiji", "aktualno", 10)

    assert items and items[0]["url"] == "https://example.com/story"
    assert any("hl=sl" in url for url in calls)
    assert any("hl=en-US" in url for url in calls)


def test_topic_queries_drop_editorial_filler_words():
    from services.sources import _topic_queries

    queries = _topic_queries(
        "Objavi profesionalen daljši članek o orbitalni energiji in satelitih"
    )
    joined = " | ".join(queries).lower()

    # Raw command may remain as one candidate, but broadened keyword candidates
    # must also include the topical words without editorial filler.
    assert any(
        "orbitalni" in query.lower()
        and "energiji" in query.lower()
        and "profesionalen" not in query.lower()
        and "dalj" not in query.lower()
        for query in queries
    )


def test_collect_topic_uses_multiple_world_providers(monkeypatch):
    from services import sources

    feed_calls = []
    gdelt_calls = []

    def fake_feed(source, *args, **kwargs):
        feed_calls.append(source["url"])
        name = source["name"]
        if "Google News SI" in name:
            return [{
                "source_name": "RTV Slovenija",
                "category": "aktualno",
                "title": "Slovenski rezultat",
                "url": "https://rtvslo.si/test-1",
                "summary": "Slovenski povzetek",
                "published": "",
                "image_url": "",
                "video_url": "",
                "hash": "si-1",
            }]
        if "Google News EN" in name:
            return [{
                "source_name": "Reuters",
                "category": "aktualno",
                "title": "Global result",
                "url": "https://reuters.com/test-2",
                "summary": "Global summary",
                "published": "",
                "image_url": "",
                "video_url": "",
                "hash": "en-2",
            }]
        if "Bing News" in name:
            return [{
                "source_name": "BBC",
                "category": "aktualno",
                "title": "Bing result",
                "url": "https://bbc.com/test-3",
                "summary": "Bing summary",
                "published": "",
                "image_url": "",
                "video_url": "",
                "hash": "bing-3",
            }]
        return []

    def fake_gdelt(query_text, category, max_items):
        gdelt_calls.append(query_text)
        return [{
            "source_name": "example.org",
            "category": category,
            "title": "GDELT result",
            "url": "https://example.org/test-4",
            "summary": "GDELT summary",
            "published": "",
            "image_url": "",
            "video_url": "",
            "hash": "gdelt-4",
        }]

    monkeypatch.setattr(sources, "fetch_feed", fake_feed)
    monkeypatch.setattr(sources, "_gdelt_news", fake_gdelt)
    monkeypatch.setattr(sources, "_duckduckgo_web", lambda *a, **k: [])

    items = sources.collect_topic("Objavi članek o globalnem energetskem trgu", "aktualno", 30)
    names = {item["source_name"] for item in items}

    assert "RTV Slovenija" in names
    assert "Reuters" in names
    assert any("news.google.com" in url for url in feed_calls)
    assert any("bing.com/news/search" in url for url in feed_calls)
    assert gdelt_calls


def test_dedupe_diverse_limits_single_source():
    from services.sources import _dedupe_diverse

    items = []
    for index in range(8):
        items.append({
            "source_name": "Same Outlet",
            "category": "aktualno",
            "title": f"Story {index}",
            "url": f"https://same.example/story-{index}",
            "summary": "",
            "published": "",
            "image_url": "",
            "video_url": "",
            "hash": f"same-{index}",
        })
    items.append({
        "source_name": "Other Outlet",
        "category": "aktualno",
        "title": "Other story",
        "url": "https://other.example/story",
        "summary": "",
        "published": "",
        "image_url": "",
        "video_url": "",
        "hash": "other-1",
    })

    out = _dedupe_diverse(items, 20, per_source=3)
    assert sum(1 for item in out if item["source_name"] == "Same Outlet") == 3
    assert any(item["source_name"] == "Other Outlet" for item in out)


def test_gdelt_rejects_non_https_results(monkeypatch):
    from services import sources

    class FakeResponse:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self, *args):
            return json.dumps({
                "articles": [
                    {
                        "title": "HTTPS result",
                        "url": "https://good.example/story",
                        "domain": "good.example",
                        "seendate": "20260919T120000Z",
                    },
                    {
                        "title": "HTTP result",
                        "url": "http://bad.example/story",
                        "domain": "bad.example",
                        "seendate": "20260919T120000Z",
                    },
                ]
            }).encode("utf-8")

    import json
    monkeypatch.setattr(sources, "urlopen", lambda *a, **k: FakeResponse())
    items = sources._gdelt_news("test", "aktualno", 10)
    assert [item["url"] for item in items] == ["https://good.example/story"]


def test_topic_core_separates_subject_from_writing_instruction():
    from services.sources import _topic_core, _topic_queries

    command = (
        "objavi članek o dogajanju v ljubljanskem nočnem življenju "
        "in bo več teksta v samem članku"
    )
    core = _topic_core(command)
    queries = _topic_queries(command)

    assert core == "dogajanju v ljubljanskem nočnem življenju"
    joined = " | ".join(queries).lower()
    assert "več teksta" not in joined
    assert "samem članku" not in joined
    assert "ljubljana" in joined or "ljubljanskem" in joined


def test_bing_web_provider_uses_general_search_rss(monkeypatch):
    from services import sources

    captured = {}

    def fake_fetch(source, *args, **kwargs):
        captured["url"] = source["url"]
        captured["name"] = source["name"]
        return []

    monkeypatch.setattr(sources, "fetch_feed", fake_fetch)
    sources._bing_web("Ljubljana nočno življenje", "aktualno", 10)

    assert "bing.com/search" in captured["url"]
    assert "/news/search" not in captured["url"]
    assert "format=rss" in captured["url"]
    assert captured["name"].startswith("Bing Web")


def test_world_search_calls_general_web_and_gdelt(monkeypatch):
    from services import sources

    providers = []

    def fake_feed(source, *args, **kwargs):
        if "Bing Web" in source["name"]:
            providers.append("bing_web")
            return [{
                "source_name": "Visit Ljubljana",
                "category": "aktualno",
                "title": "Ljubljana nightlife guide",
                "url": "https://www.visitljubljana.com/test-nightlife",
                "summary": "Guide",
                "published": "",
                "image_url": "",
                "video_url": "",
                "hash": "web-guide",
            }]
        if "Google News" in source["name"]:
            providers.append("google")
        elif "Bing News" in source["name"]:
            providers.append("bing_news")
        return []

    def fake_gdelt(*args, **kwargs):
        providers.append("gdelt")
        return []

    monkeypatch.setattr(sources, "fetch_feed", fake_feed)
    monkeypatch.setattr(sources, "_gdelt_news", fake_gdelt)
    monkeypatch.setattr(sources, "_duckduckgo_web", lambda *a, **k: [])

    items = sources.collect_topic(
        "objavi članek o dogajanju v ljubljanskem nočnem življenju in bo več teksta v samem članku",
        "aktualno",
        30,
    )

    assert items
    assert items[0]["source_name"] == "Visit Ljubljana"
    assert "bing_web" in providers
    assert "gdelt" in providers


def test_topic_search_sources_cover_multiple_web_indexes():
    from services.sources import _topic_search_sources

    sources = _topic_search_sources("renewable energy Slovenia", "aktualno")
    providers = {item.get("provider") for item in sources}
    urls = [item["url"] for item in sources]

    assert {"google-news-si", "google-news-global", "bing-news", "bing-web"} <= providers
    assert any("news.google.com/rss/search" in url for url in urls)
    assert any("bing.com/news/search" in url and "format=rss" in url for url in urls)
    assert any("bing.com/search" in url and "format=rss" in url for url in urls)


def test_collect_topic_continues_when_one_provider_fails(monkeypatch):
    from services import sources

    calls = []

    def fake_fetch(source, *args, **kwargs):
        calls.append(source.get("provider"))
        if source.get("provider") == "google-news-si":
            raise RuntimeError("temporary provider outage")
        if source.get("provider") == "bing-web":
            return [{
                "source_name": source["name"],
                "category": "aktualno",
                "title": "Web result",
                "url": "https://example.org/research",
                "summary": "Public web source",
                "published": "",
                "image_url": "",
                "video_url": "",
                "hash": "bing-web-result",
            }]
        return []

    monkeypatch.setattr(sources, "fetch_feed", fake_fetch)
    monkeypatch.setattr(sources, "_gdelt_news", lambda *a, **k: [])
    monkeypatch.setattr(sources, "_duckduckgo_web", lambda *a, **k: [])
    items = sources.collect_topic("specialized research topic", "aktualno", 10)

    assert items and items[0]["url"] == "https://example.org/research"
    assert "google-news-si" in calls
    assert "bing-web" in calls


def test_direct_web_source_enrichment_reads_target_page(monkeypatch):
    from services import sources

    html = b"""
    <html><head>
      <title>Nightlife in Ljubljana</title>
      <meta name="description" content="Independent guide to clubs, venues and evening events in Ljubljana.">
      <meta property="og:image" content="https://example.com/night.jpg">
    </head><body><article>
      Ljubljana has several nightlife districts, live music venues and late-night cultural events.
      This paragraph provides enough directly fetched page text for the publisher evidence pool.
      Visitors should verify individual venue schedules before attending because programmes change.
    </article></body></html>
    """

    class Headers:
        def get(self, key, default=""):
            return "text/html; charset=utf-8" if key.lower() == "content-type" else default

    class Response:
        status = 200
        headers = Headers()
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, *args): return html
        def geturl(self): return "https://example.com/nightlife"

    monkeypatch.setattr(sources, "urlopen", lambda *a, **k: Response())
    item = {
        "source_name": "Bing Web – test",
        "provider": "bing-web",
        "category": "aktualno",
        "title": "Search result",
        "url": "https://example.com/nightlife",
        "summary": "Short snippet",
        "published": "",
        "image_url": "",
        "video_url": "",
        "hash": "before",
    }

    enriched, ok = sources._enrich_direct_item(item)

    assert ok is True
    assert enriched["verified_direct"] is True
    assert enriched["url"] == "https://example.com/nightlife"
    assert enriched["title"] == "Nightlife in Ljubljana"
    assert "directly fetched page text" in enriched["summary"]
    assert enriched["image_url"] == "https://example.com/night.jpg"
    assert enriched["source_name"] == "example.com"


def test_direct_enrichment_skips_news_aggregator_links():
    from services.sources import _direct_candidate

    assert _direct_candidate({
        "provider": "google-news-si",
        "url": "https://news.google.com/rss/articles/test",
    }) is False
    assert _direct_candidate({
        "provider": "bing-web",
        "url": "https://example.org/article",
    }) is True


def test_rank_topic_items_prefers_relevant_direct_evidence():
    from services.sources import rank_topic_items

    items = [
        {
            "title": "Generic travel guide",
            "summary": "A long unrelated guide about beaches and museums. " * 20,
            "source_name": "generic.example",
            "url": "https://generic.example/guide",
            "verified_direct": True,
        },
        {
            "title": "Ljubljana nočno življenje",
            "summary": "Pregled klubov, večernih dogodkov in nočnega življenja v Ljubljani.",
            "source_name": "local.example",
            "url": "https://local.example/nightlife",
            "verified_direct": True,
        },
        {
            "title": "Ljubljana dogodki",
            "summary": "Kratek koledar večernih dogodkov v Ljubljani.",
            "source_name": "calendar.example",
            "url": "https://calendar.example/events",
            "verified_direct": False,
        },
    ]

    ranked = rank_topic_items("dogajanje v ljubljanskem nočnem življenju", items)

    assert ranked[0]["url"] == "https://local.example/nightlife"
    assert ranked[-1]["url"] == "https://generic.example/guide"


def test_manual_editor_system_prompt_replaces_generic_skip_rule():
    from agent import manual_editor_system_prompt

    base = (
        "Facts only.\n"
        "- Če material ne zadostuje za kakovosten samostojen članek, vrni `skip=true`.\n"
        "Never invent facts."
    )
    prompt = manual_editor_system_prompt(
        base,
        "dogajanje v ljubljanskem nočnem življenju",
        12,
    )

    assert "Če material ne zadostuje za kakovosten samostojen članek" not in prompt
    assert "Prednost avtorizirane ročne uredniške zahteve" in prompt
    assert "Če vsaj trije od prvih virov" in prompt
    assert "12 preverjenih spletnih virov" in prompt
    assert "ničesar ne ugibaj" in prompt


def test_duckduckgo_web_parses_direct_https_results(monkeypatch):
    from services import sources

    html = b"""
    <html><body>
      <div class="result results_links results_links_deep web-result">
        <h2 class="result__title">
          <a rel="nofollow" class="result__a"
             href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.org%2Fresearch%3Fa%3D1">
             Independent research page
          </a>
        </h2>
        <a class="result__snippet">A substantive public-web search snippet about the requested topic.</a>
      </div>
    </body></html>
    """

    class Response:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, *args): return html

    monkeypatch.setattr(sources, "urlopen", lambda *a, **k: Response())

    items = sources._duckduckgo_web("specialized research topic", "aktualno", 10)

    assert len(items) == 1
    assert items[0]["url"] == "https://example.org/research?a=1"
    assert items[0]["provider"] == "duckduckgo-web"
    assert items[0]["source_name"] == "example.org"
    assert "substantive public-web search snippet" in items[0]["summary"].lower()


def test_collect_topic_includes_duckduckgo_general_web(monkeypatch):
    from services import sources

    monkeypatch.setattr(sources, "fetch_feed", lambda *a, **k: [])
    monkeypatch.setattr(sources, "_gdelt_news", lambda *a, **k: [])
    monkeypatch.setattr(
        sources,
        "_duckduckgo_web",
        lambda query, category, limit: [{
            "source_name": "example.net",
            "category": category,
            "title": "General web result",
            "url": "https://example.net/topic",
            "summary": "Independent result from a general web index.",
            "published": "",
            "image_url": "",
            "video_url": "",
            "hash": "ddg-general",
            "provider": "duckduckgo-web",
        }],
    )

    items = sources.collect_topic("very niche topic", "aktualno", 10)

    assert items
    assert items[0]["url"] == "https://example.net/topic"
    assert items[0]["provider"] == "duckduckgo-web"


def test_direct_enrichment_accepts_duckduckgo_results():
    from services.sources import _direct_candidate

    assert _direct_candidate({
        "provider": "duckduckgo-web",
        "url": "https://example.org/article",
    }) is True


def test_collect_topic_submits_web_indexes_in_parallel(monkeypatch):
    from services import sources
    import threading

    entered = []
    gate = threading.Event()

    def blocking_feed(source, *args, **kwargs):
        entered.append(source.get("provider"))
        if len(entered) >= 2:
            gate.set()
        gate.wait(timeout=1)
        return []

    def blocking_gdelt(*args, **kwargs):
        entered.append("gdelt")
        gate.set()
        return []

    monkeypatch.setattr(sources, "fetch_feed", blocking_feed)
    monkeypatch.setattr(sources, "_gdelt_news", blocking_gdelt)
    monkeypatch.setattr(sources, "_duckduckgo_web", lambda *a, **k: [])

    sources.collect_topic("parallel search topic", "aktualno", 5)

    assert "google-news-si" in entered
    assert "google-news-global" in entered
    assert "gdelt" in entered


def test_automatic_sources_merge_feed_and_webwide(monkeypatch):
    import agent

    feed_item = {
        "url": "https://news.example/feed",
        "hash": "feed-1",
        "title": "Slovenska nogometna liga prinaša derbi",
        "summary": "Nogometna tekma bo ta konec tedna, kluba pa sta predstavila priprave in pričakovanja.",
        "provider": "",
    }
    web_item = {
        "url": "https://web.example/story",
        "hash": "web-1",
        "title": "Tennis tournament reaches the final",
        "summary": "The tennis tournament reaches its final after two competitive semifinal matches and strong performances.",
        "provider": "bing-news",
    }
    calls = []
    monkeypatch.setattr(agent, "collect", lambda *a, **k: [feed_item])
    monkeypatch.setattr(
        agent,
        "collect_topic",
        lambda query, category, limit: calls.append((query, category, limit)) or [web_item, feed_item],
    )

    items = agent.collect_automatic_sources(
        {"input_sources": [], "max_source_items": 30},
        "sport",
    )

    assert [item["url"] for item in items] == [
        "https://news.example/feed",
        "https://web.example/story",
    ]
    assert calls and calls[0][0] == "Slovenija šport danes"


def test_qa_repair_prompt_contains_validation_requirements():
    from agent import qa_repair_task

    prompt = qa_repair_task("Osnovna naloga.", ["prekratek", "brez_virov"], 1200, 10000)

    assert "prekratek" in prompt
    assert "brez_virov" in prompt
    assert "1200" in prompt and "10000" in prompt
    assert "HTTPS URL-je iz podanih virov" in prompt


def test_fallback_digest_can_pass_standard_qa_with_verified_sources():
    from services.fallback_writer import build_digest

    items = []
    for index in range(5):
        items.append({
            "source_name": f"Vir {index}",
            "category": "sport",
            "title": f"Športna zgodba {index}",
            "url": f"https://example.com/sport-{index}",
            "summary": (
                f"Preverjen vir {index} opisuje športni dogodek, njegov potek in odzive udeležencev. "
                f"Za zgodbo {index} navaja tudi okoliščine, ki pomagajo razumeti dogajanje. "
                f"Dodatna preverljiva informacija {index} dopolnjuje kontekst brez ugibanja."
            ),
            "published": "2026-09-20",
            "image_url": "",
            "video_url": "",
            "hash": f"sport-{index}",
        })

    article = build_digest(items, "sport", max_items=5)
    errors = validate(article, 1200, 10000, set(), set())

    assert errors == []


def test_automatic_source_rejects_non_latin_unrelated_sport_result():
    from agent import automatic_source_usable

    item = {
        "title": "월드뉴스 | KBS 뉴스",
        "summary": "무단 전재, 재배포 및 이용 금지.",
        "url": "https://news.kbs.co.kr/news/pc/program/program.do?bcd=0026",
        "provider": "bing-web",
    }
    assert automatic_source_usable(item, "sport", trusted_primary=False) is False


def test_automatic_source_rejects_generic_google_topic_page():
    from agent import automatic_source_usable

    item = {
        "title": "Google News - World",
        "summary": "Browse world stories, videos and other content from Google News.",
        "url": "https://news.google.com/topics/example",
        "provider": "bing-web",
    }
    assert automatic_source_usable(item, "sport", trusted_primary=False) is False


def test_automatic_source_accepts_relevant_english_sport_result():
    from agent import automatic_source_usable

    item = {
        "title": "Champions League match ends with late winning goal",
        "summary": (
            "The football match produced a late goal after a competitive second half, "
            "with the coach and players reacting after the final whistle."
        ),
        "url": "https://example.com/sport/champions-league-match",
        "provider": "bing-news",
    }
    assert automatic_source_usable(item, "sport", trusted_primary=False) is True


def test_automatic_source_accepts_localized_google_news_sport_result():
    from agent import automatic_source_usable

    item = {
        "title": "Dončić z odlično predstavo do nove zmage",
        "summary": (
            "Slovenski košarkar je dosegel pomembne točke, njegova ekipa pa je v končnici "
            "tekme potrdila zmago."
        ),
        "url": "https://example.si/sport/doncic-zmaga",
        "provider": "google-news-si",
    }
    assert automatic_source_usable(item, "sport", trusted_primary=False) is True


def test_automatic_source_rejects_unrelated_latin_broad_result_for_sport():
    from agent import automatic_source_usable

    item = {
        "title": "World news and international affairs",
        "summary": (
            "A general overview of diplomatic events, media developments and international "
            "affairs from several regions."
        ),
        "url": "https://example.com/world",
        "provider": "bing-web",
    }
    assert automatic_source_usable(item, "sport", trusted_primary=False) is False


def test_collect_automatic_sources_filters_broad_noise(monkeypatch):
    import agent

    primary = [{
        "title": "Slovenska liga prinaša nov derbi",
        "summary": "Nogometna tekma bo odigrana ta konec tedna, kluba pa sta objavila priprave.",
        "url": "https://sport.example.si/derbi",
        "hash": "primary-1",
        "provider": "",
    }]
    broad = [
        {
            "title": "월드뉴스 | KBS 뉴스",
            "summary": "무단 전재, 재배포 및 이용 금지.",
            "url": "https://news.kbs.co.kr/world",
            "hash": "bad-1",
            "provider": "bing-web",
        },
        {
            "title": "Tennis final decided in three sets",
            "summary": (
                "The tennis final went to a deciding set before the winner closed out "
                "the match with a break of serve."
            ),
            "url": "https://example.com/tennis-final",
            "hash": "good-2",
            "provider": "bing-news",
        },
    ]
    monkeypatch.setattr(agent, "collect", lambda *a, **k: primary)
    monkeypatch.setattr(agent, "collect_topic", lambda *a, **k: broad)

    out = agent.collect_automatic_sources(
        {"input_sources": [], "max_source_items": 30},
        "sport",
    )

    assert [item["url"] for item in out] == [
        "https://sport.example.si/derbi",
        "https://example.com/tennis-final",
    ]


def test_automatic_story_pool_keeps_one_coherent_story():
    import agent

    items = [
        {
            "title": "Tour de France bi se lahko začel v Sloveniji",
            "summary": "Organizatorji govorijo o možnosti slovenskega začetka dirke.",
            "url": "https://example.com/tour-a",
            "verified_direct": True,
            "provider": "bing-news",
        },
        {
            "title": "Slovenski začetek Tour de France dobiva podporo",
            "summary": "Pogovori o začetku Tour de France v Sloveniji se nadaljujejo.",
            "url": "https://example.com/tour-b",
            "verified_direct": True,
            "provider": "bing-news",
        },
        {
            "title": "Košarkarska liga se vrača prihodnji teden",
            "summary": "Klubi se pripravljajo na novo košarkarsko sezono.",
            "url": "https://example.com/basket",
            "verified_direct": True,
            "provider": "bing-news",
        },
    ]

    pool = agent.automatic_story_pool(items, "sport", max_items=6)
    urls = [item["url"] for item in pool]
    assert "https://example.com/tour-a" in urls
    assert "https://example.com/tour-b" in urls
    assert "https://example.com/basket" not in urls


def test_automatic_story_pool_prefers_direct_evidence():
    import agent

    items = [
        {
            "title": "Slovenija vodi po prvem dnevu",
            "summary": "Kratek RSS povzetek brez širšega konteksta.",
            "url": "https://example.com/rss",
            "verified_direct": False,
            "provider": "",
        },
        {
            "title": "Davisov pokal: Slovenija vodi po prvem dnevu",
            "summary": (
                "Neposredno preverjena stran opisuje Davisov pokal, potek dvoboja, "
                "rezultat prvega dne in izjave po tekmah."
            ),
            "url": "https://example.com/direct",
            "verified_direct": True,
            "provider": "bing-news",
        },
    ]

    pool = agent.automatic_story_pool(items, "sport", max_items=6)
    assert pool[0]["url"] == "https://example.com/direct"


def test_article_used_items_marks_only_cited_sources_processed():
    import agent

    pool = [
        {"url": "https://example.com/a", "title": "A"},
        {"url": "https://example.com/b", "title": "B"},
        {"url": "https://example.com/c", "title": "C"},
    ]
    article = {
        "sources": [
            {"label": "B", "url": "https://example.com/b"},
            {"label": "C", "url": "https://example.com/c"},
        ]
    }
    assert [item["url"] for item in agent.article_used_items(article, pool)] == [
        "https://example.com/b",
        "https://example.com/c",
    ]


def test_grounding_repair_task_contains_review_and_draft():
    import agent

    article = {"title": "Test", "content": "Unsupported competition claim."}
    review = {
        "issues": ["Competition format is not in sources."],
        "unsupported_claims": ["first world group"],
    }
    prompt = agent.grounding_repair_task("TASK", article, review)
    assert "DEJSTVENI QA POPRAVEK" in prompt
    assert "Competition format is not in sources." in prompt
    assert "first world group" in prompt
    assert "Unsupported competition claim." in prompt


def test_fallback_digest_does_not_repeat_lead_summary():
    from services.fallback_writer import build_digest

    lead = "Slovenija je po prvem dnevu dvoboja povedla z 2:0."
    items = [
        {
            "source_name": "Vir A",
            "category": "sport",
            "title": "Slovenija povedla po prvem dnevu",
            "url": "https://example.com/a",
            "summary": lead,
            "published": "2026-09-20",
            "image_url": "",
            "video_url": "",
            "hash": "a",
        },
        {
            "source_name": "Vir B",
            "category": "sport",
            "title": "Drugi vir potrjuje vodstvo",
            "url": "https://example.com/b",
            "summary": "Drugi vir potrjuje rezultat in dodaja odziv po zaključku prvega dne.",
            "published": "2026-09-20",
            "image_url": "",
            "video_url": "",
            "hash": "b",
        },
    ]
    article = build_digest(items, "sport", max_items=2)
    assert article["content"].count(lead) == 1


def test_defer_scheduled_slot_is_idempotent_and_records_reason(monkeypatch):
    import agent

    state = {"scheduled_slots_deferred": []}
    fixed = agent.datetime(2026, 9, 20, 10, 45, tzinfo=agent.ZoneInfo("Europe/Ljubljana"))
    monkeypatch.setattr(agent, "now", lambda: fixed)

    agent.defer_scheduled_slot(state, "2026-09-20|08:17|sport", "ponavljanje")
    agent.defer_scheduled_slot(state, "2026-09-20|08:17|sport", "ponavljanje")

    assert state["scheduled_slots_deferred"] == ["2026-09-20|08:17|sport"]
    assert state["last_editorial_hold"]["reason"] == "ponavljanje"


def test_mark_scheduled_slot_done_removes_deferred_marker():
    import agent

    slot = "2026-09-20|08:17|sport"
    state = {
        "scheduled_slots_done": [],
        "scheduled_slots_deferred": [slot],
    }
    agent.mark_scheduled_slot_done(state, slot)

    assert state["scheduled_slots_done"] == [slot]
    assert state["scheduled_slots_deferred"] == []


def test_story_pool_does_not_merge_unrelated_european_final_stories():
    import agent

    items = [
        {
            "title": "Slovenija po 24 letih znova v finalu evropskega prvenstva U18 proti Italiji",
            "summary": "Mladinska reprezentanca se je uvrstila v finale.",
            "url": "https://example.com/u18-final",
            "verified_direct": True,
            "provider": "google-news-si",
        },
        {
            "title": "Slovenija začela izločilne boje evropskega prvenstva v odbojki",
            "summary": "Odbojkarska reprezentanca je začela izločilni del.",
            "url": "https://example.com/volleyball",
            "verified_direct": True,
            "provider": "google-news-si",
        },
        {
            "title": "Mlada Slovenka na evropskem prestolu",
            "summary": "Posameznica je osvojila evropski naslov v drugi športni disciplini.",
            "url": "https://example.com/individual",
            "verified_direct": True,
            "provider": "google-news-si",
        },
    ]

    pool = agent.automatic_story_pool(items, "sport", max_items=6)
    assert len(pool) == 1


def test_story_tokens_remove_generic_competition_words():
    import agent

    tokens = agent._story_tokens({
        "title": "Slovenija v finalu evropskega prvenstva proti Italiji za zlato"
    })
    assert not any(token.startswith("sloven") for token in tokens)
    assert not any(token.startswith("evrop") for token in tokens)
    assert not any(token.startswith("prven") for token in tokens)
    assert not any(token.startswith("final") for token in tokens)
    assert not any(token.startswith("italij") for token in tokens)
