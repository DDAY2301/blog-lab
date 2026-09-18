from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import yaml

BASE = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from services.sources import collect, collect_topic
from services.ai_provider import generate, AIUnavailable
from services.fallback_writer import build_digest
from services.validator import validate
from services.publisher import publish_to_app, slugify
from services.state import load_json, atomic_json

STATE = BASE / "data/agent-state.json"
CONTROL = BASE / "data/agent-control.json"
PROCESSED = BASE / "data/processed-items.json"
STATUS = BASE / "public/data/agent-status.json"
APP = BASE / "src/App.jsx"
VALID_CATEGORIES = {"sport", "politika", "aktualno"}

def operator_media(topic: str) -> tuple[list[dict], dict | None]:
    urls = re.findall(r'https://[^\\s<>"\\']+', topic or "")
    images = []
    video = None
    seen = set()
    for raw in urls:
        url = raw.rstrip(".,);]")
        low = url.lower()
        if url in seen:
            continue
        seen.add(url)
        if re.search(r'\\.(?:jpe?g|png|webp|gif|avif)(?:\\?|$)', low):
            images.append({"url": url, "alt": "", "caption": ""})
        elif ("youtube.com/" in low or "youtu.be/" in low or re.search(r'\\.(?:mp4|webm|ogg)(?:\\?|$)', low)) and video is None:
            video = {"url": url, "title": ""}
    return images[:12], video

def now(): return datetime.now(ZoneInfo("Europe/Ljubljana"))
def control(): return load_json(str(CONTROL), {"enabled": True, "publish_mode": "automatic"})
def enabled(cfg): return cfg.get("enabled", True) and control().get("enabled", True) and os.getenv("AGENT_ENABLED", "true").lower() == "true"
def set_status(cfg, state, value, message="", output=None):
    atomic_json(str(STATUS), {"agent": cfg["agent_name"], "status": value, "enabled": enabled(cfg), "category": state.get("current_category"), "last_run": now().isoformat(timespec="seconds"), "last_success": state.get("last_success"), "last_output": output or state.get("last_output"), "next_run": None, "message": message, "posts_today": state.get("posts_today", 0), "last_error": state.get("last_error")})
