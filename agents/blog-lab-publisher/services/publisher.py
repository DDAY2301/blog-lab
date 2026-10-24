from __future__ import annotations
import json, os, re, tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ANCHOR = "const starterArticles = ["
def slugify(text: str) -> str:
    repl = {"č":"c","š":"s","ž":"z","ć":"c","đ":"d"}
    text = "".join(repl.get(c.lower(), c.lower()) for c in text)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:90] or "objava"
def _image(value):
    if not value:
        return None
    if isinstance(value, str):
        return {"url": value, "alt": "", "caption": ""}
    if not isinstance(value, dict) or not value.get("url"):
        return None
    return {
        "url": str(value.get("url", "")).strip(),
        "alt": str(value.get("alt", "")).strip(),
        "caption": str(value.get("caption", "")).strip(),
        "sourceUrl": str(value.get("sourceUrl", "")).strip(),
    }

def _video(value):
    if not value:
        return None
    if isinstance(value, str):
        return {"url": value, "title": ""}
    if not isinstance(value, dict) or not value.get("url"):
        return None
    return {"url": str(value.get("url", "")).strip(), "title": str(value.get("title", "")).strip()}

def _sources(values):
    out = []
    for value in values if isinstance(values, list) else []:
        if not isinstance(value, dict) or not value.get("url"):
            continue
        out.append({
            "label": str(value.get("label") or value.get("title") or "Vir").strip(),
            "url": str(value.get("url", "")).strip(),
        })
    return out[:30]

def to_js_object(article: dict, agent_name: str) -> str:
    now = datetime.now(ZoneInfo("Europe/Ljubljana")).isoformat(timespec="seconds")
    obj = {
        "id": article["id"],
        "title": article["title"],
        "excerpt": article["excerpt"],
        "seoDescription": article["seoDescription"],
        "content": article["content"],
        "category": article["category"],
        "author": agent_name,
        "status": article.get("status", "published"),
        "heroImage": _image(article.get("heroImage")),
        "video": _video(article.get("video")),
        "gallery": [img for img in (_image(x) for x in article.get("gallery", []) if x) if img][:12],
        "sources": _sources(article.get("sources", [])),
        "createdAt": now,
        "updatedAt": now,
    }
    return "  " + json.dumps(obj, ensure_ascii=False, indent=2).replace("\n", "\n  ") + ",\n"
def _atomic_article_path(app_path: str, article_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,119}", article_id):
        raise ValueError("Invalid article ID for atomic publishing")
    return Path(app_path).parent / "articles" / "published" / f"{article_id}.json"


def _publish_atomic(app_path: str, article: dict, agent_name: str, text: str) -> None:
    article_id = str(article.get("id") or "")
    dest = _atomic_article_path(app_path, article_id)
    # Legacy App still contains all earlier articles during the zero-loss transition.
    if f'"{article_id}"' in text or f'id: "{article_id}"' in text:
        raise RuntimeError("podvojen ID")
    existing = dest.parent.glob("*.json") if dest.parent.is_dir() else []
    for path in existing:
        if path.name == dest.name:
            raise RuntimeError("podvojen ID")
        try:
            if json.loads(path.read_text(encoding="utf-8")).get("id") == article_id:
                raise RuntimeError("podvojen ID")
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Invalid existing atomic article: {path.name}") from exc
    data = json.loads(to_js_object(article, agent_name).strip().removesuffix(","))
    dest.parent.mkdir(parents=True, exist_ok=True)
    # One file per article; a crash never truncates App.jsx or a previous article.
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", dir=dest.parent,
        prefix=f".{article_id}.", suffix=".tmp", delete=False,
    ) as temp:
        temp_path = Path(temp.name)
        try:
            json.dump(data, temp, ensure_ascii=False, indent=2)
            temp.write("\n")
            temp.flush()
            os.fsync(temp.fileno())
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise
    try:
        # Never silently overwrite an existing publication.
        if dest.exists():
            raise RuntimeError("podvojen ID")
        os.replace(temp_path, dest)
    finally:
        temp_path.unlink(missing_ok=True)


def publish_to_app(app_path: str, article: dict, agent_name: str) -> None:
    with open(app_path, "r", encoding="utf-8") as f:
        text = f.read()
    if ANCHOR not in text:
        raise RuntimeError("starterArticles sidro ni najdeno")
    if 'import.meta.glob("./articles/published/*.json"' in text:
        _publish_atomic(app_path, article, agent_name, text)
        return
    # Preserve legacy behavior for earlier releases and isolated test fixtures.
    if f'"{article["id"]}"' in text or f'id: "{article["id"]}"' in text:
        raise RuntimeError("podvojen ID")
    updated = text.replace(ANCHOR, ANCHOR + "\n" + to_js_object(article, agent_name), 1)
    with open(app_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(updated)
