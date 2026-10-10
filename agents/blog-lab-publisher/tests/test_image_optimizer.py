from io import BytesIO
from pathlib import Path
import sys
from unittest.mock import patch

from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.image_optimizer import optimize_commons_hero


def _commons_article():
    return {"heroImage": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/example.jpg/1600px-example.jpg",
        "sourceUrl": "https://commons.wikimedia.org/wiki/File:Example.jpg",
        "caption": "Avtor · Wikimedia Commons · CC BY-SA 4.0",
        "alt": "Planinska pot",
    }}


def test_ignores_unlicensed_or_other_hosts(tmp_path):
    article = _commons_article()
    article["heroImage"]["sourceUrl"] = "https://other.example/photo"
    assert optimize_commons_hero(article, tmp_path) == article
    assert not (tmp_path / "media").exists()


def test_commons_image_optimized_to_local_webp(tmp_path):
    source = Image.new("RGB", (1700, 1200), (70, 80, 90))
    data = BytesIO()
    source.save(data, format="PNG")
    class FakeResponse:
        headers = {"Content-Type": "image/png"}
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, limit): return data.getvalue()[:limit]

    with patch("services.image_optimizer.urlopen", return_value=FakeResponse()):
        result = optimize_commons_hero(_commons_article(), tmp_path)
    assert result["heroImage"]["url"].startswith("/media/articles/")
    assert result["heroImage"]["sourceUrl"].startswith("https://commons.wikimedia.org/")
    output = tmp_path / result["heroImage"]["url"].lstrip("/")
    assert output.exists()
    with Image.open(output) as img:
        assert img.format == "WEBP"
        assert img.size == (1600, 900)
