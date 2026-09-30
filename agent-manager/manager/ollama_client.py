from __future__ import annotations

import json
import os
from dataclasses import dataclass

import httpx


@dataclass
class OllamaClient:
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    preferred_model: str = os.getenv("AGENT_MANAGER_MODEL", "qwen3-coder:30b")
    fallback_models: tuple[str, ...] = tuple(
        x.strip()
        for x in os.getenv(
            "AGENT_MANAGER_FALLBACK_MODELS",
            "qwen2.5-coder:7b,devstral",
        ).split(",")
        if x.strip()
    )
    timeout: float = 180.0

    async def available_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url.rstrip('/')}/api/tags")
            response.raise_for_status()
            payload = response.json()
        return [str(m.get("name")) for m in payload.get("models", []) if m.get("name")]

    async def choose_model(self) -> str:
        available = await self.available_models()
        if self.preferred_model in available:
            return self.preferred_model

        normalized = {m.split(":")[0]: m for m in available}
        for candidate in self.fallback_models:
            if candidate in available:
                return candidate
            short = candidate.split(":")[0]
            if short in normalized:
                return normalized[short]

        if available:
            return available[0]
        raise RuntimeError(
            "Ollama is running but no local model is installed. "
            "Install one with: ollama pull qwen3-coder:30b"
        )

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
            "options": {"temperature": 0.1},
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
