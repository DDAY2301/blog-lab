import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.validator import validate
def test_valid_article():
    content=("Uporabna preverjena vsebina. "*100)+"\n## Viri\nhttps://example.com/a"; a={"title":"Nov naslov","excerpt":"Kratek povzetek","seoDescription":"Opis","content":content,"category":"Novice","tags":["test"]}; assert validate(a,100,10000,set(),set())==[]
def test_duplicate_title():
    content=("Besedilo "*100)+"\nhttps://example.com/x"; a={"title":"Isti","excerpt":"E","seoDescription":"S","content":content,"category":"Novice","tags":["x"]}; assert "podvojen_naslov" in validate(a,100,10000,{"isti"},set())


def test_rejects_source_not_in_evidence_pool():
    content = ("Preverjena vsebina brez ponavljanja. " * 50)
    article = {
        "title": "Naslov",
        "excerpt": "Povzetek",
        "seoDescription": "Opis",
        "content": content,
        "category": "Šport",
        "tags": ["šport"],
        "sources": [{"label": "Neznan vir", "url": "https://invented.example/story"}],
    }
    errors = validate(
        article,
        100,
        10000,
        set(),
        set(),
        {"https://allowed.example/story"},
    )
    assert "vir_ni_v_podlagi" in errors


def test_accepts_source_from_evidence_pool():
    content = ("Različna preverjena vsebina z dovolj besedila. " * 45)
    url = "https://allowed.example/story"
    article = {
        "title": "Naslov dva",
        "excerpt": "Povzetek",
        "seoDescription": "Opis",
        "content": content,
        "category": "Šport",
        "tags": ["šport"],
        "sources": [{"label": "Dovoljen vir", "url": url}],
    }
    errors = validate(article, 100, 10000, set(), set(), {url})
    assert "vir_ni_v_podlagi" not in errors


def test_rejects_repeated_long_sentence():
    sentence = (
        "Slovenska reprezentanca je po prvem delu srečanja ohranila prednost "
        "in mirno nadaljevala tekmo do naslednje faze."
    )
    article = {
        "title": "Brez ponavljanja v naslovu",
        "excerpt": "Povzetek",
        "seoDescription": "Opis",
        "content": sentence + " " + sentence + " https://example.com/a",
        "category": "Šport",
        "tags": ["šport"],
        "sources": [{"label": "Vir", "url": "https://example.com/a"}],
    }
    assert "ponavljanje" in validate(article, 100, 10000, set(), set())


def test_rejects_generic_editorial_heading():
    article = {
        "title": "Konkreten naslov",
        "excerpt": "Povzetek",
        "seoDescription": "Opis",
        "content": ("Uredniško besedilo. " * 30) + "\n## Zaključek\n" + ("Nova informacija. " * 20) + " https://example.com/a",
        "category": "Šport",
        "tags": ["šport"],
        "sources": [{"label": "Vir", "url": "https://example.com/a"}],
    }
    assert "genericni_podnaslov" in validate(article, 100, 10000, set(), set())
