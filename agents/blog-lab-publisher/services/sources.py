from __future__ import annotations
import hashlib
from html import unescape
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
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
        "provider": _clean(source.get("provider", ""))[:80],
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

def _topic_core(topic: str) -> str:
    text = _clean(topic or "")
    text = re.sub(r"\[(?:hero slika|naložena slika):\s*https://[^\]]+\]", " ", text, flags=re.I)
    text = re.sub(r"https://\S+", " ", text)
    text = " ".join(text.split()).strip(" .,:;!?")
    if not text:
        return ""

    # Remove the editorial command wrapper while preserving the actual subject.
    text = re.sub(
        r"^(?:prosim\s+)?"
        r"(?:objavi|napiši|napisi|pripravi|ustvari|sestavi)\s+"
        r"(?:(?:daljši|daljsi|daljše|daljse|kratek|kratki|nov|novi|novo|profesionalen|profesionalni)\s+)*"
        r"(?:članek|clanek|prispevek|objavo|objava|post)\s+"
        r"(?:o|na\s+temo|glede)\s+",
        "",
        text,
        flags=re.I,
    )

    # Split off writing/layout instructions from the topic. Example:
    # "dogajanje v ljubljanskem nočnem življenju in bo več teksta v članku"
    # -> "dogajanje v ljubljanskem nočnem življenju"
    text = re.split(
        r"\s+(?:in|ter)\s+(?="
        r"(?:naj|bo|bodi|dodaj|vključi|vkljuci|naredi|piši|pisi|uporabi|"
        r"povečaj|povecaj|izboljšaj|izboljsaj|več|vec|manj)\b)",
        text,
        maxsplit=1,
        flags=re.I,
    )[0]
    return " ".join(text.split()).strip(" .,:;!?")

def _topic_queries(topic: str) -> list[str]:
    original = _clean(topic or "")
    core = _topic_core(topic)
    if not core:
        return []

    candidates = [core]

    # Genuine compound topics such as "ceste in vikend izleti" still receive
    # their own subqueries. Editorial suffixes have already been removed above.
    parts = [
        p.strip(" .,:;!?")
        for p in re.split(r"\s+(?:in|ter)\s+", core, flags=re.I)
        if len(p.strip()) >= 8
    ]
    candidates.extend(parts[:2])

    stop = {
        "objavi", "objava", "članek", "clanek", "članku", "clanku",
        "napiši", "napisi", "prispevek", "dodaj", "prosim", "lahko", "naj",
        "bodi", "naredi", "sedaj", "zdaj", "kjer", "kako", "kam", "nekaj",
        "zelo", "tudi", "samo", "stran", "novem", "novi", "novo",
        "aktualno", "aktualen", "aktualna", "aktualni", "profesionalen",
        "profesionalno", "daljši", "daljsi", "daljše", "daljse", "boljši",
        "boljsi", "boljše", "boljse", "dober", "dobra", "dobro", "teksta",
        "besedila", "samem", "več", "vec",
    }
    words = [
        w for w in re.findall(r"[A-Za-zČŠŽčšžĆćĐđ0-9-]+", core)
        if len(w) >= 4 and w.lower() not in stop
    ]
    if words:
        candidates.append(" ".join(words[:6]))
        if len(words) >= 4:
            candidates.append(" ".join(words[:4]))
        if len(words) >= 2:
            candidates.append(" ".join(words[-3:]))

    # A short location/topic phrase often works better with general web search
    # than the complete natural-language request.
    ljubljana = re.sub(r"\bljubljansk\w*\b", "Ljubljana", core, flags=re.I)
    if ljubljana.lower() != core.lower():
        candidates.append(ljubljana)

    out = []
    seen = set()
    for candidate in candidates:
        candidate = " ".join(candidate.split()).strip(" .,:;!?")
        key = candidate.lower()
        if candidate and key not in seen:
            seen.add(key)
            out.append(candidate)
    return out[:5]

def _bing_web(query_text: str, category: str, max_items: int) -> list[dict]:
    # Bing's RSS search output is a general-web fallback. It can surface
    # official sites, local portals, event guides and other non-news pages.
    source = {
        "name": f"Bing Web – {category} – {query_text[:60]}",
        "category": category,
        "url": (
            "https://www.bing.com/search"
            f"?q={quote_plus(query_text)}&format=rss&setlang=sl-SI"
        ),
        "type": "rss",
    }
    return fetch_feed(source, timeout=10, retries=1)[:max_items]

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
    return fetch_feed(source, timeout=10, retries=1)[:max_items]

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
    with urlopen(req, timeout=10) as response:
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
                "provider": "gdelt",
            },
            title,
            link,
            summary,
            published,
            image_url=image_url,
            source_name=source_name,
        ))
    return out[:max_items]


