from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.editorial_guard import validate_automatic_story
from agent import automatic_source_usable


def _article(title, excerpt, content):
    return {
        "title": title,
        "excerpt": excerpt,
        "content": content,
        "sources": [{"url": "https://example.org/story", "label": "Vir"}],
    }


def _slovenian_copy():
    return (
        "Pot skozi dolino je primerna za premišljen obisk, saj se je po poti "
        "mogoče odpraviti tudi z družino. Pri obisku je pomembno, da se "
        "pripravimo na vreme in upoštevamo informacije o razmerah na poti. "
        "Za obisk iz Slovenije je priporočljivo vnaprej preveriti dostop "
        "ter urnik in se po poti vrniti pred mrakom. "
    ) * 4


def test_holds_juneteenth_in_gourmet():
    article = _article(
        "What Is Juneteenth? | HISTORY",
        "A federal holiday in the United States.",
        "Pregled za rubriko gourmet. Open navigation Close navigation " + "U.S. History " * 100,
    )
    source = {
        "url": "https://example.org/story",
        "title": "What Is Juneteenth? | HISTORY",
        "summary": "The US federal holiday marks the end of slavery.",
    }
    errors = validate_automatic_story(article, [source], "gourmet")
    assert "naslov_ni_v_rubriki" in errors
    assert "viri_ne_podpirajo_slovenske_rubrike" in errors
    assert "surov_spletni_izpis" in errors
    assert not automatic_source_usable(source, "gourmet", trusted_primary=True)


def test_allows_grounded_slovenian_tamar_walk():
    article = _article(
        "Planica in dolina Tamar: planinski izlet",
        "Planinski pohod iz Planice v dolino Tamar v Sloveniji.",
        _slovenian_copy(),
    )
    source = {
        "url": "https://example.org/story",
        "title": "Planica in Tamar: pohodniška pot",
        "summary": "Pohod v dolino Tamar v Sloveniji ponuja dostop do koče in gorskega okolja.",
    }
    assert validate_automatic_story(article, [source], "gore") == []


def test_holds_english_scraped_copy_even_when_headline_is_relevant():
    article = _article(
        "Slovenian cuisine: potica in Ljubljana",
        "Potica is Slovenian food served in Ljubljana.",
        ("Read more about the recipes and the latest news from Ljubljana. "
         "This information is a guide to the food and what to see in the city. ") * 10,
    )
    source = {
        "url": "https://example.org/story",
        "title": "Potica in slovenska kuhinja",
        "summary": "Slovenska potica je tradicionalna jed, ki jo najdemo tudi v Ljubljani.",
    }
    assert "besedilo_ni_v_slovenscini" in validate_automatic_story(article, [source], "gourmet")


def test_holds_source_from_unrelated_country():
    article = _article(
        "Kolesarjenje po Sloveniji: najlepše poti",
        "V Sloveniji je veliko kolesarskih poti.",
        _slovenian_copy(),
    )
    source = {
        "url": "https://example.org/story",
        "title": "Cycling in Oregon",
        "summary": "A scenic bike ride in the United States with plenty of trails.",
    }
    assert "viri_ne_podpirajo_slovenske_rubrike" in validate_automatic_story(article, [source], "kolesarstvo")
