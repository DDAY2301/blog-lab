"""Cost-free, bounded search diversification for autonomous Slovenian articles.

This is a *discovery* layer, not a weaker publishing rule: candidates still
pass automatic_source_usable, learning policy and the full editorial QA.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from zoneinfo import ZoneInfo

from services import sources
from services.validator import _canonical_url


# Narrow, distinct beats repeating one enormous keyword soup every 15 minutes.
# No unstable API keys, speculative facts, or artificially generated sources.
CATEGORY_LENSES = {
    "kolesarstvo": (
        "Slovenija kolesarske poti nove označene trase",
        "Slovenija gravel kolesarstvo turistične poti",
        "Slovenija gorsko kolesarjenje traili varnost",
        "Slovenija kolesarske prireditve lokalne poti",
        "Slovenija kolesarski turizem razvoj infrastrukture",
        "Slovenija daljinske kolesarske poti občine",
    ),
    "dediscina": (
        "Slovenija kulturna dediščina muzejska razstava",
        "Slovenija arheologija zgodovinska odkritja muzeji",
        "Slovenija obnova gradov kulturnih spomenikov",
        "Slovenija nesnovna dediščina ljudska tradicija",
        "Slovenija zgodovinski muzeji nove zbirke",
        "Slovenija Plečnik arhitektura kulturna dediščina",
    ),
    "sezonsko": (
        "Slovenija jesenski izleti turistični dogodki",
        "Slovenija zimski turizem sezonski dogodki",
        "Slovenija pomladni izleti festival turizem",
        "Slovenija poletne prireditve naravni parki",
        "Slovenija turistične destinacije sezonske prireditve",
        "Slovenija vremenske razmere izleti obiskovalci",
    ),
    "gore": (
        "Slovenija planinske poti PZS vzdrževanje",
        "Slovenija pohodništvo gorske koče planinstvo",
        "Slovenija gore varnost reševanje pohodniki",
        "Slovenija trail tek gorska prireditev",
        "Slovenija kampiranje naravni parki pravila",
        "Slovenija pohodniške poti hribovje obnova",
    ),
    "gourmet": (
        "Slovenija gastronomski dogodki lokalne jedi",
        "Slovenija tradicionalne jedi kulinarična dediščina",
        "Slovenija lokalni pridelovalci gastronomski turizem",
        "Slovenija restavracije sezonska ponudba kulinarika",
        "Slovenija kulinarični festivali lokalna hrana",
        "Slovenija regionalni recepti tradicionalna kuhinja",
    ),
}


def focused_queries(category: str, *, day: date | None = None, count: int = 2) -> list[str]:
    """Two complementary lenses rotate by Slovenia-local day, no random loops."""
    lenses = CATEGORY_LENSES.get(category, ())
    if not lenses:
        return []
    if day is None:
        day = datetime.now(ZoneInfo("Europe/Ljubljana")).date()
    start = day.toordinal() % len(lenses)
    positions = [start, (start + max(1, len(lenses) // 2)) % len(lenses)]
    return [lenses[i] for i in positions[:max(1, min(count, 2))]]


def _title_key(title: str) -> str:
    folded = unicodedata.normalize("NFKD", str(title or "").lower())
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return " ".join(re.findall(r"[a-z0-9]+", folded))


def unpublished_items(items: list[dict], processed: list[dict], *, limit: int = 30) -> list[dict]:
    """Remove old/duplicate sources *before* expensive writing or media lookup."""
    used_urls = {
        canonical for row in processed or []
        if isinstance(row, dict)
        if (canonical := _canonical_url(str(row.get("url") or "")))
    }
    used_hashes = {
        str(row.get("hash")) for row in processed or []
        if isinstance(row, dict) and row.get("hash")
    }
    used_titles = {
        key for row in processed or []
        if isinstance(row, dict)
        if (key := _title_key(row.get("title") or "")) and len(key) >= 24
    }
    out, seen_urls, seen_hashes = [], set(), set()
    for item in items or []:
        if not isinstance(item, dict):
            continue
        canonical = _canonical_url(str(item.get("url") or ""))
        fingerprint = str(item.get("hash") or "")
        title_key = _title_key(item.get("title") or "")
        if not canonical or canonical in used_urls or canonical in seen_urls:
            continue
        if fingerprint and (fingerprint in used_hashes or fingerprint in seen_hashes):
            continue
        if title_key and len(title_key) >= 24 and title_key in used_titles:
            continue
        out.append(item)
        seen_urls.add(canonical)
        if fingerprint:
            seen_hashes.add(fingerprint)
        if len(out) >= limit:
            break
    return out


def collect_focused_sources(
    category: str, *, max_items: int = 30, day: date | None = None
) -> list[dict]:
    """Bounded provider-diverse fallback (<=6 feed requests, <=8 page checks)."""
    queries = focused_queries(category, day=day)
    if not queries:
        return []
    tasks = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for query in queries:
            for spec in sources._topic_search_sources(query, category):
                if spec.get("provider") in {"google-news-si", "bing-web"}:
                    tasks.append((query, spec["provider"], pool.submit(sources.fetch_feed, spec, 8, 1)))
            tasks.append((
                query, "duckduckgo-web",
                pool.submit(sources._duckduckgo_web, query, category, 10),
            ))
        results, counts = [], {}
        for query, provider, future in tasks:
            try:
                fetched = future.result()
            except Exception as exc:
                # No API-key or quota bypass; one unavailable source cannot block another.
                print(
                    f"DISCOVERY_V2_PROVIDER_WARN provider={provider} "
                    f"query={query!r} error={str(exc)[:140]}"
                )
                continue
            counts[provider] = counts.get(provider, 0) + len(fetched or [])
            results.extend(fetched or [])

    diverse = sources._dedupe_diverse(results, max_items, per_source=3)
    enriched = sources._enrich_direct_sources(diverse, max_checks=min(8, max_items))
    final = sources._dedupe_diverse(enriched, max_items, per_source=3)
    print(
        f"DISCOVERY_V2_RAW category={category} queries={len(queries)} "
        f"selected={len(final)} providers="
        + ",".join(f"{k}:{counts[k]}" for k in sorted(counts))
    )
    return final
