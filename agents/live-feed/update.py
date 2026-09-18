from __future__ import annotations
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public" / "live-feed.json"
RSS_URL = "https://news.google.com/rss?hl=sl&gl=SI&ceid=SI:sl"
MAX_ITEMS = 10

def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", unescape(value or ""))
    return " ".join(value.split()).strip()

def fetch() -> bytes:
    req = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "BlogLabLiveFeed/1.0 (+https://dday2301.github.io/blog-lab/)"}
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read()

def iso_date(raw: str) -> str:
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return ""

def build(xml_bytes: bytes) -> dict:
    root = ET.fromstring(xml_bytes)
    items = []
    seen = set()
    for node in root.findall(".//item"):
        title = clean(node.findtext("title", ""))
        link = clean(node.findtext("link", ""))
        published = clean(node.findtext("pubDate", ""))
        source = clean(node.findtext("source", ""))
        if not title or not link:
            continue
        key = (title.lower(), link)
        if key in seen:
            continue
        seen.add(key)
        items.append({
            "title": title[:220],
            "url": link[:2000],
            "source": source[:100] or "Google News",
            "publishedAt": iso_date(published),
        })
        if len(items) >= MAX_ITEMS:
            break
    return {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "fresh",
        "items": items,
    }

def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = build(fetch())
        if not data["items"]:
            raise RuntimeError("RSS returned no usable items")
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"LIVE_FEED_UPDATED {len(data['items'])}")
        return 0
    except Exception as exc:
        print(f"LIVE_FEED_WARNING {type(exc).__name__}: {exc}")
        if OUT.exists():
            try:
                current = json.loads(OUT.read_text(encoding="utf-8"))
            except Exception:
                current = {"items": []}
            current["status"] = "stale"
            current["lastErrorAt"] = datetime.now(timezone.utc).isoformat()
            OUT.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return 0
        OUT.write_text(json.dumps({
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "status": "unavailable",
            "items": [],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
