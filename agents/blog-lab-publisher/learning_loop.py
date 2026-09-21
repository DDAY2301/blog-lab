from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

import yaml

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
sys.path.insert(0, str(HERE))

from agent import (  # noqa: E402
    PROCESSED,
    STATE,
    atomic_json,
    collect_automatic_sources,
    load_json,
    now,
)
from services.learning import STATIC_BLOCKED_HOSTS, host_of, learning_source_score  # noqa: E402

LEARNING = BASE / "data/article-learning.json"
LEARNING_STATUS = BASE / "public/data/article-learning-status.json"
APP = BASE / "src/App.jsx"
LOGS = BASE / "logs"
CATEGORIES = ("sport", "politika", "aktualno")

CATEGORY_RULES = {
    "sport": [
        "Vsak športni članek mora imeti jasno športno jedro že v naslovu ali prvem odstavku.",
        "Ne objavljaj biografij, enciklopedij ali univerzitetnih profilov kot športne novice.",
        "Prednost imajo slovenski športni viri, klubi, zveze, tekme, rezultati in športna infrastruktura.",
    ],
    "politika": [
        "Politične članke piši nevtralno, brez priporočil, ocen kandidatov ali napovedovanja izida.",
        "Loči dokumentirana dejstva od izjav akterjev in mnenjskih interpretacij.",
        "Vsak politični članek mora imeti preverljive vire in jasen časovni okvir.",
    ],
    "aktualno": [
        "Aktualno mora ostati vezano na Slovenijo, lokalno dogajanje ali jasno relevantno evropsko/regionalno temo.",
        "Ne mešaj nepovezanih naslovov v en članek; raje izberi eno zgodbo z najboljšimi viri.",
        "Če so viri šibki, objavi kratek faktografski pregled namesto napihnjene zgodbe.",
    ],
}

GLOBAL_WRITING_RULES = [
    "Naslov naj bo konkreten in naj ne obljublja več, kot viri dokazujejo.",
    "Prvi odstavek mora povedati kaj se je zgodilo, kje, kdaj in zakaj je pomembno.",
    "Vsaka trditev, ki ni splošno znana, mora izhajati iz vira v članku.",
    "Ne zapolnjuj manjkajočih dejstev z ugibanjem ali generičnimi stavki.",
    "Ne ponavljaj dolgih povedi, podnaslovov ali skoraj enakih odstavkov.",
]


def _load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _host(url: str) -> str:
    try:
        return (urlparse(str(url or "")).hostname or "").lower().removeprefix("www.")
    except Exception:
        return ""


def _extract_current_articles() -> list[dict]:
    text = APP.read_text(encoding="utf-8") if APP.exists() else ""
    blocks = re.findall(r'\{\s*\n\s*"id":\s*"([^"]+)"(?P<body>.*?"updatedAt":\s*"[^"]+"\s*\n\s*\})', text, flags=re.S)
    out = []
    for article_id, body in blocks[:40]:
        title = re.search(r'"title":\s*"([^"]+)"', body)
        category = re.search(r'"category":\s*"([^"]+)"', body)
        created = re.search(r'"createdAt":\s*"([^"]+)"', body)
        out.append({
            "id": article_id,
            "title": title.group(1) if title else "",
            "category": category.group(1) if category else "",
            "createdAt": created.group(1) if created else "",
        })
    return out


def _failure_signals() -> list[dict]:
    signals = []
    if LOGS.exists():
        for path in sorted(LOGS.glob("fallback-failed-*.json"))[-20:]:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                signals.append({
                    "file": path.name,
                    "category": data.get("category"),
                    "errors": data.get("errors") or [],
                    "title": (data.get("article") or {}).get("title"),
                })
            except Exception:
                continue
    state = _load(STATE, {})
    if state.get("last_error"):
        signals.append({"file": "agent-state", "category": state.get("current_category"), "errors": [state.get("last_error")]})
    if state.get("last_editorial_hold"):
        hold = state.get("last_editorial_hold") or {}
        signals.append({"file": "agent-state", "category": state.get("current_category"), "errors": [hold.get("reason")], "slot": hold.get("slot")})
    return signals


def _item_quality(item: dict, category: str) -> float:
    score = learning_source_score(item, category)
    title = str(item.get("title") or "")
    summary = str(item.get("summary") or "")
    host = _host(str(item.get("url") or ""))
    text = f"{title} {summary}".lower()

    if len(title) >= 35:
        score += 0.4
    if len(summary) >= 180:
        score += 0.8
    if host.endswith(".si"):
        score += 0.7
    if item.get("verified_direct"):
        score += 0.8
    if "wikipedia" in host or host in STATIC_BLOCKED_HOSTS:
        score -= 5.0
    if category == "sport" and not any(term in text for term in ("šport", "sport", "nogomet", "košark", "tekma", "liga", "klub", "prvenst", "turnir", "trener", "igral")):
        score -= 2.0
    if category == "politika" and not any(term in text for term in ("vlada", "parlament", "polit", "minister", "zakon", "strank", "volit", "predsed")):
        score -= 1.5
    if category == "aktualno" and not any(term in text for term in ("sloven", "ljubljan", "maribor", "aktual", "danes", "dogod", "novice")):
        score -= 0.8
    return round(score, 3)


