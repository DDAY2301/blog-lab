import asyncio

from manager.ai_router_v4 import AIRouterV4


def test_router_falls_back_to_ollama(monkeypatch):
    router = AIRouterV4()
    router.priority = ["colibri", "ollama"]

    async def colibri_fail(system, user):
        raise RuntimeError("offline")

    async def ollama_ok(system, user):
        return "qwen-test", {"summary": "ok"}

    monkeypatch.setattr(router.colibri, "chat_json", colibri_fail)
    monkeypatch.setattr(router.ollama, "chat_json", ollama_ok)

    provider, result = asyncio.run(router.chat_json("s", "u"))
    assert provider == "ollama/qwen-test"
    assert result["summary"] == "ok"


def test_decision_only_colibri_skips_chat_and_uses_ollama(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_COLIBRI_PROFILE", "decision-laya")
    router = AIRouterV4()
    router.priority = ["colibri", "ollama"]

    async def colibri_must_not_chat(system, user):
        raise AssertionError("decision-only Colibri must not receive chat requests")

    async def ollama_ok(system, user):
        return "qwen2.5-coder:3b", {"summary": "ollama-generation"}

    monkeypatch.setattr(router.colibri, "chat_json", colibri_must_not_chat)
    monkeypatch.setattr(router.ollama, "chat_json", ollama_ok)

    provider, result = asyncio.run(router.chat_json("system", "task"))
    assert provider == "ollama/qwen2.5-coder:3b"
    assert result["summary"] == "ollama-generation"
    assert router.colibri.decision_only is True
