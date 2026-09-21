from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from agent import (  # noqa: E402
    APP,
    BASE,
    PROCESSED,
    STATE,
    allowed_source_urls,
    article_used_items,
    atomic_json,
    automatic_story_pool,
    collect_automatic_sources,
    control,
    enabled,
    existing_titles,
    load_json,
    mark_scheduled_slot_done,
    now,
    prepare_article_candidate,
)
from services.fallback_writer import build_digest  # noqa: E402
from services.publisher import publish_to_app, slugify  # noqa: E402
from services.validator import validate  # noqa: E402
from services.learning import learning_source_ok, rank_sources_with_learning  # noqa: E402


CATEGORY_TERMS = {
    "sport": (
        "šport", "sport", "športn", "nogomet", "košark", "kosark", "tenis",
        "odboj", "rokomet", "hokej", "smuč", "smuc", "koles", "tekma",
        "prvenst", "liga", "turnir", "atlet", "trener", "igral", "gol",
        "uefa", "fifa", "olimp", "medal", "velesovo", "stadion", "klub",
    ),
    "politika": (
        "polit", "vlada", "parlament", "državni zbor", "drzavni zbor",
        "minister", "ministr", "predsed", "zakon", "strank", "koalic",
        "opozic", "volit", "evropska unija", "eu", "bruselj",
    ),
    "aktualno": (
        "sloven", "ljubljan", "maribor", "celje", "kopr", "novice", "danes",
        "aktual", "dogaj", "dogodek", "vreme", "promet", "gospodar", "družb",
        "druzb", "zdrav", "šol", "sol", "kultur",
    ),
}

BAD_AUTONOMOUS_HOSTS = {
    "wikipedia.org",
    "en.wikipedia.org",
    "simple.wikipedia.org",
    "theoreticalminimum.com",
    "stanford.edu",
    "sitp.stanford.edu",
    "physics.stanford.edu",
}


def _source_text(item: dict) -> str:
    return " ".join([
        str(item.get("title") or ""),
        str(item.get("summary") or ""),
        str(item.get("source_name") or ""),
        str(item.get("url") or ""),
    ]).lower()


def _host(url: str) -> str:
    try:
        return (urlparse(str(url or "")).hostname or "").lower().removeprefix("www.")
    except Exception:
        return ""


def _category_relevant(item: dict, category: str) -> bool:
    text = _source_text(item)
    host = _host(str(item.get("url") or ""))

    # Encyclopedia/profile/university pages are not acceptable as autonomous
    # daily news anchors. They caused a physics biography to be published in the
    # sports slot, so block them before the article writer sees them.
    if any(host == bad or host.endswith("." + bad) for bad in BAD_AUTONOMOUS_HOSTS):
        return False
    if not learning_source_ok(item, category):
        return False

    terms = CATEGORY_TERMS.get(category)
    if not terms:
        return True
    if not any(term in text for term in terms):
        return False

    # Sports and politics slots must be clearly category-bound. A generic page
    # that only mentions the category in our wrapper text is not enough, because
    # fallback articles prepend the category name themselves later.
    if category == "sport":
        return any(term in text for term in terms if term not in {"šport", "sport"})
    return True


def _filter_category_pool(items: list[dict], category: str) -> list[dict]:
    filtered = [item for item in items if _category_relevant(item, category)]
    if len(filtered) != len(items):
        print(f"FALLBACK_CATEGORY_GUARD category={category} kept={len(filtered)}/{len(items)}")
    return filtered


def _reset_daily_state(state: dict, today: str) -> dict:
    if state.get("posts_date") != today:
        state["posts_date"] = today
        state["posts_today"] = 0
        state["scheduled_posts_today"] = 0
        state["manual_posts_today"] = 0
        state["scheduled_slots_done"] = []
        state["scheduled_slots_deferred"] = []
        state["last_editorial_hold"] = None
    state.setdefault("scheduled_posts_today", 0)
    state.setdefault("manual_posts_today", 0)
    state.setdefault("scheduled_slots_done", [])
    state.setdefault("scheduled_slots_deferred", [])
    return state


def _write_status(cfg: dict, state: dict, status: str, message: str, output: str | None = None) -> None:
    status_path = BASE / "public/data/agent-status.json"
    atomic_json(str(status_path), {
        "agent": cfg.get("agent_name", "Blog Lab Publisher Agent"),
        "status": status,
        "enabled": enabled(cfg),
        "category": state.get("current_category"),
        "last_run": now().isoformat(timespec="seconds"),
        "last_success": state.get("last_success"),
        "last_output": output or state.get("last_output"),
        "next_run": None,
        "message": message,
        "posts_today": state.get("posts_today", 0),
        "scheduled_posts_today": state.get("scheduled_posts_today", 0),
        "manual_posts_today": state.get("manual_posts_today", 0),
        "writer_mode": state.get("writer_mode", "deterministic_fallback"),
        "scheduled_slots_done": state.get("scheduled_slots_done", []),
        "scheduled_slots_deferred": state.get("scheduled_slots_deferred", []),
        "last_editorial_hold": state.get("last_editorial_hold"),
        "last_error": state.get("last_error"),
    })


