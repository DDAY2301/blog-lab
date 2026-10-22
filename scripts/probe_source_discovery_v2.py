"""Non-publishing live check for BlogLab Source Discovery V2.

Uses public search endpoints and read-only local data. No secrets or site changes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agents/blog-lab-publisher"))

from agent import automatic_source_usable  # noqa: E402
from services.learning import learning_source_ok  # noqa: E402
from services.source_discovery_v2 import collect_focused_sources, unpublished_items  # noqa: E402

CATEGORIES = ("kolesarstvo", "dediscina", "sezonsko", "gore", "gourmet")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--category", choices=CATEGORIES, default="dediscina")
    p.add_argument("--limit", type=int, default=30)
    args = p.parse_args()
    maximum = min(max(args.limit, 5), 30)
    history_path = ROOT / "data/processed-items.json"
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
    items = collect_focused_sources(args.category, max_items=maximum)
    relevant = [
        item for item in items
        if automatic_source_usable(item, args.category, trusted_primary=False)
        and learning_source_ok(item, args.category)
    ]
    fresh = unpublished_items(relevant, history, limit=maximum)
    print(
        f"DISCOVERY_V2_LIVE_PROBE category={args.category} "
        f"collected={len(items)} editorial_usable={len(relevant)} "
        f"new_unpublished={len(fresh)} (NO PUBLICATION)"
    )
    for item in fresh[:3]:
        host = (urlparse(str(item.get("url") or "")).hostname or "").lower()
        title = str(item.get("title") or "").replace("\n", " ")[:110]
        print(f"  candidate title={title!r} host={host} verified_direct={bool(item.get('verified_direct'))}")
    if not fresh:
        print("DISCOVERY_V2_EDITORIAL_HOLD: no suitable fresh candidates; never publish duplicates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
