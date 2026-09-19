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
    text = topic or ""
    marker_re = re.compile(
        r"\[(hero slika|naložena slika):\s*(https://[^|\]\s]+)(?:\s*\|\s*([^\]]{0,180}))?\]",
        re.I,
    )
    marked = []
    for role, url, caption in marker_re.findall(text):
        marked.append((
            role.lower(),
            url.rstrip(".,);]\\\"'"),
            " ".join(str(caption or "").split())[:180],
        ))
    marked.sort(key=lambda row: 0 if row[0] == "hero slika" else 1)

    images = []
    video = None
    seen = set()

    for _, url, caption in marked:
        low = url.lower()
        if url in seen:
            continue
        if re.search(r'\.(?:jpe?g|png|webp|gif|avif)(?:\?|$)', low):
            seen.add(url)
            images.append({"url": url, "alt": "", "caption": caption})

    text_without_markers = marker_re.sub(" ", text)
    for raw in re.findall(r"https://[^\s<>\]]+", text_without_markers):
        url = raw.rstrip(".,);]\\\"'")
        if "|" in url:
            url = url.split("|", 1)[0].strip()
        low = url.lower()
        if not url or url in seen:
            continue
        if re.search(r'\.(?:jpe?g|png|webp|gif|avif)(?:\?|$)', low):
            seen.add(url)
            images.append({"url": url, "alt": "", "caption": ""})
        elif ("youtube.com/" in low or "youtu.be/" in low or re.search(r'\.(?:mp4|webm|ogg)(?:\?|$)', low)) and video is None:
            seen.add(url)
            video = {"url": url, "title": ""}

    return images[:12], video

def _media_url(value) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return str(value.get("url") or "").strip()
    return ""

def apply_media_policy(article: dict, source_items: list[dict], topic: str = "") -> dict:
    """Apply deterministic media priority without inventing URLs.

    Priority: authenticated operator uploads > AI-selected verified media >
    image/video URLs present in the source records.
    """
    explicit_images, explicit_video = operator_media(topic)
    existing_gallery = article.get("gallery") if isinstance(article.get("gallery"), list) else []

    if explicit_images:
        article["heroImage"] = explicit_images[0]
        gallery_candidates = explicit_images[1:] + existing_gallery
    else:
        gallery_candidates = list(existing_gallery)

    source_images = []
    for item in source_items or []:
        url = str(item.get("image_url") or "").strip()
        if not url:
            continue
        source_images.append({
            "url": url,
            "alt": str(item.get("title") or "").strip()[:180],
            "caption": str(item.get("source_name") or "").strip()[:120],
        })

    if not _media_url(article.get("heroImage")) and source_images:
        article["heroImage"] = source_images.pop(0)

    gallery_candidates.extend(source_images)
    hero_url = _media_url(article.get("heroImage"))
    deduped = []
    seen = {hero_url} if hero_url else set()
    for image in gallery_candidates:
        url = _media_url(image)
        if not url or url in seen:
            continue
        seen.add(url)
        deduped.append(image)
        if len(deduped) >= 12:
            break
    article["gallery"] = deduped

    if explicit_video:
        article["video"] = explicit_video
    elif not _media_url(article.get("video")):
        for item in source_items or []:
            url = str(item.get("video_url") or "").strip()
            if url:
                article["video"] = {"url": url, "title": str(item.get("title") or "").strip()[:120]}
                break

    return article

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
    ap.add_argument("--output-category", default="")
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
            message = "Za zahtevano temo ni bilo mogoče najti dovolj tematskih virov."
            set_status(cfg, state, "failed", message)
            state["last_error"] = "no_topic_sources"
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
            state["last_failure"] = now().isoformat(timespec="seconds")
            atomic_json(str(STATE), state)
            print("NO_TOPIC_SOURCES")
            return 3
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
    if args.output_category.strip():
        article["category"] = args.output_category.strip()[:40]
    article = apply_media_policy(article, used_for_article, args.topic)
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
