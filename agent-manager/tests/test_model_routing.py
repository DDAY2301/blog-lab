import asyncio

from manager.ollama_client import OllamaClient


def test_auto_max_chooses_strongest_installed(monkeypatch) -> None:
    client = OllamaClient(
        preferred_model="auto-max",
        capability_priority=(
            "qwen3.8:27b-q8_0",
            "qwen3.8:27b",
            "devstral-small-2",
        ),
    )

    async def fake_models() -> list[str]:
        return ["devstral-small-2:latest", "qwen3.8:27b"]

    monkeypatch.setattr(client, "available_models", fake_models)
    assert asyncio.run(client.choose_model()) == "qwen3.8:27b"


def test_explicit_quality_tag_is_not_downgraded_by_alias(monkeypatch) -> None:
    client = OllamaClient(
        preferred_model="auto-max",
        capability_priority=("qwen3.8:27b-q8_0", "qwen3.8:27b"),
    )

    async def fake_models() -> list[str]:
        return ["qwen3.8:27b"]

    monkeypatch.setattr(client, "available_models", fake_models)
    assert asyncio.run(client.choose_model()) == "qwen3.8:27b"
