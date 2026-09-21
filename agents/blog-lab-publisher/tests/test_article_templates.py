from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.article_templates import (
    TEMPLATES,
    apply_article_template,
    choose_article_template,
    template_prompt,
)


def test_all_expected_templates_exist():
    assert set(TEMPLATES) == {
        "newsroom",
        "pulse",
        "afterdark",
        "studio",
        "fieldnote",
        "magazine",
    }


def test_sport_uses_pulse():
    assert choose_article_template("sport", "tekma slovenske košarkarske lige") == "pulse"


def test_politics_uses_newsroom():
    assert choose_article_template("politika", "razprava v parlamentu o zakonu") == "newsroom"


def test_nightlife_uses_afterdark():
    assert choose_article_template("aktualno", "nočno življenje, koncerti in klubi v Ljubljani") == "afterdark"


def test_technology_uses_studio():
    assert choose_article_template("aktualno", "AI startup in nova tehnološka platforma") == "studio"


def test_travel_food_uses_fieldnote():
    assert choose_article_template("aktualno", "vikend izlet, lokalna hrana in muzej") == "fieldnote"


def test_general_current_affairs_uses_magazine():
    assert choose_article_template("aktualno", "dogajanje tega tedna") == "magazine"


def test_short_ai_keyword_is_word_bounded():
    # "ai" inside another word must not force the Studio template.
    assert choose_article_template("aktualno", "trajnostni razvoj mesta") == "magazine"


def test_template_prompt_is_editorial_not_factual():
    prompt = template_prompt("aktualno", "koncert in nočno življenje")
    assert "Template: After Dark" in prompt
    assert "Template določa ritem in strukturo, ne dejstev." in prompt


def test_apply_article_template_persists_visual_contract():
    article = apply_article_template(
        {
            "title": "Nočno nebo nad Ljubljano",
            "category": "Aktualno",
            "content": "Preverjena vsebina.",
        },
        "aktualno",
        "nočno nebo nad Ljubljano",
    )
    assert article["visualTemplate"] in TEMPLATES
    assert article["templateLabel"] == TEMPLATES[article["visualTemplate"]]["label"]


def test_prepare_article_candidate_always_adds_template():
    from agent import prepare_article_candidate

    article = prepare_article_candidate(
        {
            "title": "Nova AI platforma v Sloveniji",
            "category": "Aktualno",
            "content": "Preverjena vsebina.",
            "heroImage": None,
            "gallery": [],
            "video": None,
        },
        [],
        "nova AI platforma v Sloveniji",
        "Aktualno",
    )
    assert article["visualTemplate"] == "studio"
    assert article["templateLabel"] == "Studio"
