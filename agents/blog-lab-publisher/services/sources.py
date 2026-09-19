from __future__ import annotations
import hashlib
from html import unescape
import json
import re
import time
from urllib.parse import quote_plus, urlparse
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

def _item(source, title, link, summary, published, image_url="", video_url="", source_name=""):
    material = f"{title}|{link}".encode("utf-8")
    return {
        "source_name": _clean(source_name)[:200] or source.get("name", source["url"]),
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
                        outlet = _text(n, ["source"])
                        items.append(_item(source, title, link, summary, published, image_url, video_url, outlet))
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
                    author = _text(n, [f"{{{nsurl}}}author", f"{{{nsurl}}}source"])
                    items.append(_item(source, title, link, summary, published, image_url, video_url, author))
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

def _bing_news(query_text: str, category: str, max_items: int) -> list[dict]:
    source = {
        "name": f"Bing News – {category} – {query_text[:60]}",
        "category": category,
        "url": (
            "https://www.bing.com/news/search"
            f"?q={quote_plus(query_text)}&format=rss&setlang=en-US"
        ),
        "type": "rss",
    }
    return fetch_feed(source, timeout=12, retries=2)[:max_items]

def _gdelt_news(query_text: str, category: str, max_items: int) -> list[dict]:
    # GDELT indexes news sites worldwide and does not require an API key.
    limit = max(10, min(int(max_items), 50))
    url = (
        "https://api.gdeltproject.org/api/v2/doc/doc"
        f"?query={quote_plus(query_text)}"
        "&mode=ArtList"
        f"&maxrecords={limit}"
        "&format=json"
        "&sort=HybridRel"
    )
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=15) as response:
        if getattr(response, "status", 200) >= 400:
            raise RuntimeError(f"HTTP {response.status}")
        raw = response.read(2_000_000)
    data = json.loads(raw.decode("utf-8", errors="replace"))
    articles = data.get("articles") or []
    out = []
    for article in articles:
        if not isinstance(article, dict):
            continue
        link = _safe_https(article.get("url", ""))
        title = _clean(article.get("title", ""))
        if not link or not title:
            continue
        domain = _clean(article.get("domain", ""))
        source_name = domain or "GDELT"
        summary = _clean(article.get("snippet", "") or article.get("title", ""))
        image_url = _safe_https(article.get("socialimage", ""))
        published = _clean(article.get("seendate", ""))
        out.append(_item(
            {
                "name": f"GDELT – {category}",
                "category": category,
                "url": url,
            },
            title,
            link,
            summary,
            published,
            image_url=image_url,
            source_name=source_name,
        ))
    return out[:max_items]

def _source_key(item: dict) -> str:
    source = _clean(item.get("source_name", "")).lower()
    if source and not source.startswith(("google news", "bing news", "gdelt")):
        return source
    try:
        host = (urlparse(item.get("url", "")).hostname or "").lower()
    except Exception:
        host = ""
    return host.removeprefix("www.") or source or "unknown"

def _dedupe_diverse(items: list[dict], max_items: int, per_source: int = 4) -> list[dict]:
    unique = _dedupe(items)
    out = []
    counts = {}
    for item in unique:
        if not _safe_https(item.get("url", "")):
            continue
        key = _source_key(item)
        if counts.get(key, 0) >= per_source:
            continue
        counts[key] = counts.get(key, 0) + 1
        out.append(item)
        if len(out) >= max_items:
            break
    return out

def collect_topic(topic: str, category: str, max_items: int = 30) -> list[dict]:
    queries = _topic_queries(topic)
    if not queries:
        return []

    # World source search:
    # 1) Google News Slovenia
    # 2) Google News global English
    # 3) Bing News
    # 4) GDELT worldwide news index
    # We merge rather than stop at the first provider so articles can cite
    # multiple independent outlets instead of a single search ecosystem.
    providers = []
    for hl, gl, ceid, label in [
        ("sl", "SI", "SI:sl", "Google News SI"),
        ("en-US", "US", "US:en", "Google News EN"),
    ]:
        providers.append(("google", (hl, gl, ceid, label)))
    providers.extend([
        ("bing", None),
        ("gdelt", None),
    ])

    gathered = []
    target = max(8, min(max_items, 30))

    for provider, settings in providers:
        provider_items = []
        for query_text in queries:
            try:
                if provider == "google":
                    hl, gl, ceid, label = settings
                    source = {
                        "name": f"{label} – {category} – {query_text[:60]}",
                        "category": category,
                        "url": (
                            "https://news.google.com/rss/search"
                            f"?q={quote_plus(query_text)}&hl={quote_plus(hl)}"
                            f"&gl={quote_plus(gl)}&ceid={quote_plus(ceid)}"
                        ),
                        "type": "rss",
                    }
                    found = fetch_feed(source, timeout=12, retries=2)
                elif provider == "bing":
                    found = _bing_news(query_text, category, target)
                else:
                    found = _gdelt_news(query_text, category, target)
                provider_items.extend(found)
            except Exception as exc:
                print(
                    f"WARN world source provider={provider} "
                    f"query={query_text!r} error={exc}"
                )

            if len(_dedupe(provider_items)) >= target:
                break

        gathered.extend(provider_items)
        # Once we have a healthy, diverse source pool there is no need to
        # continue spending network time on every remaining provider.
        if len(_dedupe_diverse(gathered, target)) >= min(target, 12):
            break

    return _dedupe_diverse(gathered, max_items)

def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        if item["hash"] in seen:
            continue
        seen.add(item["hash"])
        unique.append(item)
    return unique