def run(category: str, scheduled_slot: str = "", dry_run: bool = False) -> int:
    cfg = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
    state = load_json(str(STATE), {})
    processed = load_json(str(PROCESSED), [])
    today = now().date().isoformat()
    state = _reset_daily_state(state, today)
    state["current_category"] = category

    if not enabled(cfg):
        _write_status(cfg, state, "paused", "Fallback publisher je izklopljen.")
        print("FALLBACK_DISABLED")
        return 0

    if state.get("scheduled_posts_today", 0) >= int(cfg.get("maximum_outputs_per_day", 3)):
        _write_status(cfg, state, "completed", "Dosežena je dnevna omejitev samodejnih objav.")
        print("FALLBACK_DAILY_LIMIT")
        return 0

    items = rank_sources_with_learning(_filter_category_pool(collect_automatic_sources(cfg, category), category), category)
    seen_hashes = {x.get("hash") for x in processed}
    fresh = [x for x in items if x.get("hash") not in seen_hashes]
    source_pool = fresh or items
    source_pool = rank_sources_with_learning(_filter_category_pool(source_pool, category), category)
    evidence_pool = automatic_story_pool(source_pool, category, max_items=6)
    evidence_pool = rank_sources_with_learning(_filter_category_pool(evidence_pool, category), category)
    if not evidence_pool:
        state["last_error"] = "fallback_no_category_evidence"
        atomic_json(str(STATE), state)
        _write_status(cfg, state, "waiting", "Fallback ni našel dovolj preverljivih virov za zahtevano kategorijo.")
        print("FALLBACK_NO_CATEGORY_EVIDENCE")
        return 0

    article = build_digest(evidence_pool, category)
    if article.get("skip"):
        state["last_error"] = str(article.get("reason") or "fallback_skip")[:240]
        atomic_json(str(STATE), state)
        _write_status(cfg, state, "waiting", state["last_error"])
        print("FALLBACK_SKIP")
        return 0

    used_for_article = article_used_items(article, evidence_pool)
    if not used_for_article:
        used_for_article = evidence_pool[:1]
    used_for_article = _filter_category_pool(used_for_article, category)
    if not used_for_article:
        state["last_error"] = "fallback_used_sources_failed_category_guard"
        atomic_json(str(STATE), state)
        _write_status(cfg, state, "waiting", "Fallback viri niso prestali kategorijskega preverjanja.")
        print("FALLBACK_USED_SOURCES_FAILED_CATEGORY_GUARD")
        return 0

    article = prepare_article_candidate(article, used_for_article, "", "")
    article["fallback"] = True
    article["id"] = slugify(article.get("title", "")) + "-" + hashlib.sha1(
        str(used_for_article[0].get("url", "fallback")).encode("utf-8")
    ).hexdigest()[:8]

    min_chars = int(cfg["min_article_chars"])
    max_chars = int(cfg["max_article_chars"])
    titles = existing_titles()
    used_urls = {x.get("url") for x in processed if x.get("url")}
    allowed_urls = allowed_source_urls(evidence_pool)
    errors = validate(article, min_chars, max_chars, titles, used_urls, allowed_urls)
    if errors:
        diag = BASE / "logs" / f"fallback-failed-{now().strftime('%Y%m%d-%H%M%S')}.json"
        diag.parent.mkdir(parents=True, exist_ok=True)
        diag.write_text(
            json.dumps({"category": category, "errors": errors, "article": article}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        state["last_error"] = ",".join(errors)
        atomic_json(str(STATE), state)
        _write_status(cfg, state, "waiting", "Fallback QA ni uspel: " + ",".join(errors))
        print("FALLBACK_QA_FAILED " + ",".join(errors))
        return 0

    if dry_run:
        draft = BASE / "content/drafts" / f"{article['id']}.json"
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        _write_status(cfg, state, "needs_review", "Fallback osnutek je shranjen.", str(draft))
        print("FALLBACK_DRY_RUN_OK")
        return 0

    publish_to_app(str(APP), article, cfg["agent_name"])
    cited_items = article_used_items(article, evidence_pool)
    for item in cited_items:
        processed.append({**item, "processed_at": now().isoformat(timespec="seconds"), "output_id": article["id"]})
    atomic_json(str(PROCESSED), processed[-750:])

    state.update({
        "last_success": now().isoformat(timespec="seconds"),
        "last_output": article["id"],
        "last_error": None,
        "consecutive_failures": 0,
        "posts_date": today,
        "posts_today": state.get("posts_today", 0) + 1,
        "scheduled_posts_today": state.get("scheduled_posts_today", 0) + 1,
        "manual_posts_today": state.get("manual_posts_today", 0),
        "agent_version": "3.0.0-learning-guarded-fallback",
        "current_category": category,
        "writer_mode": "deterministic_fallback",
        "last_editorial_hold": None,
    })
    if scheduled_slot:
        mark_scheduled_slot_done(state, scheduled_slot)
    atomic_json(str(STATE), state)
    _write_status(cfg, state, "completed", "Fallback članek je objavljen brez zunanjega AI providerja.", article["id"])
    print(f"FALLBACK_PUBLISHED:{article['id']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", choices=["sport", "politika", "aktualno"], required=True)
    ap.add_argument("--scheduled-slot", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return run(args.category, args.scheduled_slot, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