def _merge_score(old: float, new: float, factor: float = 0.65) -> float:
    try:
        old_f = float(old)
    except Exception:
        old_f = 0.0
    return round(old_f * factor + new * (1 - factor), 3)


def learn_category(cfg: dict, category: str, previous: dict, processed: list[dict]) -> dict:
    previous_health = previous.get("source_health") if isinstance(previous.get("source_health"), dict) else {}
    health: dict[str, dict] = {k: dict(v) for k, v in previous_health.items() if isinstance(v, dict)}
    host_titles: dict[str, list[str]] = defaultdict(list)
    current_items = []
    try:
        current_items = collect_automatic_sources(cfg, category)
    except Exception as exc:
        current_items = []
        print(f"LEARNING_WARN collect_failed category={category} error={exc}")

    for item in current_items[:40]:
        host = host_of(str(item.get("url") or ""))
        if not host:
            continue
        new_score = _item_quality(item, category)
        record = health.get(host, {})
        record["score"] = _merge_score(record.get("score", 0), new_score)
        record["seen"] = int(record.get("seen", 0) or 0) + 1
        record["last_seen"] = now().isoformat(timespec="seconds")
        record["last_title"] = str(item.get("title") or "")[:180]
        record["last_provider"] = str(item.get("provider") or "")[:80]
        host_titles[host].append(str(item.get("title") or "")[:140])
        health[host] = record

    # Reward sources that produced successful articles, because processed items
    # are direct evidence that a source can support publication.
    for item in processed[-250:]:
        if str(item.get("category") or "").lower() != category:
            continue
        host = host_of(str(item.get("url") or ""))
        if not host:
            continue
        record = health.get(host, {})
        record["score"] = _merge_score(record.get("score", 0), 2.5, factor=0.8)
        record["published"] = int(record.get("published", 0) or 0) + 1
        record["last_output_id"] = str(item.get("output_id") or "")[:160]
        health[host] = record

    blocked_hosts = sorted({
        host for host, record in health.items()
        if float(record.get("score", 0) or 0) <= -4
    } | {host for host in STATIC_BLOCKED_HOSTS})

    ranked_hosts = sorted(
        health.items(),
        key=lambda row: (-float(row[1].get("score", 0) or 0), row[0]),
    )[:25]

    return {
        "last_learning_run": now().isoformat(timespec="seconds"),
        "learning_mode": "continuous_24h",
        "writing_rules": CATEGORY_RULES.get(category, []),
        "blocked_hosts": blocked_hosts[:40],
        "preferred_hosts": [host for host, _ in ranked_hosts[:12]],
        "source_health": {host: record for host, record in ranked_hosts},
        "current_source_count": len(current_items),
        "example_titles": {
            host: titles[:3]
            for host, titles in list(host_titles.items())[:12]
        },
    }


def run(mode: str = "continuous") -> int:
    cfg = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
    previous = _load(LEARNING, {})
    processed = _load(PROCESSED, [])
    articles = _extract_current_articles()
    failures = _failure_signals()

    categories_prev = previous.get("categories") if isinstance(previous.get("categories"), dict) else {}
    categories = {}
    for category in CATEGORIES:
        categories[category] = learn_category(cfg, category, categories_prev.get(category, {}), processed)

    failure_counter = Counter()
    for failure in failures:
        for error in failure.get("errors") or []:
            if error:
                failure_counter[str(error)] += 1

    learning = {
        "version": "1.0.0-continuous-learning",
        "mode": mode,
        "updated_at": now().isoformat(timespec="seconds"),
        "loop_count": int(previous.get("loop_count", 0) or 0) + 1,
        "global_writing_rules": GLOBAL_WRITING_RULES,
        "global_news_rules": [
            "Prednost imajo sveži slovenski viri z dovolj dolgim povzetkom ali neposredno preverjeno vsebino.",
            "Če vir večkrat sproži napačno kategorijo, se njegova ocena zniža in ga fallback ne uporablja več.",
            "Če ni dovolj dokazov za članek, je bolje počakati kot objaviti napačno temo.",
        ],
        "categories": categories,
        "recent_articles": articles[:12],
        "recent_failures": failures[-12:],
        "failure_summary": dict(failure_counter.most_common(12)),
    }
    atomic_json(str(LEARNING), learning)

    status = {
        "status": "learning_completed",
        "updated_at": learning["updated_at"],
        "loop_count": learning["loop_count"],
        "categories_checked": list(CATEGORIES),
        "recent_article_count": len(articles),
        "recent_failure_count": len(failures),
        "mode": mode,
    }
    atomic_json(str(LEARNING_STATUS), status)
    print("LEARNING_COMPLETED " + json.dumps(status, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="continuous", choices=["continuous", "manual", "after_publish"])
    args = parser.parse_args()
    return run(args.mode)


if __name__ == "__main__":
    raise SystemExit(main())
