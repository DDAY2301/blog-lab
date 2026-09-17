import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.validator import validate
def test_valid_article():
    content=("Uporabna preverjena vsebina. "*100)+"\n## Viri\nhttps://example.com/a"; a={"title":"Nov naslov","excerpt":"Kratek povzetek","seoDescription":"Opis","content":content,"category":"Novice","tags":["test"]}; assert validate(a,100,10000,set(),set())==[]
def test_duplicate_title():
    content=("Besedilo "*100)+"\nhttps://example.com/x"; a={"title":"Isti","excerpt":"E","seoDescription":"S","content":content,"category":"Novice","tags":["x"]}; assert "podvojen_naslov" in validate(a,100,10000,{"isti"},set())
