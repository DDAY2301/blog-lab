from __future__ import annotations
import json
import re
import urllib.request
from html import unescape
from urllib.parse import quote, urlencode

API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "BlogLabSloveniaMedia/1.0 (+https://bloglab.eu/)"
CATEGORY_FALLBACKS = {
    "kolesarstvo": "cycling Slovenia landscape",
    "dediščina": "Slovenia cultural heritage castle",
    "dediscina": "Slovenia cultural heritage castle",
    "sezonsko": "Slovenia tourism landscape",
    "gore & traili": "Slovenia mountains hiking",
    "gore": "Slovenia mountains hiking",
    "gourmet": "Slovenian cuisine food",
    "vodniki": "Slovenia travel landscape",
}
ALLOWED_LICENSE_TOKENS = ("cc by", "cc-by", "cc0", "public domain", "cc by-sa", "cc-by-sa")

def _clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", unescape(str(value or "")))
    return " ".join(value.split()).strip()

def _safe_query(value: str) -> str:
    return " ".join(re.findall(r"[A-Za-zÀ-ž0-9'-]+", str(value or ""))[:11]).strip()

def _api(params: dict) -> dict:
    req = urllib.request.Request(API + "?" + urlencode(params), headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read(2_000_000).decode("utf-8", errors="replace"))

def _search_once(query: str) -> dict | None:
    payload = _api({
        "action":"query","generator":"search","gsrnamespace":"6","gsrsearch":query,"gsrlimit":"12",
        "prop":"imageinfo","iiprop":"url|extmetadata|mime","iiurlwidth":"1600",
        "format":"json","formatversion":"2","origin":"*"
    })
    for page in (payload.get("query") or {}).get("pages") or []:
        title = str(page.get("title") or "")
        info = (page.get("imageinfo") or [{}])[0]
        if str(info.get("mime") or "").lower() not in {"image/jpeg","image/png","image/webp"}:
            continue
        meta = info.get("extmetadata") or {}
        license_name = _clean((meta.get("LicenseShortName") or {}).get("value",""))
        if not any(token in license_name.lower() for token in ALLOWED_LICENSE_TOKENS):
            continue
        author = _clean((meta.get("Artist") or {}).get("value","")) or "Wikimedia Commons"
        description = _clean((meta.get("ImageDescription") or {}).get("value",""))
        image_url = str(info.get("thumburl") or info.get("url") or "").strip()
        if not image_url.startswith("https://"):
            continue
        source_url = "https://commons.wikimedia.org/wiki/" + quote(title.replace(" ","_"), safe=":_(),-'")
        return {
            "url": image_url,
            "alt": description[:180] or title.replace("File:","").rsplit(".",1)[0],
            "caption": f"{author} · Wikimedia Commons · {license_name}",
            "sourceUrl": source_url,
        }
    return None

def commons_image_for(topic: str, category: str) -> dict | None:
    category_key = str(category or "").strip().lower()
    topic_query = _safe_query(topic)
    attempts = []
    if topic_query:
        attempts.append(f"{topic_query} Slovenia")
    if CATEGORY_FALLBACKS.get(category_key):
        attempts.append(CATEGORY_FALLBACKS[category_key])
    attempts.append("Slovenia tourism landscape")
    seen = set()
    for query in attempts:
        key=query.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        try:
            found=_search_once(query)
        except Exception as exc:
            print(f"WARN commons media query={query!r} error={type(exc).__name__}: {exc}")
            continue
        if found:
            print(f"COMMONS_MEDIA_SELECTED query={query!r} source={found.get('sourceUrl','')}")
            return found
    return None
