from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .ollama_client import OllamaClient


@dataclass
class ProviderStatus:
    name: str
    ok: bool
    model: str | None = None
    latency_ms: float | None = None
    error: str | None = None
    detail: dict[str, Any] | None = None


class ColibriClient:
    """OpenAI-compatible client for colibri v2.x (coli serve / coli web)."""

    def __init__(self) -> None:
        self.base_url = os.getenv("COLIBRI_BASE_URL", "http://127.0.0.1:8790/v1").rstrip("/")
        self.health_url = os.getenv("COLIBRI_HEALTH_URL", self.base_url.removesuffix("/v1") + "/health")
        self.model = os.getenv("COLIBRI_MODEL", "").strip()
        self.api_key = os.getenv("COLIBRI_API_KEY", "").strip()
        self.timeout = float(os.getenv("COLIBRI_TIMEOUT", "300"))

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def available_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/models", headers=self._headers())
            r.raise_for_status()
            data = r.json()
        rows = data.get("data", data.get("models", []))
        out: list[str] = []
        for row in rows if isinstance(rows, list) else []:
            if isinstance(row, dict):
                value = row.get("id") or row.get("name")
                if value:
                    out.append(str(value))
            elif row:
                out.append(str(row))
        return out

    async def choose_model(self) -> str:
        models = await self.available_models()
        if self.model and self.model in models:
            return self.model
        if models:
            return models[0]
        raise RuntimeError("Colibri API is reachable but no model is loaded.")

    async def status(self) -> ProviderStatus:
        start = time.perf_counter()
        try:
            model = await self.choose_model()
            return ProviderStatus(
                name="colibri",
                ok=True,
                model=model,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
            )
        except Exception as exc:
            return ProviderStatus(
                name="colibri",
                ok=False,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
                error=str(exc),
            )

    async def system_one(self, state: str, questions: dict[str, Any]) -> dict[str, Any]:
        model = await self.choose_model()
        body = {"model": model, "state": state, "questions": questions}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/systemone",
                headers=self._headers(),
                json=body,
            )
            r.raise_for_status()
            return r.json()

    async def chat_json(self, system: str, user: str) -> tuple[str, dict]:
        model = await self.choose_model()
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "temperature": 0.05,
            "max_tokens": int(os.getenv("COLIBRI_MAX_TOKENS", "2048")),
        }
        effort = os.getenv("COLIBRI_REASONING_EFFORT", "high").strip().lower()
        if effort in {"low", "medium", "high", "xhigh"}:
            body["reasoning_effort"] = effort

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=body,
            )
            r.raise_for_status()
            data = r.json()

        content = str(
            ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "")
        ).strip()
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"summary": content}
        return f"colibri/{model}", parsed


class AIRouterV4:
    """Colibri-first AI router with Ollama fallback and deterministic availability."""

    def __init__(self) -> None:
        self.colibri = ColibriClient()
        self.ollama = OllamaClient()
        self.priority = [
            x.strip().lower()
            for x in os.getenv("AGENT_MANAGER_AI_PRIORITY", "colibri,ollama").split(",")
            if x.strip()
        ]
        self._fail_until: dict[str, float] = {}
        self.cooldown = max(15, int(os.getenv("AGENT_MANAGER_PROVIDER_COOLDOWN", "60")))

    async def status(self) -> dict[str, dict[str, Any]]:
        c = await self.colibri.status()
        start = time.perf_counter()
        try:
            model = await self.ollama.choose_model()
            o = ProviderStatus(
                name="ollama",
                ok=True,
                model=model,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
            )
        except Exception as exc:
            o = ProviderStatus(
                name="ollama",
                ok=False,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
                error=str(exc),
            )
        return {
            "colibri": c.__dict__,
            "ollama": o.__dict__,
            "priority": self.priority,
        }

    async def triage(self, state: str) -> dict[str, Any] | None:
        if self._fail_until.get("colibri", 0) > time.time():
            return None
        questions = {
            "severity": {
                "type": "choice",
                "instructions": "How severe is this operational incident?",
                "criteria": {
                    "P0": "system-wide outage, data corruption, or security emergency",
                    "P1": "critical service unavailable or repeated unrecovered failure",
                    "P2": "degraded service with a workaround or noncritical component failure",
                    "P3": "minor issue or maintenance concern"
                }
            },
            "action": {
                "type": "choice",
                "instructions": "Which safe response family fits best?",
                "criteria": {
                    "observe": "collect more evidence without changing the system",
                    "restart": "restart a reversible local service or worker",
                    "self_heal": "invoke an existing tested self-heal workflow",
                    "human": "human approval or credentials are required"
                }
            }
        }
        try:
            return await self.colibri.system_one(state, questions)
        except Exception:
            return None

    async def chat_json(self, system: str, user: str) -> tuple[str, dict]:
        now = time.time()
        errors: list[str] = []
        for provider in self.priority:
            if self._fail_until.get(provider, 0) > now:
                continue
            try:
                if provider == "colibri":
                    return await self.colibri.chat_json(system, user)
                if provider == "ollama":
                    model, result = await self.ollama.chat_json(system, user)
                    return f"ollama/{model}", result
            except Exception as exc:
                self._fail_until[provider] = now + self.cooldown
                errors.append(f"{provider}: {exc}")
        raise RuntimeError("No local AI provider is available. " + " | ".join(errors))