def _duckduckgo_result_url(value: str) -> str:
    """Resolve DuckDuckGo HTML redirect links to the public result URL."""
    href = unescape(str(value or "")).strip()
    if href.startswith("//"):
        href = "https:" + href
    if href.startswith("/"):
        href = "https://duckduckgo.com" + href
    if not href.lower().startswith("https://"):
        return ""
    try:
        parsed = urlparse(href)
        host = (parsed.hostname or "").lower()
        if host.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
            target = parse_qs(parsed.query).get("uddg", [""])[0]
            target = unquote(target)
            return _safe_https(target)
    except Exception:
        return ""
    return _safe_https(href)

def _duckduckgo_web(query_text: str, category: str, max_items: int) -> list[dict]:
    """Search DuckDuckGo's official non-JavaScript HTML results.

    DuckDuckGo documents HTML/Lite versions for browsers without JavaScript.
    We only retain normal HTTPS result URLs plus visible result snippets.
    """
    url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query_text)
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
        },
    )
    with urlopen(req, timeout=12) as response:
        if getattr(response, "status", 200) >= 400:
            raise RuntimeError(f"HTTP {response.status}")
        raw = response.read(1_800_000)
    html = raw.decode("utf-8", errors="replace")

    # Each result block contains a result__a link and usually result__snippet.
    blocks = re.split(r'(?i)<div[^>]+class=["\'][^"\']*result[^"\']*["\']', html)
    out = []
    for block in blocks[1:]:
        link_match = re.search(
            r'(?is)<a[^>]+class=["\'][^"\']*result__a[^"\']*["\'][^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            block,
        )
        if not link_match:
            # Some responses put href before class.
            link_match = re.search(
                r'(?is)<a[^>]+href=["\']([^"\']+)["\'][^>]+class=["\'][^"\']*result__a[^"\']*["\'][^>]*>(.*?)</a>',
                block,
            )
        if not link_match:
            continue
        link = _duckduckgo_result_url(link_match.group(1))
        title = _clean(link_match.group(2))
        if not link or not title:
            continue

        snippet_match = re.search(
            r'(?is)<(?:a|div)[^>]+class=["\'][^"\']*result__snippet[^"\']*["\'][^>]*>(.*?)</(?:a|div)>',
            block,
        )
        summary = _clean(snippet_match.group(1)) if snippet_match else ""
        try:
            host = (urlparse(link).hostname or "").lower().removeprefix("www.")
        except Exception:
            host = ""

        out.append(_item(
            {
                "name": f"DuckDuckGo Web – {category}",
                "category": category,
                "url": url,
                "provider": "duckduckgo-web",
            },
            title,
            link,
            summary or title,
            "",
            source_name=host or "DuckDuckGo Web",
        ))
        if len(out) >= max_items:
            break
    return out

DIRECT_SKIP_HOSTS = {
    "news.google.com",
    "google.com",
    "www.google.com",
    "bing.com",
    "www.bing.com",
}

