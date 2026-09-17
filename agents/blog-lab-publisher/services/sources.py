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

def _item(source, title, link, summary, published):
    material = f"{title}|{link}".encode("utf-8")
    return {
        "source_name": source.get("name", source["url"]),
        "category": source.get("category", "aktualno"),
        "title": _clean(title)[:500],
        "url": _clean(link)[:2000],
        "summary": _clean(summary)[:4000],
        "published": _clean(published)[:200],
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
                        items.append(_item(source, title, link, summary, published))
                return items
            nsurl = "http://www.w3.org/2005/Atom"
            for n in root.findall(f".//{{{nsurl}}}entry"):
                title = _text(n, [f"{{{nsurl}}}title"])
                link_el = n.find(f"{{{nsurl}}}link")
                link = link_el.attrib.get("href", "") if link_el is not None else ""
                summary = _text(n, [f"{{{nsurl}}}summary", f"{{{nsurl}}}content"])
                published = _text(n, [f"{{{nsurl}}}published", f"{{{nsurl}}}updated"])
                if title and link:
                    items.append(_item(source, title, link, summary, published))
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

def collect_topic(topic: str, category: str, max_items: int = 30) -> list[dict]:
    query = quote_plus((topic or "").strip())
    if not query:
        return []
    source = {
        "name": f"Google News – {category}",
        "category": category,
        "url": f"https://news.google.com/rss/search?q={query}&hl=sl&gl=SI&ceid=SI:sl",
        "type": "rss",
    }
    try:
        return _dedupe(fetch_feed(source))[:max_items]
    except Exception as exc:
        print(f"WARN topic source error={exc}")
        return []

def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        if item["hash"] in seen:
            continue
        seen.add(item["hash"])
        unique.append(item)
    return unique
