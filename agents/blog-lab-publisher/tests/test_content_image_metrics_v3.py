"""Publisher V3 evidence, media licensing and telemetry regression tests."""
from pathlib import Path
import sys
import yaml
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "agents/blog-lab-publisher"))
sys.path.insert(0, str(ROOT / "scripts"))
from services import sources, media_library
import publisher_v3_metrics as metrics


def test_article_paragraph_extraction_without_menu_noise():
    html = "<main><article><p>short</p><p>" + "Muzej v Ljubljani prikazuje slovensko arheološko dediščino. " * 5 + "</p></article></main>"
    assert "Muzej" in sources._article_body_paragraphs(html)
    assert "short" not in sources._article_body_paragraphs(html)
    assert sources._article_body_paragraphs("<article><p>Ni podatkov.</p></article>") == ""


def test_licensing_rejects_noncommercial_and_derivatives_restrictions():
    for label in ("CC BY 4.0", "CC BY-SA 4.0", "CC0 1.0", "Public domain"):
        assert media_library._license_is_reusable(label)
    for label in ("CC BY-NC 4.0", "CC BY-ND 4.0", "All Rights Reserved"):
        assert not media_library._license_is_reusable(label)


def test_commons_selects_usable_landscape_image(monkeypatch):
    def item(width, height, suffix):
        return {"title": "File:Ljubljana Castle " + suffix + ".jpg", "imageinfo": [{
            "mime": "image/jpeg", "width": width, "height": height,
            "thumburl": "https://upload.wikimedia.org/" + suffix + ".jpg",
            "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"},
                            "ImageDescription": {"value": "Ljubljana castle historic Slovenia"}},
        }]}
    monkeypatch.setattr(media_library, "_api", lambda *_: {
        "query": {"pages": [item(300, 180, "tiny"), item(2200, 1400, "good")]},
    })
    assert media_library._search_once("Ljubljana Castle", "dediscina", ("ljubljan",))["url"].endswith("good.jpg")


def test_publisher_telemetry_measures_ids_not_green_status():
    before = 'const starterArticles = [\n  {\n    "id": "old",\n  }\n]'
    after = 'const starterArticles = [\n  {\n    id: "new",\n  },\n  {\n    "id": "old",\n  }\n]'
    r = metrics.outcome_from_text(before, after, [{"attempts": [{"errors": ["prekratek", "manjka_fotografija"]}]}])
    assert r["published_count"] == 1 and r["new_article_ids"] == ["new"]
    assert r["qa_rejected_attempts_observed"] == 1
    assert r["qa_reasons_observed"]["manjka_fotografija"] == 1
    assert metrics.outcome_from_text(before, before)["outcome"] == "no_article"


def test_budget_metrics_not_mistaken_for_billed_minutes():
    r = metrics.summarize_workflows([{"name": "Publisher", "conclusion": "success",
        "run_started_at": "2026-10-24T12:00:00Z", "updated_at": "2026-10-24T12:02:00Z"}], 3, False)
    assert not r["pagination_complete"]
    assert r["workflows"]["Publisher"]["wall_minutes"] == 2
    assert "NOT billable" in r["note"]


def test_budget_workflow_read_only_and_no_push_chaining():
    cfg = yaml.load((ROOT / ".github/workflows/publisher-v3-budget.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert set(cfg["on"]) == {"schedule", "workflow_dispatch"}
    assert cfg["permissions"] == {"contents": "read", "actions": "read"}
