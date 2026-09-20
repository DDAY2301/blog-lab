from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import yaml

BASE = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from services.sources import collect, collect_topic, rank_topic_items
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

def manual_editor_system_prompt(system_prompt: str, topic: str, source_count: int) -> str:
    """Resolve the generic skip rule for an authenticated manual editorial request."""
    text = str(system_prompt or "")
    text = text.replace(
        "- Če material ne zadostuje za kakovosten samostojen članek, vrni `skip=true`.",
        "- Pri samodejnem uredniškem izboru lahko zavrneš temo, če gradivo res ne zadostuje.",
    )
    return text + (
        "\n\n## Prednost avtorizirane ročne uredniške zahteve\n"
        f"Urednik je izrecno zahteval temo: {topic.strip()}\n"
        f"Na voljo je {int(source_count)} preverjenih spletnih virov, razvrščenih po relevantnosti.\n"
        "Pri tej ročni zahtevi NE vrni skip=true samo zato, ker tema ni breaking news, "
        "ker so viri različnih tipov ali ker ni dovolj dejstev za 800–1300 besed. "
        "Če vsaj trije od prvih virov vsebinsko podpirajo zahtevano temo, napiši članek. "
        "Dolžino prilagodi dokazljivemu gradivu; 450–900 besed je sprejemljivo. "
        "Uporabljaj samo dejstva iz virov, jasno omeji negotovost in ničesar ne ugibaj. "
        "skip=true je dovoljen samo, če so najrelevantnejši viri dejansko nepovezani s temo "
        "ali ne vsebujejo dovolj preverljivih dejstev niti za kratek faktografski članek."
    )

def now(): return datetime.now(ZoneInfo("Europe/Ljubljana"))
def control(): return load_json(str(CONTROL), {"enabled": True, "publish_mode": "automatic"})
def enabled(cfg): return cfg.get("enabled", True) and control().get("enabled", True) and os.getenv("AGENT_ENABLED", "true").lower() == "true"
def set_status(cfg, state, value, message="", output=None):
    atomic_json(str(STATUS), {
        "agent": cfg["agent_name"],
        "status": value,
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
        "writer_mode": state.get("writer_mode", "unknown"),
        "scheduled_slots_done": state.get("scheduled_slots_done", []),
        "last_error": state.get("last_error"),
    })
def mark_scheduled_slot_done(state: dict, slot_id: str) -> None:
    slot_id = str(slot_id or "").strip()
    if not slot_id:
        return
    done = list(state.get("scheduled_slots_done") or [])
    if slot_id not in done:
        done.append(slot_id)
    state["scheduled_slots_done"] = done[-12:]


AUTO_SEARCH_QUERIES = {
    "sport": "Slovenija šport danes",
    "politika": "Slovenija politika danes",
    "aktualno": "Slovenija aktualne novice danes",
}


AUTO_CATEGORY_TERMS = {
    "sport": (
        "šport", "sport", "nogomet", "football", "soccer", "košark", "basket",
        "tenis", "tennis", "koles", "cycling", "atlet", "hokej", "hockey",
        "smuč", "ski", "rokomet", "handball", "odboj", "volley", "liga", "league",
        "prvenst", "championship", "tekm", "match", "igral", "player", "trener",
        "coach", "gol", "goal", "racing", "race", "formula", "moto", "nba",
        "uefa", "fifa", "olimp", "olymp", "medal", "turnir", "tournament",
    ),
    "politika": (
        "politika", "politic", "vlada", "government", "parlament", "parliament",
        "volit", "election", "minister", "predsed", "president", "zakon", "law",
        "strank", "party", "koalic", "coalition", "opozic", "opposition",
        "državni zbor", "national assembly", "evropska unija", "european union",
    ),
}


def _mostly_latin(text: str, minimum_ratio: float = 0.55) -> bool:
    letters = [ch for ch in str(text or "") if ch.isalpha()]
    if len(letters) < 12:
        return True
    latin = 0
    for ch in letters:
        try:
            if "LATIN" in unicodedata.name(ch):
                latin += 1
        except ValueError:
            pass
    return (latin / len(letters)) >= minimum_ratio


