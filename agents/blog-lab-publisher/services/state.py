from __future__ import annotations
import json, os, tempfile
from pathlib import Path
def load_json(path: str, default):
    p = Path(path)
    if not p.exists(): return default
    return json.loads(p.read_text(encoding="utf-8"))
def atomic_json(path: str, data) -> None:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=p.name, dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2); f.write("\n")
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
