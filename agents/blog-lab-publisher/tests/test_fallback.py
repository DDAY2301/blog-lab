import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.fallback_writer import build_digest

def test_fallback_builds_sports_article():
    items = [{"title": f"Novica {i}", "url": f"https://example.com/{i}", "summary": "To je dovolj dolg povzetek športnega dogodka z osnovnimi preverljivimi informacijami. " * 4, "published": "danes", "source_name": "Primer"} for i in range(5)]
    a = build_digest(items, "sport")
    assert a["category"] == "Šport"
    assert len(a["content"]) > 1200
    assert "## Viri" in a["content"]

def test_political_fallback_is_neutral():
    item = {"title": "Politična novica", "url": "https://example.com/p", "summary": "Objavljen je nov podatek.", "source_name": "Primer"}
    a = build_digest([item], "politika")
    assert "ne podpira kandidatov" in a["content"]