def _meta_content(html: str, key: str) -> str:
    key_re = re.escape(key)
    patterns = [
        rf'<meta[^>]+(?:name|property)=["\']{key_re}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\']{key_re}["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.I)
        if match:
            return _clean(match.group(1))
    return ""

def _visible_html_text(html: str, limit: int = 4200) -> str:
    text = re.sub(r"(?is)<(?:script|style|svg|noscript|template|nav|footer)[^>]*>.*?</(?:script|style|svg|noscript|template|nav|footer)>", " ", html)
    article = re.search(r"(?is)<article\b[^>]*>(.*?)</article>", text)
    if article:
        text = article.group(1)
    else:
        main = re.search(r"(?is)<main\b[^>]*>(.*?)</main>", text)
        if main:
            text = main.group(1)
    text = re.sub(r"(?is)<!--.*?-->", " ", text)
    text = _clean(text)
    return text[:limit]

def _direct_candidate(item: dict) -> bool:
    # Only hydrate direct web-index results. Google/Bing News aggregator URLs
    # may require consent/redirect logic and are already usable as indexed evidence.
    provider = _clean(item.get("provider", "")).lower()
    if provider not in {"bing-web", "duckduckgo-web", "gdelt", "direct-web"}:
        return False
    link = _safe_https(item.get("url", ""))
    if not link:
        return False
    try:
        host = (urlparse(link).hostname or "").lower()
    except Exception:
        return False
    return bool(host and host not in DIRECT_SKIP_HOSTS)

def _enrich_direct_item(item: dict, timeout: int = 6) -> tuple[dict, bool]:
    if not _direct_candidate(item):
        return item, False
    link = _safe_https(item.get("url", ""))
    req = Request(
        link,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            if getattr(response, "status", 200) >= 400:
                return item, False
            content_type = str(response.headers.get("content-type", "")).lower()
            if "html" not in content_type:
                return item, False
            raw = response.read(700_000)
            final_url = _safe_https(getattr(response, "geturl", lambda: link)())
    except Exception:
        return item, False

    html = raw.decode("utf-8", errors="replace")
    title = (
        _meta_content(html, "og:title")
        or _meta_content(html, "twitter:title")
    )
    if not title:
        match = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
        title = _clean(match.group(1)) if match else ""

    description = (
        _meta_content(html, "description")
        or _meta_content(html, "og:description")
        or _meta_content(html, "twitter:description")
    )
    body_text = _visible_html_text(html)
    summary_parts = []
    for part in [description, body_text]:
        part = _clean(part)
        if part and part not in summary_parts:
            summary_parts.append(part)
    summary = " ".join(summary_parts).strip()[:5000]

    if len(summary) < 120:
        return item, False

    enriched = dict(item)
    if final_url:
        enriched["url"] = final_url
    if title and len(title) >= 8:
        enriched["title"] = title[:500]
    enriched["summary"] = summary
    image = _safe_https(
        _meta_content(html, "og:image")
        or _meta_content(html, "twitter:image")
    )
    if image:
        enriched["image_url"] = image

    try:
        host = (urlparse(enriched["url"]).hostname or "").lower().removeprefix("www.")
    except Exception:
        host = ""
    generic = _clean(enriched.get("source_name", "")).lower()
    if host and (not generic or generic.startswith(("bing web", "bing news", "gdelt"))):
        enriched["source_name"] = host[:200]

    enriched["verified_direct"] = True
    enriched["hash"] = hashlib.sha256(
        f"{enriched.get('title','')}|{enriched.get('url','')}".encode("utf-8")
    ).hexdigest()
    return enriched, True

def _enrich_direct_sources(items: list[dict], max_checks: int = 14) -> list[dict]:
    if not items:
        return []

    indexed = list(enumerate(items))
    candidates = [(idx, item) for idx, item in indexed if _direct_candidate(item)][:max_checks]
    if not candidates:
        return items

    enriched_by_index = {}
    verified = 0
    with ThreadPoolExecutor(max_workers=min(6, len(candidates))) as pool:
        future_map = {
            pool.submit(_enrich_direct_item, item): idx
            for idx, item in candidates
        }
        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                enriched, ok = future.result()
            except Exception:
                continue
            enriched_by_index[idx] = enriched
            verified += 1 if ok else 0

    out = []
    for idx, item in indexed:
        out.append(enriched_by_index.get(idx, item))
    print(f"TOPIC_DIRECT_OK checked={len(candidates)} enriched={verified}")
    return out

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

def _topic_search_sources(query_text: str, category: str) -> list[dict]:
    encoded = quote_plus(query_text)
    return [
        {
            "name": f"Google News SI – {category} – {query_text[:60]}",
            "category": category,
            "url": (
                "https://news.google.com/rss/search"
                f"?q={encoded}&hl=sl&gl=SI&ceid=SI:sl"
            ),
            "type": "rss",
            "provider": "google-news-si",
        },
        {
            "name": f"Google News EN – {category} – {query_text[:60]}",
            "category": category,
            "url": (
                "https://news.google.com/rss/search"
                f"?q={encoded}&hl=en-US&gl=US&ceid=US:en"
            ),
            "type": "rss",
            "provider": "google-news-global",
        },
        {
            "name": f"Bing News – {category} – {query_text[:60]}",
            "category": category,
            "url": f"https://www.bing.com/news/search?q={encoded}&format=rss",
            "type": "rss",
            "provider": "bing-news",
        },
        {
            "name": f"Bing Web – {category} – {query_text[:60]}",
            "category": category,
            "url": f"https://www.bing.com/search?q={encoded}&format=rss",
            "type": "rss",
            "provider": "bing-web",
        },
    ]

def collect_topic(topic: str, category: str, max_items: int = 30) -> list[dict]:
    queries = _topic_queries(topic)[:6]
    if not queries:
        return []

    provider_hits = {}
    tasks = []

    # Run independent public search indexes concurrently. A single slow or
    # unavailable provider should not make the whole terminal command wait for
    # each timeout in sequence.
    with ThreadPoolExecutor(max_workers=10) as pool:
        order = 0
        for query_text in queries:
            for source in _topic_search_sources(query_text, category):
                provider = source.get("provider", "unknown")
                future = pool.submit(fetch_feed, source, 10, 1)
                tasks.append((order, provider, query_text, future))
                order += 1

            tasks.append((
                order,
                "gdelt",
                query_text,
                pool.submit(_gdelt_news, query_text, category, max_items),
            ))
            order += 1

            tasks.append((
                order,
                "duckduckgo-web",
                query_text,
                pool.submit(_duckduckgo_web, query_text, category, min(max_items, 12)),
            ))
            order += 1

        # Futures already run in parallel; consuming them in submission order
        # keeps source ordering deterministic across runs.
        out = []
        for _, provider, query_text, future in sorted(tasks, key=lambda item: item[0]):
            try:
                found = future.result()
            except Exception as exc:
                print(
                    f"WARN topic source provider={provider} "
                    f"query={query_text!r} error={exc}"
                )
                continue
            if not found:
                continue
            provider_hits[provider] = provider_hits.get(provider, 0) + len(found)
            out.extend(found)

    unique = _dedupe_diverse(out, max_items, per_source=4)
    unique = _enrich_direct_sources(unique, max_checks=min(14, max_items))
    unique = _dedupe_diverse(unique, max_items, per_source=4)
    if unique:
        summary = ",".join(
            f"{name}:{count}" for name, count in sorted(provider_hits.items())
        )
        print(f"TOPIC_SOURCES_OK count={len(unique)} providers={summary}")
    return unique

TOPIC_GENERIC_TERMS = {
    "danes", "danasnjem", "današnjem", "danasnji", "današnji", "aktualno",
    "aktualne", "novice", "novica", "dogajanje", "dogajanju", "dogaja",
    "clanek", "članek", "prispevek", "objava", "objavi", "napisi", "napiši",
    "pripravi", "ustvari", "sestavi", "prosim", "tema", "temo", "glede",
    "center", "centru", "sredisce", "središče", "trenutno", "zdaj", "sedaj",
}


def _topic_rank_terms(topic: str) -> set[str]:
    core = _topic_core(topic)
    terms = set()
    for word in re.findall(r"[A-Za-zČŠŽčšžĆćĐđ0-9-]+", core):
        low = word.lower()
        if len(low) < 4 or low in TOPIC_GENERIC_TERMS:
            continue
        terms.add(low)
    return terms


def topic_relevance_score(topic: str, item: dict) -> int:
    terms = _topic_rank_terms(topic)
    if not terms:
        return 0
    haystack = " ".join([
        str(item.get("title") or ""),
        str(item.get("summary") or ""),
        str(item.get("source_name") or ""),
    ]).lower()
    hay_words = re.findall(r"[a-zčšžćđ0-9-]+", haystack)

    score = 0
    for term in terms:
        if term in haystack:
            score += 2
            continue
        stem = term[:5] if len(term) >= 6 else term
        if any(word.startswith(stem) for word in hay_words):
            score += 1
    return score


def filter_topic_items(topic: str, items: list[dict], *, minimum_score: int = 1) -> list[dict]:
    """Drop search noise instead of merely ranking it.

    A list in which every result is unrelated must become an empty evidence
    set; otherwise the first unrelated page can become a fabricated fallback.
    """
    scored = []
    for index, item in enumerate(items or []):
        relevance = topic_relevance_score(topic, item)
        if relevance < minimum_score:
            continue
        localized = 1 if str(item.get("provider") or "").lower() == "google-news-si" else 0
        direct = 1 if item.get("verified_direct") else 0
        summary_len = min(len(str(item.get("summary") or "")), 5000)
        scored.append((relevance, localized, direct, summary_len, -index, item))
    scored.sort(reverse=True, key=lambda row: row[:-1])
    return [row[-1] for row in scored]


def rank_topic_items(topic: str, items: list[dict]) -> list[dict]:
    """Rank already-relevant sources for an explicit editorial topic."""
    def score(item: dict) -> tuple:
        overlap = topic_relevance_score(topic, item)
        localized = 1 if str(item.get("provider") or "").lower() == "google-news-si" else 0
        direct = 1 if item.get("verified_direct") else 0
        summary_len = min(len(str(item.get("summary") or "")), 5000)
        has_media = 1 if item.get("image_url") or item.get("video_url") else 0
        return (overlap, localized, direct, summary_len, has_media)

    return sorted(list(items or []), key=score, reverse=True)

def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        if item["hash"] in seen:
            continue
        seen.add(item["hash"])
        unique.append(item)
    return unique
