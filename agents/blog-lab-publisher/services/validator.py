from __future__ import annotations
import re
from urllib.parse import urlparse

REQUIRED = ("title", "excerpt", "seoDescription", "content", "category", "tags")

def _safe_external_url(value: str) -> bool:
    try:
        parsed = urlparse(str(value or "").strip())
        return parsed.scheme == "https" and bool(parsed.netloc)
    except Exception:
        return False

def _media_urls(article: dict) -> list[str]:
    urls = []
    hero = article.get("heroImage")
    if isinstance(hero, str):
        urls.append(hero)
    elif isinstance(hero, dict):
        urls.append(hero.get("url", ""))
    video = article.get("video")
    if isinstance(video, str):
        urls.append(video)
    elif isinstance(video, dict):
        urls.append(video.get("url", ""))
    for item in article.get("gallery", []) if isinstance(article.get("gallery"), list) else []:
        if isinstance(item, str):
            urls.append(item)
        elif isinstance(item, dict):
            urls.append(item.get("url", ""))
    return [str(x).strip() for x in urls if str(x or "").strip()]

def _source_urls(article: dict) -> list[str]:
    urls = []
    for item in article.get("sources", []) if isinstance(article.get("sources"), list) else []:
        if isinstance(item, dict) and item.get("url"):
            urls.append(str(item["url"]).strip())
    return urls

def _normalized_sentence(value: str) -> str:
    value = re.sub(r"\[[^\]]+\]\([^\)]+\)", " ", str(value or ""))
    value = re.sub(r"[*_#>\-]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def _has_repeated_long_sentence(content: str) -> bool:
    seen = set()
    for raw in re.split(r"(?<=[.!?])\s+|\n+", str(content or "")):
        sentence = _normalized_sentence(raw)
        if len(sentence) < 75:
            continue
        if sentence in seen:
            return True
        seen.add(sentence)
    return False


def _has_generic_heading(content: str) -> bool:
    return bool(re.search(
        r"(?im)^#{2,4}\s*(?:uvod|zaključek|zakljucek|povzetek)\s*$",
        str(content or ""),
    ))


def validate(article: dict, min_chars: int, max_chars: int, used_titles: set[str], used_urls: set[str], allowed_urls: set[str] | None = None) -> list[str]:
    errors = []
    if article.get("skip"):
        return ["SKIP"]
    for key in REQUIRED:
        if not article.get(key):
            errors.append(f"manjka:{key}")

    title = str(article.get("title", "")).strip()
    content = str(article.get("content", "")).strip()
    if title.lower() in used_titles:
        errors.append("podvojen_naslov")
    if len(content) < min_chars:
        errors.append("prekratek")
    if len(content) > max_chars:
        errors.append("predolg")

    content_urls = re.findall(r"https?://[^\s)\]>\"]+", content)
    source_urls = _source_urls(article)
    evidence_urls = list(dict.fromkeys(content_urls + source_urls))
    if not evidence_urls:
        errors.append("brez_virov")
    for url in evidence_urls:
        if not _safe_external_url(url):
            errors.append("neveljaven_url")
        if url in used_urls:
            errors.append("ze_uporabljen_vir")

    if allowed_urls is not None:
        allowed = {str(url).strip() for url in allowed_urls if str(url or "").strip()}
        for url in source_urls:
            if url not in allowed:
                errors.append("vir_ni_v_podlagi")

    for url in _media_urls(article):
        if url.startswith("/"):
            continue
        if not _safe_external_url(url):
            errors.append("neveljaven_medij")

    lower = content.lower()
    if "<script" in lower or "javascript:" in lower or "data:text/html" in lower:
        errors.append("nevarna_vsebina")
    if _has_repeated_long_sentence(content):
        errors.append("ponavljanje")
    if _has_generic_heading(content):
        errors.append("genericni_podnaslov")
    if len(str(article.get("excerpt", ""))) > 240:
        errors.append("predolg_povzetek")
    if len(article.get("gallery", []) if isinstance(article.get("gallery"), list) else []) > 12:
        errors.append("prevec_slik")
    return list(dict.fromkeys(errors))
