import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.fallback_writer import build_digest

def test_fallback_builds_sports_article():
    items = [{"title": f"Novica {i}", "url": f"https://example.com/{i}", "summary": "To je dovolj dolg povzetek športnega dogodka z osnovnimi preverljivimi informacijami. " * 4, "published": "danes", "source_name": "Primer"} for i in range(5)]
    a = build_digest(items, "sport")
    assert a["category"] == "Šport"
    assert len(a["content"]) > 1200
    assert a["sources"]
    assert a["heroImage"] is None

def test_political_fallback_is_neutral():
    item = {"title": "Politična novica", "url": "https://example.com/p", "summary": "Objavljen je nov podatek.", "source_name": "Primer"}
    a = build_digest([item], "politika")
    assert "ne podpira kandidatov" in a["content"]


def test_fallback_uses_source_media_when_present():
    items = [{
        "title": "Dogodek",
        "url": "https://example.com/story",
        "summary": "Dovolj dolg preverljiv povzetek. " * 50,
        "source_name": "Primer",
        "image_url": "https://example.com/photo.jpg",
        "video_url": "https://youtu.be/example",
    }]
    a = build_digest(items, "aktualno")
    assert a["heroImage"]["url"] == "https://example.com/photo.jpg"
    assert a["video"]["url"] == "https://youtu.be/example"
    assert a["sources"][0]["url"] == "https://example.com/story"
