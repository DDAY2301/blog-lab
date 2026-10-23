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
    automatic_source_usable,
    collect_automatic_sources,
    control,
    enabled,
    existing_titles,
    load_json,
    mark_scheduled_slot_done,
    now,
    prepare_article_candidate,
    normalize_current_schedule_counter,
    OUTPUT_CATEGORY_LABELS,
)
from services.fallback_writer import build_digest  # noqa: E402
from services.publisher import publish_to_app, slugify  # noqa: E402
from services.validator import validate, _canonical_url  # noqa: E402
from services.source_discovery_v2 import collect_focused_sources, unpublished_items  # noqa: E402
from services.editorial_guard import validate_automatic_story  # noqa: E402
from services.image_optimizer import optimize_commons_hero  # noqa: E402
from services.learning import learning_source_ok, rank_sources_with_learning  # noqa: E402


CATEGORY_TERMS = {
    "kolesarstvo": (
        "koles", "cycling", "bike", "bicycle", "gravel", "mtb", "pot", "route", "trail",
    ),
    "dediscina": (
        "dedišč", "dedisc", "heritage", "zgodovin", "history", "grad", "castle",
        "muzej", "museum", "mit", "myth", "legend", "legenda", "tradic", "folklor",
    ),
    "sezonsko": (
        "turiz", "tourism", "izlet", "visit", "sezon", "vreme", "weather", "arso",
        "dogodek", "festival", "ljubljan", "bled", "bohinj", "piran", "sloven",
    ),
    "gore": (
        "gora", "mountain", "planin", "hiking", "pohod", "trail", "pzs", "triglav",
        "koča", "koca", "bivak", "kamp", "camping", "vreme", "sneg", "varnost",
    ),
    "gourmet": (
        "kulinar", "cuisine", "gourmet", "food", "hrana", "jed", "recept", "restavr",
        "gostil", "vino", "wine", "sir", "tradicional", "gastronom", "lokaln",
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
    return True


def _filter_category_pool(items: list[dict], category: str) -> list[dict]:
    filtered = [item for item in items if _category_relevant(item, category)]
    if len(filtered) != len(items):
        print(f"FALLBACK_CATEGORY_GUARD category={category} kept={len(filtered)}/{len(items)}")
    return filtered



def _fresh_story_pools(
    items: list[dict], processed: list[dict], category: str, max_attempts: int = 4
) -> list[list[dict]]:
    """Try distinct *unpublished* stories; never recycle old evidence as fallback.

    Compare both hashes and normalized URLs because RSS tracking parameters can
    change without making an already-published article a new source.
    """
    used_hashes = {str(row["hash"]) for row in processed if row.get("hash")}
    used_urls = {
        canonical for row in processed
        if (canonical := _canonical_url(str(row.get("url") or "")))
    }
    filtered = [
        item for item in _filter_category_pool(items, category)
        if _canonical_url(str(item.get("url") or ""))
        and _canonical_url(str(item.get("url") or "")) not in used_urls
        and (not item.get("hash") or str(item["hash"]) not in used_hashes)
    ]
    remaining = rank_sources_with_learning(filtered, category)
    pools = []
    for _ in range(max_attempts):
        if not remaining:
            break
        pool = automatic_story_pool(remaining, category, max_items=5)
        if not pool:
            break
        pools.append(pool)
        # Remove this entire story from consideration, not just its lead.
        # Otherwise the next attempt can reselect the same rejected story.
        selected_urls = {_canonical_url(str(x.get("url") or "")) for x in pool}
        remaining = [
            item for item in remaining
            if _canonical_url(str(item.get("url") or "")) not in selected_urls
        ]
    print(
        f"FALLBACK_FRESH_STORIES category={category} fresh={len(filtered)} "
        f"attempts={len(pools)}"
    )
    return pools

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
    return normalize_current_schedule_counter(state)


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
    primary_pools = _fresh_story_pools(items, processed, category, max_attempts=4)

    min_chars = int(cfg["min_article_chars"])
    max_chars = int(cfg["max_article_chars"])
    titles = existing_titles()
    used_urls = {str(x.get("url")) for x in processed if x.get("url")}
    output_category = OUTPUT_CATEGORY_LABELS.get(category, category)
    diagnostics = []

    def evaluate(pools: list[list[dict]], attempt_offset: int = 0):
        for attempt, pool in enumerate(pools, start=attempt_offset + 1):
            candidate = build_digest(pool, category)
            if candidate.get("skip"):
                errors = [str(candidate.get("reason") or "fallback_skip")]
            else:
                used_for_article = _filter_category_pool(article_used_items(candidate, pool), category)
                if not used_for_article:
                    errors = ["fallback_used_sources_failed_category_guard"]
                else:
                    candidate = prepare_article_candidate(candidate, used_for_article, "", output_category)
                    candidate["category"] = output_category
                    candidate["fallback"] = True
                    candidate["id"] = slugify(candidate.get("title", "")) + "-" + hashlib.sha1(
                        str(used_for_article[0].get("url", "fallback")).encode("utf-8")
                    ).hexdigest()[:8]
                    errors = validate(
                        candidate, min_chars, max_chars, titles, used_urls, allowed_source_urls(pool)
                    )
                    errors.extend(validate_automatic_story(candidate, pool, category))
                    errors = list(dict.fromkeys(errors))
            if errors:
                diagnostics.append({
                    "attempt": attempt,
                    "lead_url": str(pool[0].get("url") or ""),
                    "title": str(pool[0].get("title") or "")[:180],
                    "errors": errors,
                })
                print(f"FALLBACK_CANDIDATE_REJECTED attempt={attempt} reasons={','.join(errors)}")
                continue
            print(f"FALLBACK_CANDIDATE_ACCEPTED attempt={attempt} id={candidate['id']}")
            return candidate, pool
        return None, []

    article, evidence_pool = evaluate(primary_pools)

    # Even a *new* indexed headline can lack a valid image or enough evidence.
    # Do not abandon the scheduled slot after failing these QA gates; use a
    # bounded second source-discovery pass rather than weaken the gates.
    if article is None:
        tried_urls = [
            {"url": row.get("url", ""), "title": row.get("title", "")}
            for pool in primary_pools for row in pool
        ]
        discovered = collect_focused_sources(
            category, max_items=int(cfg.get("max_source_items", 30)),
            cache_dir=os.environ.get("RUNNER_TEMP"),
        )
        qualified = [
            item for item in discovered
            if automatic_source_usable(item, category, trusted_primary=False)
            and learning_source_ok(item, category)
        ]
        excluded = processed + tried_urls
        fresh = unpublished_items(qualified, excluded, limit=int(cfg.get("max_source_items", 30)))
        extra_pools = _fresh_story_pools(fresh, excluded, category, max_attempts=3)
        print(
            f"DISCOVERY_V2_RETRY category={category} candidates={len(discovered)} "
            f"usable={len(qualified)} fresh={len(fresh)} pools={len(extra_pools)} "
            f"prior_rejections={len(diagnostics)}"
        )
        article, evidence_pool = evaluate(extra_pools, attempt_offset=len(primary_pools))

    if article is None and not diagnostics:
        state["last_error"] = "fallback_no_fresh_evidence"
        atomic_json(str(STATE), state)
        _write_status(cfg, state, "waiting", "Ni novih neuporabljenih virov; objava se varno odloži.")
        print("FALLBACK_NO_FRESH_EVIDENCE")
        return 0

    if article is None:
        reasons = list(dict.fromkeys(reason for item in diagnostics for reason in item["errors"]))
        diag = BASE / "logs" / f"fallback-failed-{now().strftime('%Y%m%d-%H%M%S')}.json"
        diag.parent.mkdir(parents=True, exist_ok=True)
        # Keep the legacy top-level error/title keys for the 24h learning agent.
        diag.write_text(
            json.dumps({
                "category": category,
                "errors": reasons,
                "article": {"title": diagnostics[0]["title"]} if diagnostics else {},
                "attempts": diagnostics,
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        state["last_error"] = ",".join(reasons)[:240] or "fallback_no_acceptable_story"
        atomic_json(str(STATE), state)
        _write_status(cfg, state, "waiting", "Nobena sveža zgodba ni prestala uredniškega QA: " + state["last_error"])
        print("FALLBACK_QA_FAILED " + state["last_error"])
        return 0

    if dry_run:
        draft = BASE / "content/drafts" / f"{article['id']}.json"
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        _write_status(cfg, state, "needs_review", "Fallback osnutek je shranjen.", str(draft))
        print("FALLBACK_DRY_RUN_OK")
        return 0

    article = optimize_commons_hero(article, BASE / "public")
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
    ap.add_argument("--category", choices=sorted(OUTPUT_CATEGORY_LABELS), required=True)
    ap.add_argument("--scheduled-slot", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return run(args.category, args.scheduled_slot, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
