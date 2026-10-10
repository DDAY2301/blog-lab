"""Conservative, deterministic publication gate for the Slovenian tourism edition.

This is deliberately separate from prompts/LLM review: a model cannot waive it.
A held scheduled slot is preferable to publishing an unrelated scraped webpage.
"""
from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlsplit

CATEGORY_SIGNALS = {
    "kolesarstvo": ("koles", "bicikl", "cycling", "bicycle", "gravel", "mtb"),
    "dediscina": ("dedisc", "zgodovin", "grad", "muzej", "heritage", "obisc", "spomen", "tradic", "arheol"),
    "sezonsko": ("sezon", "jesen", "zima", "polet", "pomlad", "izlet", "turiz", "dogod", "vreme", "praznik"),
    "gore": ("gora", "gorah", "gors", "pohod", "planin", "alp", "trail", "pot", "vzpon", "vrh", "koca", "tamar"),
    "gourmet": ("kulinar", "gostil", "restavr", "gastronom", "recept", "jed", "hrana", "vino", "sir", "okus", "gibanic", "potica", "zlikrof", "food", "cuisine"),
}
SLOVENIA_SIGNALS = (
    "sloven", "slovensk", "ljubljan", "bohinj", "bled", "planic", "tamar",
    "triglav", "piran", "soce", "soca", "maribor", "ptuj", "idrij",
    "kranj", "gorenj", "primorsk", "prekmur", "stajers", "dolenj",
    "posav", "korosk", "vipav", "postojn", "celj", "novo mest",
    "koper", "izol", "portoroz", "brd", "radovljic", "vintgar",
    "haloz", "pohor", "logars", "skofj", "tolmin", "bovec",
)
SLOVENE_STOPWORDS = frozenset((
    "in", "je", "so", "se", "na", "za", "z", "s", "v", "iz", "pri",
    "po", "ki", "ter", "kot", "lahko", "tudi", "ob", "od", "do", "ali",
    "pa", "da", "bo", "bodo", "med", "kjer", "ko", "o", "pod", "nad",
    "kar", "ker", "sta", "bil", "bila", "bilo", "obiskovalci", "pot",
))
SCRAPED_UI = (
    "open navigation", "close navigation", "all rights reserved",
    "privacy policy", "cookie preferences", "sign in to your account",
    "subscribe to our newsletter", "skip to main content",
)


def fold(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _article_sources(article: dict) -> set[str]:
    return {
        str(item.get("url") or "").strip()
        for item in (article.get("sources") or [])
        if isinstance(item, dict) and item.get("url")
    }


def validate_automatic_story(article: dict, source_items: list[dict], category: str) -> list[str]:
    """Return hold reasons for scheduled publication; do not change manual workflows."""
    errors = []
    if article.get("skip"):
        return ["skip"]
    category_key = str(category or "").lower().strip()
    terms = CATEGORY_SIGNALS.get(category_key)
    if not terms:
        return ["neznana_rubrika"]

    title = fold(article.get("title", ""))
    excerpt = fold(article.get("excerpt", ""))
    content = str(article.get("content") or "")
    lower_content = fold(content)
    article_intro = title + " " + excerpt + " " + lower_content[:1100]

    if not _has_any(title + " " + excerpt, terms):
        errors.append("naslov_ni_v_rubriki")
    if not _has_any(article_intro, SLOVENIA_SIGNALS):
        errors.append("clanek_brez_slovenskega_konteksta")

    # A themed RSS/search query is NOT evidence that the resulting page is relevant.
    # Check the raw title and summary of each actual cited source.
    cited_urls = _article_sources(article)
    relevant = []
    for item in source_items or []:
        url = str(item.get("url") or "").strip()
        if cited_urls and url not in cited_urls:
            continue
        source_text = fold(str(item.get("title") or "") + " " + str(item.get("summary") or "")[:900])
        if _has_any(source_text, terms) and _has_any(source_text, SLOVENIA_SIGNALS):
            relevant.append(item)

    if not relevant:
        errors.append("viri_ne_podpirajo_slovenske_rubrike")

    # Website menus and text-extraction dumps are not publishable editorial copy.
    if any(fragment in lower_content for fragment in SCRAPED_UI):
        errors.append("surov_spletni_izpis")

    # A Slovenian introduction cannot excuse several paragraphs copied in English.
    plain = re.sub(r"https?://\S+|!?\[[^\]]*\]\([^)]*\)|[#*_>]", " ", lower_content)
    tokens = re.findall(r"[a-zčšžćđ]{2,}", plain)
    if len(tokens) >= 100:
        slovene_count = sum(token in SLOVENE_STOPWORDS for token in tokens)
        if slovene_count / len(tokens) < 0.07:
            errors.append("besedilo_ni_v_slovenscini")

    return list(dict.fromkeys(errors))
