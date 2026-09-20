import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.fallback_writer import build_digest
from services.validator import validate

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


def test_fallback_headlines_do_not_trigger_repetition_validator():
    long_title = "Slovenija po 24 letih znova v finalu evropskega prvenstva U18, za zlato proti Italiji"
    items = [
        {
            "title": "Odbojka (M): Italija - Slovenija, Evropsko prvenstvo 2026, Skupina A - Siol.net",
            "url": "https://example.com/lead",
            "summary": "Odbojka (M): Italija - Slovenija, Evropsko prvenstvo 2026, Skupina A Siol.net",
            "source_name": "Siol.net",
            "published": "danes",
        },
        {
            "title": f"{long_title} - Šport TV",
            "url": "https://example.com/2",
            "summary": f"{long_title} Šport TV",
            "source_name": "Šport TV",
            "published": "danes",
        },
        {
            "title": "Slovenski odbojkarji so preizkusili dvorano v Torinu, kjer jih bo pričakala Srbija - Šport TV",
            "url": "https://example.com/3",
            "summary": "Slovenski odbojkarji so preizkusili dvorano v Torinu, kjer jih bo pričakala Srbija Šport TV",
            "source_name": "Šport TV",
            "published": "danes",
        },
        {
            "title": "Mlada Slovenka na evropskem prestolu: Pred prvo me je vedno strah, nato pa ... - Žurnal24",
            "url": "https://example.com/4",
            "summary": "Mlada Slovenka na evropskem prestolu: Pred prvo me je vedno strah, nato pa ... Žurnal24",
            "source_name": "Žurnal24",
            "published": "danes",
        },
        {
            "title": "Slovenija je dobro začela izločilne boje na evropskem prvenstvu v odbojki - rtvslo.si",
            "url": "https://example.com/5",
            "summary": "Slovenija je dobro začela izločilne boje na evropskem prvenstvu v odbojki rtvslo.si",
            "source_name": "rtvslo.si",
            "published": "danes",
        },
    ]
    article = build_digest(items, "sport")
    allowed_urls = {item["url"] for item in items}
    errors = validate(article, 1200, 10000, set(), set(), allowed_urls)
    assert "ponavljanje" not in errors
    assert errors == []
