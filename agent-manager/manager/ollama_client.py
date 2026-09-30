from __future__ import annotations

import json
import os
from dataclasses import dataclass

import httpx


DEFAULT_MAX_CAPABILITY_MODELS = (
    # Use the strongest installed local model first.
    # The first entry is extremely large and will only be selected if the user
    # explicitly installed it on suitable hardware.
    "qwen3.8-flash-next:125b-a6b-q4_K_M",
    "qwen3.8:27b-q8_0",
    "qwen3.8:27b",
    "qwen3.8",
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
        ("qwen3.8", "qwen3-coder-next", "devstral-small-2", "qwen2.5-coder:7b"),
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
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # Low temperature is deliberate for autonomous code changes.
            "options": {
                "temperature": 0.05,
                "num_ctx": int(os.getenv("AGENT_MANAGER_CONTEXT", "65536")),
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
