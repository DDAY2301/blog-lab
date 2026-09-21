from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parents[3]
LEARNING_PATH = BASE / "data/article-learning.json"

STATIC_BLOCKED_HOSTS = {
    "namu.wiki",
    "wikipedia.org",
    "en.wikipedia.org",
    "simple.wikipedia.org",
    "theoreticalminimum.com",
    "stanford.edu",
    "sitp.stanford.edu",
    "physics.stanford.edu",
}


def host_of(url: str) -> str:
    try:
        return (urlparse(str(url or "")).hostname or "").lower().removeprefix("www.")
    except Exception:
        return ""


def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_learning() -> dict:
    data = _load_json(LEARNING_PATH, {})
    return data if isinstance(data, dict) else {}


def _category_memory(memory: dict, category: str) -> dict:
    categories = memory.get("categories") if isinstance(memory.get("categories"), dict) else {}
    value = categories.get(str(category or "").lower(), {})
    return value if isinstance(value, dict) else {}


def learning_source_ok(item: dict, category: str) -> bool:
    """Return whether learned memory allows this source for autonomous publishing."""
    host = host_of(str(item.get("url") or ""))
    if not host:
        return False
    if any(host == bad or host.endswith("." + bad) for bad in STATIC_BLOCKED_HOSTS):
        return False

    memory = load_learning()
    cat = _category_memory(memory, category)
    blocked = set(cat.get("blocked_hosts") or []) | set(memory.get("blocked_hosts") or [])
    if any(host == bad or host.endswith("." + bad) for bad in blocked):
        return False

    host_health = cat.get("source_health") if isinstance(cat.get("source_health"), dict) else {}
    record = host_health.get(host, {}) if isinstance(host_health.get(host, {}), dict) else {}
    # A very low learned score means this host repeatedly produced unusable or
    # off-category material. Do not permanently block mild negative scores.
    if float(record.get("score", 0) or 0) <= -4:
        return False
    return True


def learning_source_score(item: dict, category: str) -> float:
    host = host_of(str(item.get("url") or ""))
    if not host:
        return -10.0
    memory = load_learning()
    cat = _category_memory(memory, category)
    health = cat.get("source_health") if isinstance(cat.get("source_health"), dict) else {}
    record = health.get(host, {}) if isinstance(health.get(host, {}), dict) else {}

    score = float(record.get("score", 0) or 0)
    provider = str(item.get("provider") or "").lower()
    summary = str(item.get("summary") or "")
    source_name = str(item.get("source_name") or "")

    if provider == "google-news-si":
        score += 1.0
    if host.endswith(".si"):
        score += 0.8
    if item.get("verified_direct"):
        score += 1.2
    if len(summary) >= 220:
        score += 0.7
    if source_name and source_name.lower() not in {"google news", "bing", "duckduckgo"}:
        score += 0.3
    if any(host == bad or host.endswith("." + bad) for bad in STATIC_BLOCKED_HOSTS):
        score -= 10.0
    return score


def rank_sources_with_learning(items: list[dict], category: str) -> list[dict]:
    indexed = list(enumerate(items or []))
    indexed.sort(
        key=lambda pair: (
            -learning_source_score(pair[1], category),
            pair[0],
        )
    )
    return [item for _, item in indexed]
