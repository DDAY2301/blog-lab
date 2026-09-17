from __future__ import annotations
import json, os
from urllib.request import Request, urlopen

class AIUnavailable(RuntimeError):
    pass

def generate(system_prompt: str, task_prompt: str, source_items: list[dict]) -> dict:
    provider = os.getenv("AI_PROVIDER", "auto").lower()
    key = os.getenv("MODEL_API_KEY", "").strip()
    base = os.getenv("MODEL_BASE_URL", "").strip()
    model = os.getenv("MODEL_NAME", "").strip()
    if provider == "mock" or not (key and base and model):
        raise AIUnavailable("AI ni konfiguriran; tehnični mock test je uspešen, vsebina se ne objavi.")
    payload = {"model": model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": task_prompt + "\n\nVIRI:\n" + json.dumps(source_items, ensure_ascii=False)}], "temperature": 0.35, "response_format": {"type": "json_object"}}
    req = Request(base, data=json.dumps(payload).encode("utf-8"), headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=45) as r:
        data = json.loads(r.read().decode("utf-8"))
    try:
        return json.loads(data["choices"][0]["message"]["content"])
    except Exception as exc:
        raise AIUnavailable(f"Neveljaven odgovor AI ponudnika: {exc}") from exc
