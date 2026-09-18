from __future__ import annotations
import json, re
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
def publish_to_app(app_path: str, article: dict, agent_name: str) -> None:
    with open(app_path, "r", encoding="utf-8") as f: text = f.read()
    if ANCHOR not in text: raise RuntimeError("starterArticles sidro ni najdeno")
    if f'"{article["id"]}"' in text or f'id: "{article["id"]}"' in text: raise RuntimeError("podvojen ID")
    updated = text.replace(ANCHOR, ANCHOR + "\n" + to_js_object(article, agent_name), 1)
    with open(app_path, "w", encoding="utf-8", newline="\n") as f: f.write(updated)
