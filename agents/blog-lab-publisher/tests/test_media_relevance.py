from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.media_library import _location_filter, _image_relevant


def test_place_filter_preserves_planica_and_tamar():
    assert "planica" in _location_filter("Planica in dolina Tamar: planinski izlet")


def test_unrelated_generic_slovenian_photo_not_enough_for_specific_place():
    expected = _location_filter("Planica in dolina Tamar: planinski izlet")
    unrelated = "Slovenia mountains hiking at Bled"
    assert not any(term in unrelated.lower() for term in expected)


def test_category_image_still_needs_slovenia_context():
    assert not _image_relevant("Hiking in Switzerland", "Mountain Alps", "gore")

def test_commons_selection_skips_photo_already_used(monkeypatch):
    import services.media_library as media
    def mock_api(_params):
        return {"query": {"pages": [
            {"title": "File:Ljubljana cycling picture 1.jpg", "imageinfo": [{
                "mime": "image/jpeg", "width": 2400, "height": 1600,
                "url": "https://upload.wikimedia.org/wikipedia/commons/a/a1/one.jpg",
                "extmetadata": {"LicenseShortName": {"value": "CC BY 4.0"},
                                "ImageDescription": {"value": "Ljubljana Slovenia bicycle cycling"}}
            }]},
            {"title": "File:Ljubljana cycling picture 2.jpg", "imageinfo": [{
                "mime": "image/jpeg", "width": 2400, "height": 1600,
                "url": "https://upload.wikimedia.org/wikipedia/commons/b/b2/two.jpg",
                "extmetadata": {"LicenseShortName": {"value": "CC BY 4.0"},
                                "ImageDescription": {"value": "Ljubljana Slovenia bicycle cycling"}}
            }]}
        ]}}
    monkeypatch.setattr(media, "_api", mock_api)
    used = {"https://commons.wikimedia.org/wiki/File:Ljubljana_cycling_picture_1.jpg"}
    result = media._search_once("Ljubljana cycling", "kolesarstvo", (), used)
    assert result["sourceUrl"].endswith("File:Ljubljana_cycling_picture_2.jpg")


def test_published_media_registry_includes_existing_article(tmp_path):
    import json
    import services.media_library as media
    folder = tmp_path / "src" / "articles" / "published"
    folder.mkdir(parents=True)
    (folder / "story.json").write_text(json.dumps({
        "id": "story", "title": "Story",
        "heroImage": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/a/a1/photo.jpg",
            "sourceUrl": "https://commons.wikimedia.org/wiki/File:Slovenia_photo.jpg"
        }
    }), encoding="utf-8")
    used = media.published_image_sources(tmp_path)
    assert "https://commons.wikimedia.org/wiki/file:slovenia_photo.jpg" in used


def test_bad_url_is_not_silently_converted_into_photo():
    from services.media_library import _media_identity
    assert _media_identity("https://commons.wikimedia.org/wiki/File:Photo.jpg?width=1600") == (
        "https://commons.wikimedia.org/wiki/file:photo.jpg"
    )
