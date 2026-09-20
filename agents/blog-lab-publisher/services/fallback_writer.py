from __future__ import annotations
from datetime import datetime
from html import unescape
import re
from zoneinfo import ZoneInfo

LABELS = {
    "sport": ("Šport", "Šport"),
    "politika": ("Politika", "Politika"),
    "aktualno": ("Aktualno", "Aktualno"),
}

def _clean(text: str, limit: int = 720) -> str:
    text = re.sub(r"<[^>]+>", " ", unescape(text or ""))
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[:limit - 1].rsplit(" ", 1)[0] + "…"
    return text

def _headline(title: str, category_label: str) -> str:
    title = _clean(title, 115)
    title = re.sub(r"\s+-\s+[^-]{2,45}$", "", title).strip()
    if not title:
        return f"{category_label}: zgodbe dneva"
    return title

def _section_title(title: str) -> str:
    clean = _clean(title, 105)
    clean = re.sub(r"\s+-\s+[^-]{2,45}$", "", clean).strip()
    return clean or "Nova zgodba"

def build_digest(items: list[dict], category: str, max_items: int = 5) -> dict:
    now = datetime.now(ZoneInfo("Europe/Ljubljana"))
    cat_label, _ = LABELS.get(category, LABELS["aktualno"])
    chosen = items[:max_items]
    if not chosen:
        return {"skip": True, "reason": "Ni novih virov."}

    lead_item = chosen[0]
    title = _headline(lead_item.get("title", ""), cat_label)
    lead_summary = _clean(lead_item.get("summary", ""))
    if not lead_summary:
        lead_summary = (
            "Najpomembnejši razpoložljivi vir objavlja novo zgodbo, vendar RSS zapis "
            "ne vsebuje dovolj podrobnosti za širše sklepanje."
        )

    excerpt = _clean(
        f"{cat_label}: pregled preverljivih informacij iz današnjih virov, z osrednjo zgodbo »{title}«.",
        210,
    )

    parts = [
        f"**{cat_label}, {now.strftime('%-d. %-m. %Y')}.** {lead_summary}",
        (
            "Spodaj so zbrane le informacije, ki jih je mogoče neposredno povezati z objavljenimi "
            "viri. Kjer vir ne ponuja dovolj podrobnosti, besedilo ne zapolnjuje vrzeli z ugibanjem."
        ),
    ]

    if category == "politika":
        parts.append(
            "Pri političnih temah Blog Lab ne podpira kandidatov, strank ali političnih odločitev; "
            "izjave in ocene so predstavljene kot stališča njihovih avtorjev ali virov, ne kot uredniška presoja."
        )

    for item in chosen:
        section_title = _section_title(item.get("title", ""))
        summary = _clean(item.get("summary", ""))
        if not summary:
            summary = (
                "Vir je objavil novo vsebino s tem naslovom, vendar javni RSS zapis ne vsebuje "
                "dovolj vsebine za zanesljivo dodatno razlago."
            )
        published = _clean(item.get("published", ""), 100)
        source_name = _clean(item.get("source_name", "vir"), 100)
        meta = f" Vir: {source_name}."
        if published:
            meta += f" Objavljeno: {published}."
        parts.append(
            f"## {section_title}\n\n{summary}\n\n{meta} "
            f"[Odpri izvirni vir]({item.get('url', '')})"
        )

    parts.append(
        "## Kaj spremljati naprej\n\n"
        "Zgodbe se lahko po prvi objavi še dopolnijo z novimi podatki, popravki ali odzivi. "
        "Za spremembe, ki še niso zajete v teh virih, je smiselno preveriti neposredne povezave "
        "in poznejše objave istih uredništev."
    )
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
        for x in chosen
        if x.get("url")
    ]

    return {
        "title": title,
        "excerpt": excerpt,
        "seoDescription": excerpt[:158],
        "content": content,
        "category": cat_label,
        "tags": [cat_label.lower(), "pregled"],
        "heroImage": images[0] if images else None,
        "gallery": images[1:6],
        "video": {"url": video_url, "title": "Povezan video"} if video_url else None,
        "sources": sources,
        "source_urls": [x.get("url") for x in chosen],
        "fallback": True,
    }
