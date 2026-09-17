from __future__ import annotations
import hashlib
import time
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

USER_AGENT = "BlogLabPublisher/1.0 (+https://github.com/DDAY2301/blog-lab)"

def _text(node, names):
    for name in names:
        el = node.find(name)
        if el is not None and el.text:
            return el.text.strip()
    return ""

def _clean(value):
    return " ".join((value or "").replace("\x00", "").split())

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
                    title = _clean(_text(n, ["title"]))
                    link = _clean(_text(n, ["link"]))
                    summary = _clean(_text(n, ["description"]))
                    published = _clean(_text(n, ["pubDate"]))
                    if title and link:
                        items.append(_item(source, title, link, summary, published))
                return items
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for n in root.findall(".//a:entry", ns):
                title = _clean(_text(n, ["{http://www.w3.org/2005/Atom}title"]))
                link_el = n.find("{http://www.w3.org/2005/Atom}link")
                link = _clean(link_el.attrib.get("href", "") if link_el is not None else "")
                summary = _clean(_text(n, ["{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content"]))
                published = _clean(_text(n, ["{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated"]))
                if title and link:
                    items.append(_item(source, title, link, summary, published))
            return items
        except Exception as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Vir ni dosegljiv: {url}: {last}")

def _item(source, title, link, summary, published):
    material = f"{title}|{link}".encode("utf-8")
    return {"source_name": source.get("name", source["url"]), "title": title[:500], "url": link[:2000], "summary": summary[:4000], "published": published[:200], "hash": hashlib.sha256(material).hexdigest()}

def collect(sources: list[dict], max_items: int = 20) -> list[dict]:
    out = []
    for source in sources:
        try:
            out.extend(fetch_feed(source))
        except Exception as exc:
            print(f"WARN source={source.get('url')} error={exc}")
    return out[:max_items]