def _automatic_generic_result(item: dict) -> bool:
    try:
        parsed = urlparse(str(item.get("url") or ""))
        host = (parsed.hostname or "").lower().removeprefix("www.")
        path = (parsed.path or "").lower()
    except Exception:
        return True

    if host in {"namu.wiki", "duckduckgo.com", "www.duckduckgo.com"}:
        return True
    if host == "news.google.com" and ("/topics/" in path or "/search" in path):
        return True
    if host.endswith("bing.com") and ("/search" in path or "/news/search" in path):
        return True
    return False


def _automatic_category_match(item: dict, category: str) -> bool:
    text = " ".join([
        str(item.get("title") or ""),
        str(item.get("summary") or ""),
    ]).lower()
    if category in AUTO_CATEGORY_TERMS:
        return any(term in text for term in AUTO_CATEGORY_TERMS[category])

    # "Aktualno" is intentionally broad, but the autonomous Slovenian slot
    # should still be anchored to Slovenia/local sources when using global web search.
    if category == "aktualno":
        provider = str(item.get("provider") or "").lower()
        try:
            host = (urlparse(str(item.get("url") or "")).hostname or "").lower()
        except Exception:
            host = ""
        return (
            provider == "google-news-si"
            or host.endswith(".si")
            or "slovenij" in text
            or "slovenia" in text
            or "ljubljan" in text
        )
    return True


def automatic_source_usable(item: dict, category: str, *, trusted_primary: bool = False) -> bool:
    title = str(item.get("title") or "").strip()
    summary = str(item.get("summary") or "").strip()
    combined = f"{title} {summary}".strip()

    if len(title) < 8:
        return False
    if not _mostly_latin(combined):
        return False
    if _automatic_generic_result(item):
        return False

    # The configured category RSS is already a trusted scoped search. Global
    # discovery needs an additional semantic category gate.
    if not trusted_primary:
        provider = str(item.get("provider") or "").lower()
        localized_search = provider == "google-news-si"
        if not localized_search and not _automatic_category_match(item, category):
            return False

    # Do not let the fallback writer turn a headline-only search result into an
    # apparently substantive article.
    minimum_summary = 45 if trusted_primary else 80
    if len(summary) < minimum_summary and not item.get("verified_direct"):
        return False
    return True


def _merge_source_groups(*groups: list[dict], limit: int = 30) -> list[dict]:
    out = []
    seen = set()
    for group in groups:
        for item in group or []:
            key = str(item.get("url") or item.get("hash") or "").strip()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(item)
            if len(out) >= limit:
                return out
    return out


def collect_automatic_sources(cfg: dict, category: str) -> list[dict]:
    limit = int(cfg.get("max_source_items", 30))
    primary_raw = collect(cfg.get("input_sources", []), category, limit)
    primary = [
        item for item in primary_raw
        if automatic_source_usable(item, category, trusted_primary=True)
    ]

    broad_query = AUTO_SEARCH_QUERIES.get(category, f"Slovenija {category} danes")
    try:
        broad_raw = collect_topic(broad_query, category, limit)
    except Exception as exc:
        print(f"WARN automatic web-wide source search failed: {exc}")
        broad_raw = []
    broad = [
        item for item in broad_raw
        if automatic_source_usable(item, category, trusted_primary=False)
    ]

    merged = _merge_source_groups(primary, broad, limit=limit)
    print(
        f"AUTO_SOURCES category={category} "
        f"primary={len(primary)}/{len(primary_raw)} "
        f"webwide={len(broad)}/{len(broad_raw)} merged={len(merged)}"
    )
    return merged


def prepare_article_candidate(
    article: dict,
    source_items: list[dict],
    topic: str,
    output_category: str,
) -> dict:
    article = dict(article or {})
    if output_category.strip():
        article["category"] = output_category.strip()[:40]
    article = apply_media_policy(article, source_items, topic)
    return article


def qa_repair_task(task_prompt: str, errors: list[str], min_chars: int, max_chars: int) -> str:
    return (
        task_prompt
        + "\n\nQA POPRAVEK: prejšnji osnutek ni prestal avtomatske validacije. "
        + "Napake: " + ", ".join(errors)
        + f". Vrni celoten popravljen JSON članek. Content mora imeti med {min_chars} in {max_chars} znakov. "
          "Obvezno vrni title, excerpt, seoDescription, content, category, tags in sources. "
          "excerpt mora biti največ 240 znakov. sources naj vsebuje samo HTTPS URL-je iz podanih virov. "
          "Ne izmišljaj URL-jev, citatov ali dejstev. Če je naslov podvojen, izberi stvaren drugačen naslov. "
          "Ne vračaj skip=true samo zaradi dolžine; besedilo prilagodi dejansko podprtim informacijam."
    )


