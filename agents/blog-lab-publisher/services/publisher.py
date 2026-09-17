from __future__ import annotations
import json, re
from datetime import datetime
from zoneinfo import ZoneInfo
ANCHOR = "const starterArticles = ["
def slugify(text: str) -> str:
    repl = {"č":"c","š":"s","ž":"z","ć":"c","đ":"d"}
    text = "".join(repl.get(c.lower(), c.lower()) for c in text)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:90] or "objava"
def to_js_object(article: dict, agent_name: str) -> str:
    now = datetime.now(ZoneInfo("Europe/Ljubljana")).isoformat(timespec="seconds")
    obj = {"id":article["id"],"title":article["title"],"excerpt":article["excerpt"],"seoDescription":article["seoDescription"],"content":article["content"],"category":article["category"],"author":agent_name,"status":article.get("status","published"),"createdAt":now,"updatedAt":now}
    return "  " + json.dumps(obj, ensure_ascii=False, indent=2).replace("\n", "\n  ") + ",\n"
def publish_to_app(app_path: str, article: dict, agent_name: str) -> None:
    with open(app_path, "r", encoding="utf-8") as f: text = f.read()
    if ANCHOR not in text: raise RuntimeError("starterArticles sidro ni najdeno")
    if f'"{article["id"]}"' in text or f'id: "{article["id"]}"' in text: raise RuntimeError("podvojen ID")
    updated = text.replace(ANCHOR, ANCHOR + "\n" + to_js_object(article, agent_name), 1)
    with open(app_path, "w", encoding="utf-8", newline="\n") as f: f.write(updated)
