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
