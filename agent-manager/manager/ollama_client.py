from __future__ import annotations

import json
import os
from dataclasses import dataclass

import httpx


DEFAULT_MAX_CAPABILITY_MODELS = (
    # Local-first coding stack. Stable aliases are created by setup-max-model.ps1.
    # KAT-Coder-V2.5-Dev is post-trained on Qwen3.6-35B-A3B and is the preferred
    # engineering/autofix model. Qwen3.6 is the general reasoning fallback.
    "bloglab-katcoder-efficient",
    "bloglab-qwen36-efficient",
    "frob/kat-coder-v2.5-dev:35b-a3b-q4_K_M",
    "qwen3.6:35b-a3b-coding",
    "qwen3.6:35b-a3b",
    "qwen3-coder-next",
    "devstral-small-2",
    "qwen3-coder:30b",
    "qwen2.5-coder:7b",
)


def _csv_env(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return tuple(x.strip() for x in raw.split(",") if x.strip())


@dataclass
class OllamaClient:
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    preferred_model: str = os.getenv("AGENT_MANAGER_MODEL", "auto-max")
    capability_priority: tuple[str, ...] = _csv_env(
        "AGENT_MANAGER_MAX_CAPABILITY_MODELS",
        DEFAULT_MAX_CAPABILITY_MODELS,
    )
    fallback_models: tuple[str, ...] = _csv_env(
        "AGENT_MANAGER_FALLBACK_MODELS",
        ("bloglab-qwen36-efficient", "qwen3-coder-next", "devstral-small-2", "qwen2.5-coder:7b"),
    )
    timeout: float = 300.0

    async def available_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url.rstrip('/')}/api/tags")
            response.raise_for_status()
            payload = response.json()
        return [
            str(model.get("name"))
            for model in payload.get("models", [])
            if model.get("name")
        ]

    @staticmethod
    def _match_model(candidate: str, available: list[str]) -> str | None:
        if candidate in available:
            return candidate

        # Only aliases without an explicit tag may match another tag of the
        # same model family. Explicit quality tags must remain exact.
        if ":" not in candidate:
            for model in available:
                if model == candidate or model.split(":", 1)[0] == candidate:
                    return model
        return None

    async def choose_model(self) -> str:
        available = await self.available_models()
        if not available:
            raise RuntimeError(
                "Ollama is running but no local model is installed. "
                "Run: .\\setup-max-model.ps1"
            )

        if self.preferred_model.strip().lower() in {
            "auto",
            "auto-max",
            "max",
            "maximum",
        }:
            for candidate in self.capability_priority:
                match = self._match_model(candidate, available)
                if match:
                    return match
        else:
            match = self._match_model(self.preferred_model, available)
            if match:
                return match

        for candidate in self.fallback_models:
            match = self._match_model(candidate, available)
            if match:
                return match

        # Last-resort behavior keeps the system running if a user only has a
        # different Ollama model installed.
        return available[0]

    async def chat_json(self, system: str, user: str) -> tuple[str, dict]:
        model = await self.choose_model()
        body = {
            "model": model,
            "stream": False,
            "format": "json",
            "keep_alive": os.getenv("AGENT_MANAGER_OLLAMA_KEEP_ALIVE", "60s"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # Low temperature is deliberate for autonomous code changes.
            "options": {
                "temperature": 0.05,
                "num_ctx": int(os.getenv("AGENT_MANAGER_CONTEXT", "8192")),
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url.rstrip('/')}/api/chat",
                json=body,
            )
            response.raise_for_status()
            payload = response.json()

        content = str(payload.get("message", {}).get("content", "")).strip()
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"summary": content}
        return model, parsed