def existing_titles() -> set[str]:
    if not APP.exists(): return set()
    text = APP.read_text(encoding="utf-8", errors="ignore")
    return {m.strip().lower() for m in re.findall(r'(?:title|"title")\s*:\s*"([^"]+)"', text)}
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--manual", action="store_true", help="Manual/editorial request; does not consume scheduled daily quota")
    ap.add_argument("--scheduled-slot", default="", help="Resolved automatic schedule slot id for catch-up tracking")
    ap.add_argument("--category", choices=sorted(VALID_CATEGORIES), default=os.getenv("RUN_CATEGORY", "aktualno"))
    ap.add_argument("--topic", default="")
    ap.add_argument("--output-category", default="")
    args = ap.parse_args()
    cfg = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
    state = load_json(str(STATE), {
        "consecutive_failures": 0,
        "posts_today": 0,
        "scheduled_posts_today": 0,
        "manual_posts_today": 0,
        "posts_date": None,
    })
    processed = load_json(str(PROCESSED), [])
    today = now().date().isoformat()
    if state.get("posts_date") != today:
        state["posts_date"] = today
        state["posts_today"] = 0
        state["scheduled_posts_today"] = 0
        state["manual_posts_today"] = 0
        state["scheduled_slots_done"] = []
    state.setdefault("scheduled_posts_today", 0)
    state.setdefault("manual_posts_today", 0)
    state.setdefault("scheduled_slots_done", [])
    state["current_category"] = args.category
    manual_request = bool(args.manual or args.topic.strip())
    if not enabled(cfg): set_status(cfg, state, "paused", "Agent je izklopljen."); print("AGENT_DISABLED"); return 0
    if not manual_request and state["scheduled_posts_today"] >= int(cfg.get("maximum_outputs_per_day", 3)):
        set_status(cfg, state, "completed", "Dosežena je dnevna omejitev samodejnih objav.")
        print("DAILY_LIMIT")
        return 0
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
        items = collect_automatic_sources(cfg, args.category)
    seen = {x.get("hash") for x in processed}; fresh = [x for x in items if x.get("hash") not in seen]
    # Authenticated manual topic requests use --force. If current sources were already
    # observed by the autonomous cycle, allow reusing them for the explicit editorial
    # request; title/QA validation still prevents an identical published article.
    if args.topic.strip() and args.force and not fresh:
        fresh = items
    if args.topic.strip() and fresh:
        fresh = rank_topic_items(args.topic, fresh)
    if not fresh:
        set_status(cfg, state, "waiting", f"Ni novih vsebin za kategorijo {args.category}; slot ostaja odprt za naslednji catch-up.")
        print("NO_NEW_CONTENT")
        return 3 if (args.topic.strip() and args.force) else 0
    system_prompt = (HERE / "prompts/system.md").read_text(encoding="utf-8")
    task_prompt = (HERE / "prompts/task.md").read_text(encoding="utf-8")
    if args.topic.strip() and args.force:
        system_prompt = manual_editor_system_prompt(system_prompt, args.topic, len(fresh))
    if args.topic.strip():
        task_prompt += (
            "\n\nAvtorizirani urednik je zahteval temo: " + args.topic.strip()
            + "\nTema je uredniška zahteva, ne vir dejstev; dejstva še vedno črpaj samo iz podanih virov."
            + "\nTo je neposredna ročna uredniška zahteva. Če podani preverjeni spletni viri skupaj podpirajo "
              "uporaben informativni članek o temi, članek NAPIŠI. Ne vrni skip samo zato, ker tema ni breaking news, "
              "ker viri prihajajo iz različnih vrst spletnih strani ali ker material ne zadošča za 1300 besed. "
              "Če je dokazljivega gradiva manj, napiši krajši, vsebinsko zaokrožen članek približno 500–900 besed "
              "in jasno omeji trditve na to, kar viri dejansko podpirajo. skip=true uporabi samo, če so najbolj "
              "relevantni viri očitno nepovezani z zahtevano temo ali ne omogočajo niti osnovnega faktografskega članka."
        )
    set_status(cfg, state, "generating", f"Priprava članka: {args.category}.")
    used_for_article = fresh[:7]
    try:
        article = generate(system_prompt, task_prompt, fresh[:10], args.category)
        article["fallback"] = False
        state["writer_mode"] = str(article.pop("_writer_provider", "ai"))
    except AIUnavailable as exc:
        print(f"INFO AI fallback: {exc}")
        article = build_digest(used_for_article, args.category, max_items=5)
        state["writer_mode"] = "fallback"
    article = prepare_article_candidate(
        article,
        used_for_article,
        args.topic,
        args.output_category,
    )
    if article.get("skip") and args.topic.strip() and args.force and len(fresh) >= 3:
        # A manual editorial request gets one bounded second pass. The second
        # pass may still refuse genuinely unrelated evidence, but it should not
        # skip simply because the topic is evergreen or the article must be shorter.
        retry_task = (
            task_prompt
            + "\n\nPONOVNI UREDNIŠKI POSKUS: prvi odgovor je vrnil skip, vendar je bilo najdenih "
              f"{len(fresh)} preverjenih virov. Preglej predvsem prve vire po relevantnosti. "
              "Če vsaj trije podpirajo zahtevano temo, napiši stvaren članek izključno iz teh dejstev. "
              "Dovoljen je krajši format. Ne dodajaj manjkajočih dejstev in ne ugibaj."
        )
        print(f"MANUAL_WRITER_RETRY sources={len(fresh)}")
        try:
            article = generate(system_prompt, retry_task, fresh[:10], args.category)
            article["fallback"] = False
            state["writer_mode"] = str(article.pop("_writer_provider", state.get("writer_mode", "ai")))
            article = prepare_article_candidate(
                article,
                used_for_article,
                args.topic,
                args.output_category,
            )
        except AIUnavailable as exc:
            print(f"INFO manual retry unavailable: {exc}")

    min_chars = int(cfg["min_article_chars"])
    max_chars = int(cfg["max_article_chars"])
    used_urls = set() if (args.topic.strip() and args.force) else {x.get("url") for x in processed if x.get("url")}
    titles = existing_titles()

    if article.get("skip") and not manual_request:
        print(f"AUTO_WRITER_RETRY reason={str(article.get('reason') or '')[:240]}")
        retry_task = (
            task_prompt
            + "\n\nSAMODEJNI PONOVNI POSKUS: prvi osnutek je vrnil skip. "
              "Iz podanih preverljivih virov izberi najbolje podprto konkretno zgodbo in napiši uporaben "
              "faktografski članek. Če gradiva ni za dolg članek, napiši krajši, vendar zaokrožen članek. "
              "Ne ugibaj in ne dodajaj dejstev, ki jih viri ne podpirajo."
        )
        try:
            article = generate(system_prompt, retry_task, fresh[:10], args.category)
            article["fallback"] = False
            state["writer_mode"] = str(article.pop("_writer_provider", state.get("writer_mode", "ai")))
            article = prepare_article_candidate(article, used_for_article, args.topic, args.output_category)
        except AIUnavailable as exc:
            print(f"INFO automatic retry unavailable: {exc}")

    if article.get("skip") and not manual_request:
        print("AUTO_FALLBACK_AFTER_SKIP")
        article = prepare_article_candidate(
            build_digest(used_for_article, args.category, max_items=min(7, len(used_for_article))),
            used_for_article,
            args.topic,
            args.output_category,
        )
        state["writer_mode"] = "fallback"

    if article.get("skip"):
        set_status(cfg, state, "waiting", article.get("reason", "Ni primerne teme; slot ostaja odprt."))
        print("NO_SUITABLE_CONTENT")
        return 3 if (args.topic.strip() and args.force) else 0

    article["id"] = slugify(article.get("title", "")) + "-" + hashlib.sha1(used_for_article[0]["url"].encode()).hexdigest()[:8]
    errors = validate(article, min_chars, max_chars, titles, used_urls)

    if errors:
        print("QA_ERRORS_INITIAL " + ",".join(errors))
        repair_prompt = qa_repair_task(task_prompt, errors, min_chars, max_chars)
        try:
            repaired = generate(system_prompt, repair_prompt, fresh[:10], args.category)
            repaired["fallback"] = False
            state["writer_mode"] = str(repaired.pop("_writer_provider", state.get("writer_mode", "ai")))
            repaired = prepare_article_candidate(repaired, used_for_article, args.topic, args.output_category)
            if not repaired.get("skip"):
                repaired["id"] = slugify(repaired.get("title", "")) + "-" + hashlib.sha1(used_for_article[0]["url"].encode()).hexdigest()[:8]
                repaired_errors = validate(repaired, min_chars, max_chars, titles, used_urls)
                print("QA_ERRORS_REPAIR " + (",".join(repaired_errors) if repaired_errors else "none"))
                if not repaired_errors:
                    article = repaired
                    errors = []
                else:
                    errors = repaired_errors
        except AIUnavailable as exc:
            print(f"INFO QA repair unavailable: {exc}")

    if errors:
        print("QA_FALLBACK_ATTEMPT " + ",".join(errors))
        fallback = prepare_article_candidate(
            build_digest(used_for_article, args.category, max_items=min(7, len(used_for_article))),
            used_for_article,
            args.topic,
            args.output_category,
        )
        if not fallback.get("skip"):
            fallback["id"] = slugify(fallback.get("title", "")) + "-" + hashlib.sha1(used_for_article[0]["url"].encode()).hexdigest()[:8]
            fallback_errors = validate(fallback, min_chars, max_chars, titles, used_urls)
            print("QA_ERRORS_FALLBACK " + (",".join(fallback_errors) if fallback_errors else "none"))
            if not fallback_errors:
                article = fallback
                errors = []
                state["writer_mode"] = "fallback"
            else:
                errors = fallback_errors

    if errors:
        diag = BASE / "logs" / f"failed-{now().strftime('%Y%m%d-%H%M%S')}.json"
        diag.parent.mkdir(parents=True, exist_ok=True)
        diag.write_text(
            json.dumps({"category": args.category, "errors": errors, "article": article}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        state["last_error"] = ",".join(errors)
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        state["last_failure"] = now().isoformat(timespec="seconds")
        atomic_json(str(STATE), state)
        set_status(cfg, state, "failed", "QA ni uspel; slot ostaja odprt za naslednji catch-up.")
        print("QA_FAILED_FINAL " + ",".join(errors))
        return 2
    ctl = control(); publish_mode = ctl.get("publish_mode") or os.getenv("PUBLISH_MODE", "automatic").lower()
    if args.dry_run or publish_mode != "automatic":
        draft = BASE / "content/drafts" / f"{article['id']}.json"; draft.parent.mkdir(parents=True, exist_ok=True); draft.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8"); set_status(cfg, state, "needs_review", "Rezultat je shranjen kot osnutek.", str(draft)); print("DRY_RUN_OK"); return 0
    set_status(cfg, state, "publishing", "Objavljanje preverjenega članka."); publish_to_app(str(APP), article, cfg["agent_name"])
    for item in used_for_article: processed.append({**item, "processed_at": now().isoformat(timespec="seconds"), "output_id": article["id"]})
    atomic_json(str(PROCESSED), processed[-750:])
    state.update({
        "last_success": now().isoformat(timespec="seconds"),
        "last_output": article["id"],
        "last_error": None,
        "consecutive_failures": 0,
        "posts_date": today,
        "posts_today": state.get("posts_today", 0) + 1,
        "scheduled_posts_today": state.get("scheduled_posts_today", 0) + (0 if manual_request else 1),
        "manual_posts_today": state.get("manual_posts_today", 0) + (1 if manual_request else 0),
        "agent_version": "2.4.0",
        "current_category": args.category,
    })
    if args.scheduled_slot and not manual_request:
        mark_scheduled_slot_done(state, args.scheduled_slot)
    atomic_json(str(STATE), state); set_status(cfg, state, "completed", "Članek je uspešno pripravljen za objavo.", article["id"]); print(f"PUBLISHED:{article['id']}"); return 0
if __name__ == "__main__": raise SystemExit(main())
