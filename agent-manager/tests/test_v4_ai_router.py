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
