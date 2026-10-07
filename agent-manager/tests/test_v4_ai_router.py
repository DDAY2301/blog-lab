import asyncio
from types import SimpleNamespace

from manager.ai_router_v4 import AIRouterV4


def test_router_falls_back_to_ollama(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_LOW_MEMORY_AI_SWAP", "0")
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
    monkeypatch.setenv("AGENT_MANAGER_LOW_MEMORY_AI_SWAP", "0")
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


def test_low_memory_triage_starts_and_releases_colibri(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_COLIBRI_PROFILE", "decision-laya")
    monkeypatch.setenv("AGENT_MANAGER_LOW_MEMORY_AI_SWAP", "1")
    router = AIRouterV4()

    released = {"value": False}

    async def colibri_offline():
        return SimpleNamespace(ok=False)

    async def prepare():
        return True

    async def system_one(state, questions):
        return {"answers": {"severity": {"choice": "P2"}}}

    async def release():
        released["value"] = True

    monkeypatch.setattr(router.colibri, "status", colibri_offline)
    monkeypatch.setattr(router, "_prepare_low_memory_colibri", prepare)
    monkeypatch.setattr(router.colibri, "system_one", system_one)
    monkeypatch.setattr(router, "_stop_colibri_after_triage", release)

    result = asyncio.run(router.triage("degraded target"))
    assert result["answers"]["severity"]["choice"] == "P2"
    assert released["value"] is True