def existing_titles() -> set[str]:
    if not APP.exists(): return set()
    text = APP.read_text(encoding="utf-8", errors="ignore")
    return {m.strip().lower() for m in re.findall(r'(?:title|"title")\s*:\s*"([^"]+)"', text)}
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--category", choices=sorted(VALID_CATEGORIES), default=os.getenv("RUN_CATEGORY", "aktualno"))
    ap.add_argument("--topic", default="")
    args = ap.parse_args()
    cfg = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
    state = load_json(str(STATE), {"consecutive_failures": 0, "posts_today": 0, "posts_date": None})
    processed = load_json(str(PROCESSED), [])
    today = now().date().isoformat()
    if state.get("posts_date") != today: state["posts_date"], state["posts_today"] = today, 0
    state["current_category"] = args.category
    if not enabled(cfg): set_status(cfg, state, "paused", "Agent je izklopljen."); print("AGENT_DISABLED"); return 0
    if state["posts_today"] >= int(cfg.get("maximum_outputs_per_day", 3)) and not args.force: set_status(cfg, state, "completed", "Dosežena je dnevna omejitev objav."); print("DAILY_LIMIT"); return 0
    set_status(cfg, state, "collecting", f"Pridobivanje virov: {args.category}.")
    if args.topic.strip():
        items = collect_topic(args.topic, args.category, int(cfg.get("max_source_items", 30)))
        if not items:
            print("INFO topic search returned no items; falling back to category sources")
            items = collect(cfg.get("input_sources", []), args.category, int(cfg.get("max_source_items", 30)))
    else:
        items = collect(cfg.get("input_sources", []), args.category, int(cfg.get("max_source_items", 30)))
    seen = {x.get("hash") for x in processed}; fresh = [x for x in items if x.get("hash") not in seen]
    # Authenticated manual topic requests use --force. If current sources were already
    # observed by the autonomous cycle, allow reusing them for the explicit editorial
    # request; title/QA validation still prevents an identical published article.
    if args.topic.strip() and args.force and not fresh:
        fresh = items
    if not fresh:
        set_status(cfg, state, "completed", f"Ni novih vsebin za kategorijo {args.category}.")
        print("NO_NEW_CONTENT")
        return 3 if (args.topic.strip() and args.force) else 0
    system_prompt = (HERE / "prompts/system.md").read_text(encoding="utf-8")
    task_prompt = (HERE / "prompts/task.md").read_text(encoding="utf-8")
    if args.topic.strip():
        task_prompt += "\n\nAvtorizirani urednik je zahteval temo: " + args.topic.strip() + "\nTema je uredniška zahteva, ne vir dejstev; dejstva še vedno črpaj samo iz podanih virov."
    set_status(cfg, state, "generating", f"Priprava članka: {args.category}.")
    used_for_article = fresh[:5]
    try:
        article = generate(system_prompt, task_prompt, fresh[:8], args.category); article["fallback"] = False
    except AIUnavailable as exc:
        print(f"INFO AI fallback: {exc}"); article = build_digest(used_for_article, args.category, max_items=5)
    if args.topic.strip():
        explicit_images, explicit_video = operator_media(args.topic)
        if explicit_images:
            if not article.get("heroImage"):
                article["heroImage"] = explicit_images[0]
                explicit_images = explicit_images[1:]
            existing_gallery = article.get("gallery") if isinstance(article.get("gallery"), list) else []
            article["gallery"] = (existing_gallery + explicit_images)[:12]
        if explicit_video and not article.get("video"):
            article["video"] = explicit_video
    if article.get("skip"):
        set_status(cfg, state, "completed", article.get("reason", "Ni primerne teme."))
        print("NO_SUITABLE_CONTENT")
        return 3 if (args.topic.strip() and args.force) else 0
    article["id"] = slugify(article.get("title", "")) + "-" + hashlib.sha1(used_for_article[0]["url"].encode()).hexdigest()[:8]
    used_urls = set() if (args.topic.strip() and args.force) else {x.get("url") for x in processed if x.get("url")}
    errors = validate(article, int(cfg["min_article_chars"]), int(cfg["max_article_chars"]), existing_titles(), used_urls)
    if errors:
        diag = BASE / "logs" / f"failed-{now().strftime('%Y%m%d-%H%M%S')}.json"; diag.parent.mkdir(parents=True, exist_ok=True); diag.write_text(json.dumps({"category": args.category, "errors": errors, "article": article}, ensure_ascii=False, indent=2), encoding="utf-8")
        state["last_error"] = ",".join(errors); state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1; state["last_failure"] = now().isoformat(timespec="seconds"); atomic_json(str(STATE), state); set_status(cfg, state, "failed", "QA ni uspel."); return 2
    ctl = control(); publish_mode = ctl.get("publish_mode") or os.getenv("PUBLISH_MODE", "automatic").lower()
    if args.dry_run or publish_mode != "automatic":
        draft = BASE / "content/drafts" / f"{article['id']}.json"; draft.parent.mkdir(parents=True, exist_ok=True); draft.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8"); set_status(cfg, state, "needs_review", "Rezultat je shranjen kot osnutek.", str(draft)); print("DRY_RUN_OK"); return 0
    set_status(cfg, state, "publishing", "Objavljanje preverjenega članka."); publish_to_app(str(APP), article, cfg["agent_name"])
    for item in used_for_article: processed.append({**item, "processed_at": now().isoformat(timespec="seconds"), "output_id": article["id"]})
    atomic_json(str(PROCESSED), processed[-750:])
    state.update({"last_success": now().isoformat(timespec="seconds"), "last_output": article["id"], "last_error": None, "consecutive_failures": 0, "posts_date": today, "posts_today": state.get("posts_today", 0) + 1, "agent_version": "2.1.0", "current_category": args.category})
    atomic_json(str(STATE), state); set_status(cfg, state, "completed", "Članek je uspešno pripravljen za objavo.", article["id"]); print(f"PUBLISHED:{article['id']}"); return 0
if __name__ == "__main__": raise SystemExit(main())
