from __future__ import annotations

import hashlib
import re
import unicodedata

TEMPLATES = {
    "newsroom": {
        "label": "Newsroom",
        "description": "Resen uredniški format za politiko, javne zadeve in analitične novice.",
        "plan": (
            "Lead: bistvo in zakaj je pomembno. "
            "Nato 3–5 konkretnih sklopov: kaj se je zgodilo; ključna dejstva in akterji; "
            "kontekst; različni preverljivi pogledi, kadar obstajajo; kaj sledi. "
            "Ton naj bo miren, nevtralen in faktografski."
        ),
    },
    "pulse": {
        "label": "Pulse",
        "description": "Dinamičen športni in dogodkovni format.",
        "plan": (
            "Lead naj takoj poda rezultat, dogodek ali osrednji trenutek. "
            "Sledi: ključni trenutki; številke oziroma preverljiva dejstva; odzivi ali kontekst; "
            "kaj rezultat pomeni; naslednji termin ali korak, če ga viri potrjujejo. "
            "Ritem je živahen, vendar brez senzacionalizma."
        ),
    },
    "afterdark": {
        "label": "After Dark",
        "description": "Sodobni urbani format za kulturo, glasbo, gastronomijo in nočno življenje.",
        "plan": (
            "Odpri z močnim prizorom ali konkretnim mestnim kontekstom, vendar samo iz dokazljivih podatkov. "
            "Sledi: kaj se dogaja; kdo ali kaj izstopa; lokacija in praktičen kontekst; "
            "zakaj je tema zanimiva; kaj je vredno spremljati naprej. "
            "Naj zveni sodobno in samozavestno, ne kot oglas."
        ),
    },
    "studio": {
        "label": "Studio",
        "description": "Čist moderni format za tehnologijo, AI, znanost, gospodarstvo in inovacije.",
        "plan": (
            "Najprej razloži novost v enem jasnem leadu. "
            "Nato: kako stvar deluje; kaj se je dejansko spremenilo; komu je pomembna; "
            "omejitve ali tveganja; naslednji preverljivi koraki. "
            "Izogibaj se žargonu ali ga sproti razloži."
        ),
    },
    "fieldnote": {
        "label": "Field Note",
        "description": "Topel vizualni format za potovanja, hrano, naravo, lokalne zgodbe in vodiče.",
        "plan": (
            "Lead naj bralca takoj postavi v kraj ali uporabni kontekst. "
            "Sledi: kaj je vredno vedeti; ključne lokacije ali elementi; praktične informacije; "
            "lokalni kontekst; odgovoren nasvet oziroma kaj preveriti pred obiskom. "
            "Besedilo naj bo uporabno, konkretno in brez turističnega pretiravanja."
        ),
    },
    "magazine": {
        "label": "Magazine",
        "description": "Sodoben feature format za splošne aktualne zgodbe.",
        "plan": (
            "Lead naj vsebuje glavno zgodbo in jasno tezo. "
            "Nato 3–5 vsebinskih sklopov: osrednja dejstva; širši kontekst; "
            "kaj je novega ali drugačnega; posledice oziroma pomen; kaj spremljati naprej. "
            "Piši tekoče kot kakovosten spletni magazin."
        ),
    },
}

KEYWORDS = {
    "pulse": (
        "sport", "šport", "nogomet", "košark", "tenis", "koles", "tekma", "liga",
        "prvenstvo", "igralec", "trener", "formula", "hokej", "smuč", "atlet",
    ),
    "afterdark": (
        "nočno življenje", "nocno zivljenje", "nightlife", "glasb", "koncert", "festival", "klub", "kultur", "film",
        "gledali", "restavr", "bar", "chef", "kulinar", "umetnost", "design", "moda",
    ),
    "studio": (
        "tehnolog", "technology", "umetna inteligenca", "artificial intelligence", " ai ",
        "startup", "znanost", "science", "digital", "software", "aplikacij", "gospodar",
        "finance", "financ", "inovacij", "robot", "podjetj",
    ),
    "fieldnote": (
        "potov", "travel", "izlet", "narava", "planin", "gora", "jezero", "morje",
        "hrana", "food", "recept", "lokaln", "muzej", "grad", "dedišč", "heritage",
        "vodnik", "guide", "obisk",
    ),
    "newsroom": (
        "politik", "vlada", "minister", "parlament", "volit", "zakon", "občina",
        "predsednik", "javni", "eu ", "evropsk", "držav",
    ),
}

CATEGORY_DEFAULTS = {
    "sport": "pulse",
    "politika": "newsroom",
    "aktualno": "magazine",
    "šport": "pulse",
    "politika": "newsroom",
    "aktualno": "magazine",
    "novice": "magazine",
    "projekti": "studio",
    "vodniki": "fieldnote",
    "mnenja": "magazine",
}


def _fold(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text).strip()
    return f" {text} "


def choose_article_template(category: str, topic: str = "", title: str = "") -> str:
    haystack = _fold(" ".join([str(category or ""), str(topic or ""), str(title or "")]))
    scores = {}
    for key, terms in KEYWORDS.items():
        score = 0
        for term in terms:
            folded = _fold(term).strip()
            if not folded:
                continue
            if len(folded) <= 3:
                matched = bool(re.search(rf"(?<!\\w){re.escape(folded)}(?!\\w)", haystack))
            else:
                matched = folded in haystack
            if matched:
                score += 2 if len(folded) >= 7 else 1
        scores[key] = score

    best_key = max(scores, key=scores.get)
    if scores[best_key] > 0:
        return best_key

    category_key = _fold(category).strip()
    if category_key in CATEGORY_DEFAULTS:
        return CATEGORY_DEFAULTS[category_key]

    # Stable fallback: articles without a clear topical signal still alternate
    # between two clean magazine-like layouts without relying on randomness.
    digest = hashlib.sha1(_fold(topic or title or category).encode("utf-8")).digest()[0]
    return "magazine" if digest % 2 == 0 else "fieldnote"


def template_prompt(category: str, topic: str = "") -> str:
    key = choose_article_template(category, topic)
    profile = TEMPLATES[key]
    return (
        "\n\n## Obvezni Blog Lab article template\n"
        f"Template: {profile['label']} ({key}).\n"
        f"Uredniški namen: {profile['description']}\n"
        f"Struktura: {profile['plan']}\n"
        "Template določa ritem in strukturo, ne dejstev. Ne izmišljaj informacij, "
        "ne dodajaj praznih sekcij in ne spreminjaj nevtralnega uredniškega standarda."
    )


def apply_article_template(article: dict, category: str, topic: str = "") -> dict:
    out = dict(article or {})
    key = choose_article_template(
        category or str(out.get("category") or ""),
        topic,
        str(out.get("title") or ""),
    )
    out["visualTemplate"] = key
    out["templateLabel"] = TEMPLATES[key]["label"]
    return out
