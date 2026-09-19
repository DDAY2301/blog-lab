from __future__ import annotations
import hashlib
from html import unescape
import re
import time
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

USER_AGENT = "BlogLabPublisher/2.1 (+https://github.com/DDAY2301/blog-lab)"

def _text(node, names):
    for name in names:
        el = node.find(name)
        if el is not None and el.text:
            return el.text.strip()
    return ""

def _clean(value):
    value = re.sub(r"<[^>]+>", " ", unescape(value or ""))
    return " ".join(value.replace("\x00", "").split())

def _safe_https(value: str) -> str:
    value = unescape(str(value or "")).strip()
    return value[:2000] if value.lower().startswith("https://") else ""

def _node_media(node, summary: str = "") -> tuple[str, str]:
    image_url = ""
    video_url = ""
    raw_summary = unescape(summary or "")
    image_match = re.search(r'<img[^>]+src=["\'](https://[^"\']+)["\']', raw_summary, re.I)
    if image_match:
        image_url = _safe_https(image_match.group(1))
    youtube_match = re.search(r'https://(?:www\.)?(?:youtube\.com/watch\?[^\s"\']*v=|youtu\.be/)[^\s"\'&<]+', raw_summary, re.I)
    if youtube_match:
        video_url = _safe_https(youtube_match.group(0))

    for el in node.iter():
        tag = str(el.tag).lower()
        attrs = {str(k).lower(): str(v) for k, v in el.attrib.items()}
        candidate = _safe_https(attrs.get("url") or attrs.get("href") or "")
        if not candidate:
            continue
        media_type = attrs.get("type", "").lower()
        medium = attrs.get("medium", "").lower()
        if not image_url and ("thumbnail" in tag or medium == "image" or media_type.startswith("image/")):
            image_url = candidate
        if not video_url and (medium == "video" or media_type.startswith("video/") or "youtube.com/" in candidate or "youtu.be/" in candidate):
            video_url = candidate
    return image_url, video_url

def _item(source, title, link, summary, published, image_url="", video_url=""):
    material = f"{title}|{link}".encode("utf-8")
    return {
        "source_name": source.get("name", source["url"]),
        "category": source.get("category", "aktualno"),
        "title": _clean(title)[:500],
        "url": _clean(link)[:2000],
        "summary": _clean(summary)[:4000],
        "published": _clean(published)[:200],
        "image_url": _safe_https(image_url),
        "video_url": _safe_https(video_url),
        "hash": hashlib.sha256(material).hexdigest(),
    }

def fetch_feed(source: dict, timeout: int = 15, retries: int = 3) -> list[dict]:
    url = source["url"]
    last = None
    for attempt in range(retries):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, text/xml"})
            with urlopen(req, timeout=timeout) as r:
                if getattr(r, "status", 200) >= 400:
                    raise RuntimeError(f"HTTP {r.status}")
                raw = r.read(2_000_000)
            root = ET.fromstring(raw)
            items = []
            nodes = root.findall(".//item")
            if nodes:
                for n in nodes:
                    title = _text(n, ["title"])
                    link = _text(n, ["link"])
                    summary = _text(n, ["description", "summary"])
                    published = _text(n, ["pubDate", "date"])
                    if title and link:
                        image_url, video_url = _node_media(n, summary)
                        items.append(_item(source, title, link, summary, published, image_url, video_url))
                return items
            nsurl = "http://www.w3.org/2005/Atom"
            for n in root.findall(f".//{{{nsurl}}}entry"):
                title = _text(n, [f"{{{nsurl}}}title"])
                link_el = n.find(f"{{{nsurl}}}link")
                link = link_el.attrib.get("href", "") if link_el is not None else ""
                summary = _text(n, [f"{{{nsurl}}}summary", f"{{{nsurl}}}content"])
                published = _text(n, [f"{{{nsurl}}}published", f"{{{nsurl}}}updated"])
                if title and link:
                    image_url, video_url = _node_media(n, summary)
                    items.append(_item(source, title, link, summary, published, image_url, video_url))
            return items
        except Exception as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Vir ni dosegljiv: {url}: {last}")

