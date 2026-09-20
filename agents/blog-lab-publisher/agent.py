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
from services.sources import collect, collect_topic, filter_topic_items, rank_topic_items
from services.ai_provider import generate, review_grounding, AIUnavailable
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
        "scheduled_slots_deferred": state.get("scheduled_slots_deferred", []),
        "last_editorial_hold": state.get("last_editorial_hold"),
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
    deferred = [item for item in (state.get("scheduled_slots_deferred") or []) if item != slot_id]
    state["scheduled_slots_deferred"] = deferred[-12:]


def defer_scheduled_slot(state: dict, slot_id: str, reason: str) -> None:
    slot_id = str(slot_id or "").strip()
    if not slot_id:
        return
    deferred = list(state.get("scheduled_slots_deferred") or [])
    if slot_id not in deferred:
        deferred.append(slot_id)
    state["scheduled_slots_deferred"] = deferred[-12:]
    state["last_editorial_hold"] = {
        "slot": slot_id,
        "reason": str(reason or "editorial_qa")[:240],
        "at": now().isoformat(timespec="seconds"),
    }


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


STORY_STOPWORDS = {
    "slovenija", "slovenski", "slovenska", "slovensko", "danes", "novice",
    "sport", "šport", "tekma", "tekmi", "tekmo", "ekipa", "ekipe", "igralec",
    "igralci", "liga", "prvenstvo", "turnir", "zmaga", "zmago", "nov", "nova",
    "novo", "proti", "pred", "med", "after", "with", "from", "this", "that",
    "team", "match", "game", "news", "today", "league", "sport",
}


def _story_tokens(item: dict) -> set[str]:
    title = unicodedata.normalize("NFKD", str(item.get("title") or "").lower())
    title = "".join(ch for ch in title if not unicodedata.combining(ch))
    words = re.findall(r"[a-z0-9čšžćđ-]{4,}", title)
    tokens = set()
    for word in words:
        if word in STORY_STOPWORDS:
            continue
        stem = word[:7] if len(word) >= 8 else word
        tokens.add(stem)
    return tokens


def automatic_story_pool(items: list[dict], category: str, max_items: int = 6) -> list[dict]:
    """Choose one coherent automatic story instead of feeding unrelated headlines to the writer."""
    raw_candidates = list(items or [])[:24]
    if not raw_candidates:
        return []

    # Directly fetched pages usually contain far more evidence than RSS-only
    # headlines, so prefer them while preserving stable order within each tier.
    candidates = [
        item for _, item in sorted(
            enumerate(raw_candidates),
            key=lambda pair: (
                0 if pair[1].get("verified_direct") else 1,
                0 if str(pair[1].get("provider") or "") == "google-news-si" else 1,
                -min(len(str(pair[1].get("summary") or "")), 5000),
                pair[0],
            ),
        )
    ][:18]

    token_sets = [_story_tokens(item) for item in candidates]
    best_index = 0
    best_members = [0]
    best_score = -1

    for index, tokens in enumerate(token_sets):
        members = [index]
        for other_index, other in enumerate(token_sets):
            if other_index == index:
                continue
            shared = tokens & other
            # Two shared title concepts, or one distinctive long concept,
            # is enough to treat two source records as the same story.
            if len(shared) >= 2 or any(len(token) >= 7 for token in shared):
                members.append(other_index)
        direct = 1 if candidates[index].get("verified_direct") else 0
        localized = 1 if str(candidates[index].get("provider") or "") == "google-news-si" else 0
        score = len(members) * 100 + localized * 10 + direct * 5 - index
        if score > best_score:
            best_score = score
            best_index = index
            best_members = members

    ordered = [candidates[best_index]]
    for index in best_members:
        if index == best_index:
            continue
        ordered.append(candidates[index])
        if len(ordered) >= max_items:
            break

    # When no corroborating title exists, keep the single strongest scoped source.
    pool = ordered[:max_items]
    print(
        f"AUTO_STORY_POOL category={category} candidates={len(candidates)} "
        f"selected={len(pool)} anchor={str(pool[0].get('title') or '')[:100]}"
    )
    return pool


def allowed_source_urls(source_items: list[dict]) -> set[str]:
    return {
        str(item.get("url") or "").strip()
        for item in source_items or []
        if str(item.get("url") or "").strip()
    }


def article_used_items(article: dict, source_items: list[dict]) -> list[dict]:
    source_urls = {
        str(item.get("url") or "").strip()
        for item in article.get("sources", [])
        if isinstance(item, dict) and str(item.get("url") or "").strip()
    }
    used = [item for item in source_items or [] if str(item.get("url") or "").strip() in source_urls]
    return used or list(source_items or [])[:1]


