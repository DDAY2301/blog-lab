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