def collect(sources: list[dict], category: str, max_items: int = 30) -> list[dict]:
    out = []
    selected = [s for s in sources if s.get("category", "aktualno") == category]
    for source in selected:
        try:
            out.extend(fetch_feed(source))
        except Exception as exc:
            print(f"WARN source={source.get('url')} error={exc}")
    return _dedupe(out)[:max_items]

def _topic_queries(topic: str) -> list[str]:
    text = _clean(topic or "")
    text = re.sub(r"\[(?:hero slika|naložena slika):\s*https://[^\]]+\]", " ", text, flags=re.I)
    text = re.sub(r"https://\S+", " ", text)
    text = " ".join(text.split()).strip(" .,:;!?")
    if not text:
        return []

    candidates = [text]

    # Natural editorial prompts often contain two useful topic clauses joined by "in".
    parts = [p.strip(" .,:;!?") for p in re.split(r"\s+(?:in|ter)\s+", text, flags=re.I) if len(p.strip()) >= 8]
    candidates.extend(parts[:3])

    stop = {
        "objavi", "objava", "članek", "clanek", "napiši", "napisi", "prispevek",
        "dodaj", "prosim", "lahko", "naj", "bodi", "naredi", "sedaj", "zdaj",
        "kjer", "kako", "kam", "nekaj", "zelo", "tudi", "samo", "stran",
        "novem", "novi", "novo", "aktualno", "aktualen", "aktualna", "aktualni",
        "profesionalen", "profesionalno", "daljši", "daljsi", "daljše", "daljse",
        "boljši", "boljsi", "boljše", "boljse", "dober", "dobra", "dobro",
    }
    words = [
        w for w in re.findall(r"[A-Za-zČŠŽčšžĆćĐđ0-9-]+", text)
        if len(w) >= 4 and w.lower() not in stop
    ]
    if words:
        candidates.append(" ".join(words[:7]))
        candidates.append(" ".join(words[:4]))
        if len(words) >= 3:
            candidates.append(" ".join(words[-3:]))
        if len(words) >= 2:
            candidates.append(" ".join(words[:2]))

    out = []
    seen = set()
    for candidate in candidates:
        key = candidate.lower()
        if candidate and key not in seen:
            seen.add(key)
            out.append(candidate)
    return out[:6]

def collect_topic(topic: str, category: str, max_items: int = 30) -> list[dict]:
    queries = _topic_queries(topic)
    if not queries:
        return []

    # Prefer Slovenian Google News. If it yields nothing at all, retry the same
    # editorial topic against a broader English index. This increases coverage
    # for international/niche manual requests without ever publishing
    # source-less claims.
    locales = [
        ("sl", "SI", "SI:sl", "SI"),
        ("en-US", "US", "US:en", "EN"),
    ]
    out = []

    for hl, gl, ceid, locale_label in locales:
        locale_out = []
        for query_text in queries:
            source = {
                "name": f"Google News {locale_label} – {category} – {query_text[:60]}",
                "category": category,
                "url": (
                    "https://news.google.com/rss/search"
                    f"?q={quote_plus(query_text)}&hl={quote_plus(hl)}"
                    f"&gl={quote_plus(gl)}&ceid={quote_plus(ceid)}"
                ),
                "type": "rss",
            }
            try:
                locale_out.extend(fetch_feed(source))
            except Exception as exc:
                print(
                    f"WARN topic source locale={locale_label} "
                    f"query={query_text!r} error={exc}"
                )
            if len(_dedupe(locale_out)) >= max_items:
                break

        locale_out = _dedupe(locale_out)
        if locale_out:
            out.extend(locale_out)
            break

    return _dedupe(out)[:max_items]

def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        if item["hash"] in seen:
            continue
        seen.add(item["hash"])
        unique.append(item)
    return unique
