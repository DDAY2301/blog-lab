from __future__ import annotations
import re
from urllib.parse import urlparse
REQUIRED = ("title", "excerpt", "seoDescription", "content", "category", "tags")
def validate(article: dict, min_chars: int, max_chars: int, used_titles: set[str], used_urls: set[str]) -> list[str]:
    errors = []
    if article.get("skip"):
        return ["SKIP"]
    for key in REQUIRED:
        if not article.get(key): errors.append(f"manjka:{key}")
    title = str(article.get("title", "")).strip()
    content = str(article.get("content", "")).strip()
    if title.lower() in used_titles: errors.append("podvojen_naslov")
    if len(content) < min_chars: errors.append("prekratek")
    if len(content) > max_chars: errors.append("predolg")
    urls = re.findall(r"https?://[^\s)\]>]+", content)
    if not urls: errors.append("brez_virov")
    for url in urls:
        if not urlparse(url).netloc: errors.append("neveljaven_url")
        if url in used_urls: errors.append("ze_uporabljen_vir")
    if "<script" in content.lower() or "javascript:" in content.lower(): errors.append("nevarna_vsebina")
    if len(str(article.get("excerpt", ""))) > 240: errors.append("predolg_povzetek")
    return errors