def grounding_repair_task(task_prompt: str, article: dict, review: dict) -> str:
    issues = [str(x) for x in review.get("issues", []) if str(x).strip()]
    unsupported = [str(x) for x in review.get("unsupported_claims", []) if str(x).strip()]
    return (
        task_prompt
        + "\n\nDEJSTVENI QA POPRAVEK: osnutek ni prestal preverjanja proti virom. "
        + "Odstrani ali popravi VSE trditve, ki niso neposredno podprte s podanimi viri. "
          "Ne nadomeščaj jih z novimi domnevami. Ne mešaj različnih tekmovanj, dogodkov ali oseb. "
          "Če vir ne navaja formata tekmovanja, skupine, lestvice, rezultata ali poti napredovanja, tega ne trdi. "
          "Odpravi ponavljanje in uporabi konkretne vsebinske podnaslove, ne 'Uvod', 'Zaključek' ali 'Povzetek'. "
        + "\nQA issues: " + json.dumps(issues, ensure_ascii=False)
        + "\nUnsupported claims: " + json.dumps(unsupported, ensure_ascii=False)
        + "\nPrejšnji osnutek: " + json.dumps(article, ensure_ascii=False)
        + "\nVrni celoten popravljen JSON članek ali skip=true, če evidence ne zadošča."
    )


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
        state["scheduled_slots_deferred"] = []
        state["last_editorial_hold"] = None
    state.setdefault("scheduled_posts_today", 0)
    state.setdefault("manual_posts_today", 0)
    state.setdefault("scheduled_slots_done", [])
    state.setdefault("scheduled_slots_deferred", [])
    state.setdefault("last_editorial_hold", None)
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
        items = filter_topic_items(args.topic, items, minimum_score=1)
        if not items:
            message = "Za zahtevano temo ni bilo mogoče najti dovolj relevantnih in preverljivih virov."
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
    evidence_pool = fresh[:10] if manual_request else automatic_story_pool(fresh, args.category, max_items=6)
    if not evidence_pool:
        set_status(cfg, state, "waiting", "Ni dovolj koherentne dokazne podlage; slot ostaja odprt.")
        print("NO_COHERENT_STORY")
        return 0
    used_for_article = evidence_pool[:7]
    allowed_urls = allowed_source_urls(evidence_pool)
    try:
        article = generate(system_prompt, task_prompt, evidence_pool[:8], args.category)
        article["fallback"] = False
        state["writer_mode"] = str(article.pop("_writer_provider", "ai"))
    except AIUnavailable as exc:
        if manual_request:
            state["last_error"] = "manual_ai_unavailable"
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
            state["last_failure"] = now().isoformat(timespec="seconds")
            atomic_json(str(STATE), state)
            set_status(
                cfg,
                state,
                "failed",
                "AI pisec trenutno ni na voljo; ročni članek ni bil objavljen brez varnega uredniškega pregleda.",
            )
            print(f"ARTICLE_AI_UNAVAILABLE {exc}")
            return 4
        print(f"AUTO_AI_UNAVAILABLE {exc}")
        state["writer_mode"] = "unavailable"
        state["last_error"] = None
        state["consecutive_failures"] = 0
        if args.scheduled_slot:
            defer_scheduled_slot(state, args.scheduled_slot, "ai_unavailable")
        atomic_json(str(STATE), state)
        set_status(
            cfg,
            state,
            "waiting",
            "AI pisec trenutno ni na voljo; samodejni termin je zadržan brez objave nekakovostnega fallbacka.",
        )
        return 0
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
            article = generate(system_prompt, retry_task, evidence_pool[:8], args.category)
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
            article = generate(system_prompt, retry_task, evidence_pool[:8], args.category)
            article["fallback"] = False
            state["writer_mode"] = str(article.pop("_writer_provider", state.get("writer_mode", "ai")))
            article = prepare_article_candidate(article, used_for_article, args.topic, args.output_category)
        except AIUnavailable as exc:
            print(f"INFO automatic retry unavailable: {exc}")

    if article.get("skip"):
        if not manual_request and args.scheduled_slot:
            defer_scheduled_slot(
                state,
                args.scheduled_slot,
                str(article.get("reason") or "writer_skip")[:300],
            )
            atomic_json(str(STATE), state)
        set_status(
            cfg,
            state,
            "waiting",
            article.get("reason", "Ni dovolj kakovostne podlage za objavo."),
        )
        print("NO_SUITABLE_CONTENT")
        return 3 if (args.topic.strip() and args.force) else 0

    article["id"] = slugify(article.get("title", "")) + "-" + hashlib.sha1(used_for_article[0]["url"].encode()).hexdigest()[:8]
    errors = validate(article, min_chars, max_chars, titles, used_urls, allowed_urls)

    if errors:
        print("QA_ERRORS_INITIAL " + ",".join(errors))
        repair_prompt = qa_repair_task(task_prompt, errors, min_chars, max_chars)
        try:
            repaired = generate(system_prompt, repair_prompt, evidence_pool[:8], args.category)
            repaired["fallback"] = False
            state["writer_mode"] = str(repaired.pop("_writer_provider", state.get("writer_mode", "ai")))
            repaired = prepare_article_candidate(repaired, used_for_article, args.topic, args.output_category)
            if not repaired.get("skip"):
                repaired["id"] = slugify(repaired.get("title", "")) + "-" + hashlib.sha1(used_for_article[0]["url"].encode()).hexdigest()[:8]
                repaired_errors = validate(repaired, min_chars, max_chars, titles, used_urls, allowed_urls)
                print("QA_ERRORS_REPAIR " + (",".join(repaired_errors) if repaired_errors else "none"))
                if not repaired_errors:
                    article = repaired
                    errors = []
                else:
                    errors = repaired_errors
        except AIUnavailable as exc:
            print(f"INFO QA repair unavailable: {exc}")

    if not errors:
        grounding_errors = []
        try:
            review = review_grounding(article, evidence_pool, args.category)
            if not review.get("pass"):
                grounding_errors = ["grounding_failed"]
                print(
                    "GROUNDING_REVIEW_FAIL "
                    + json.dumps({
                        "issues": review.get("issues", []),
                        "unsupported_claims": review.get("unsupported_claims", []),
                    }, ensure_ascii=False)
                )
                repair_task = grounding_repair_task(task_prompt, article, review)
                repaired = generate(system_prompt, repair_task, evidence_pool[:8], args.category)
                repaired["fallback"] = False
                state["writer_mode"] = str(repaired.pop("_writer_provider", state.get("writer_mode", "ai")))
                repaired = prepare_article_candidate(
                    repaired,
                    used_for_article,
                    args.topic,
                    args.output_category,
                )
                if not repaired.get("skip"):
                    repaired["id"] = (
                        slugify(repaired.get("title", ""))
                        + "-"
                        + hashlib.sha1(used_for_article[0]["url"].encode()).hexdigest()[:8]
                    )
                    repaired_errors = validate(
                        repaired,
                        min_chars,
                        max_chars,
                        titles,
                        used_urls,
                        allowed_urls,
                    )
                    if not repaired_errors:
                        second_review = review_grounding(repaired, evidence_pool, args.category)
                        if second_review.get("pass"):
                            article = repaired
                            grounding_errors = []
                            print("GROUNDING_REVIEW_REPAIR_PASS")
                        else:
                            print(
                                "GROUNDING_REVIEW_REPAIR_FAIL "
                                + json.dumps(second_review, ensure_ascii=False)
                            )
                    else:
                        print("GROUNDING_REPAIR_QA_FAIL " + ",".join(repaired_errors))
        except AIUnavailable as exc:
            print(f"GROUNDING_REVIEW_UNAVAILABLE {exc}")
            grounding_errors = ["grounding_unavailable"]


        if grounding_errors:
            errors = grounding_errors

    if errors:
        diag = BASE / "logs" / f"failed-{now().strftime('%Y%m%d-%H%M%S')}.json"
        diag.parent.mkdir(parents=True, exist_ok=True)
        diag.write_text(
            json.dumps({"category": args.category, "errors": errors, "article": article}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        state["last_error"] = ",".join(errors)
        if manual_request:
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
            state["last_failure"] = now().isoformat(timespec="seconds")
            atomic_json(str(STATE), state)
            set_status(cfg, state, "failed", "QA ni uspel pri ročni uredniški zahtevi.")
            print("QA_FAILED_FINAL " + ",".join(errors))
            return 2

        # Editorial insufficiency is not an infrastructure failure. Keep the
        # automatic slot open and let a later catch-up use fresher evidence,
        # without triggering the self-heal workflow to repeat the same draft.
        state["consecutive_failures"] = 0
        state["last_error"] = None
        if args.scheduled_slot:
            defer_scheduled_slot(state, args.scheduled_slot, ",".join(errors))
        atomic_json(str(STATE), state)
        set_status(
            cfg,
            state,
            "waiting",
            "QA je zadržal samodejni osnutek; termin je odložen, naslednji dnevni termini ostajajo aktivni.",
        )
        print("QA_DEFERRED " + ",".join(errors))
        return 0
    ctl = control(); publish_mode = ctl.get("publish_mode") or os.getenv("PUBLISH_MODE", "automatic").lower()
    if args.dry_run or publish_mode != "automatic":
        draft = BASE / "content/drafts" / f"{article['id']}.json"; draft.parent.mkdir(parents=True, exist_ok=True); draft.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8"); set_status(cfg, state, "needs_review", "Rezultat je shranjen kot osnutek.", str(draft)); print("DRY_RUN_OK"); return 0
    set_status(cfg, state, "publishing", "Objavljanje preverjenega članka."); publish_to_app(str(APP), article, cfg["agent_name"])
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
        "scheduled_posts_today": state.get("scheduled_posts_today", 0) + (0 if manual_request else 1),
        "manual_posts_today": state.get("manual_posts_today", 0) + (1 if manual_request else 0),
        "agent_version": "2.7.0",
        "current_category": args.category,
    })
    if args.scheduled_slot and not manual_request:
        mark_scheduled_slot_done(state, args.scheduled_slot)
    atomic_json(str(STATE), state); set_status(cfg, state, "completed", "Članek je uspešno pripravljen za objavo.", article["id"]); print(f"PUBLISHED:{article['id']}"); return 0
if __name__ == "__main__": raise SystemExit(main())
