from __future__ import annotations
from datetime import datetime
from html import unescape
import re
from zoneinfo import ZoneInfo

LABELS = {"sport": ("Šport", "Športni pregled"), "politika": ("Politika", "Politični pregled"), "aktualno": ("Aktualno", "Aktualni pregled")}

def _clean(text: str, limit: int = 620) -> str:
    text = re.sub(r"<[^>]+>", " ", unescape(text or ""))
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[:limit - 1].rsplit(" ", 1)[0] + "…"
    return text

def build_digest(items: list[dict], category: str, max_items: int = 5) -> dict:
    now = datetime.now(ZoneInfo("Europe/Ljubljana"))
    cat_label, prefix = LABELS.get(category, LABELS["aktualno"])
    chosen = items[:max_items]
    if not chosen:
        return {"skip": True, "reason": "Ni novih virov."}
    title = f"{prefix}: {now.strftime('%-d. %-m. %Y')}"
    excerpt = f"Samodejni pregled najnovejših objav za področje {cat_label.lower()}, sestavljen iz javno dostopnih RSS virov in neposrednih povezav do izvirnikov."
    parts = [f"Danes, {now.strftime('%-d. %-m. %Y')}, Blog Lab povzema nove objave s področja **{cat_label.lower()}**. Pregled je sestavljen samo iz podatkov, ki so bili objavljeni v navedenih virih; kjer RSS ne vsebuje dovolj podrobnosti, dodatnih dejstev ne ugibamo."]
    if category == "politika":
        parts.append("Pri političnih temah je poudarek na nevtralnem povzemanju objavljenih informacij. Pregled ne podpira kandidatov, strank ali političnih odločitev in ne napoveduje volilnih izidov.")
    for i, item in enumerate(chosen, 1):
        summary = _clean(item.get("summary", ""))
        if not summary:
            summary = "Vir je objavil novo vsebino s tem naslovom, vendar RSS zapis ne vsebuje dovolj dolgega povzetka za dodatno razlago."
        published = _clean(item.get("published", ""), 120)
        meta = f" Objavljeno: {published}." if published else ""
        parts.append(f"## {i}. {_clean(item.get('title', 'Brez naslova'), 180)}\n\n{summary}{meta}\n\n[Odpri izvirni vir]({item.get('url', '')})")
    parts.append("## Kaj spremljati naprej\n\nKer se aktualne zgodbe hitro dopolnjujejo, je smiselno preveriti izvirne povezave za morebitne nove podatke, popravke ali odzive. Blog Lab bo naslednji pregled pripravil šele, ko zazna nove, še neobdelane vnose.")
    content = "\n\n".join(parts)
    images = []
    seen_images = set()
    for item in chosen:
        image_url = str(item.get("image_url") or "").strip()
        if image_url and image_url not in seen_images:
            seen_images.add(image_url)
            images.append({
                "url": image_url,
                "alt": _clean(item.get("title", ""), 180),
                "caption": _clean(item.get("source_name", ""), 100),
            })
    video_url = next((str(x.get("video_url") or "").strip() for x in chosen if x.get("video_url")), "")
    sources = [
        {
            "label": f"{_clean(x.get('source_name', 'Vir'), 100)} — {_clean(x.get('title', 'Objava'), 120)}",
            "url": x.get("url", ""),
        }
        for x in chosen if x.get("url")
    ]
    return {
        "title": title,
        "excerpt": excerpt,
        "seoDescription": excerpt[:158],
        "content": content,
        "category": cat_label,
        "tags": [cat_label.lower(), "pregled", "aktualno"],
        "heroImage": images[0] if images else None,
        "gallery": images[1:6],
        "video": {"url": video_url, "title": "Povezan video"} if video_url else None,
        "sources": sources,
        "source_urls": [x.get("url") for x in chosen],
        "fallback": True,
    }
