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
