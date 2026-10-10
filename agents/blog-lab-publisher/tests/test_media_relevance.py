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
