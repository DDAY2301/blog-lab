from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

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

    items = collect_automatic_sources(cfg, category)
    seen_hashes = {x.get("hash") for x in processed}
    fresh = [x for x in items if x.get("hash") not in seen_hashes]
    source_pool = fresh or items
    evidence_pool = automatic_story_pool(source_pool, category, max_items=6)
    if not evidence_pool:
        state["last_error"] = "fallback_no_evidence"
        atomic_json(str(STATE), state)
        _write_status(cfg, state, "waiting", "Fallback ni našel dovolj preverljivih virov.")
        print("FALLBACK_NO_EVIDENCE")
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
        "agent_version": "2.8.0-autonomous-fallback",
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
