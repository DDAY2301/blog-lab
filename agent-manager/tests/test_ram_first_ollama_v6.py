"""RAM-first profile: unload Ollama after completed Manager AI replies."""
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from manager.ollama_client import OllamaClient


def test_ram_first_keep_alive_is_forwarded_to_ollama(monkeypatch):
    from manager import ollama_client

    monkeypatch.setenv("AGENT_MANAGER_OLLAMA_KEEP_ALIVE", "0s")
    monkeypatch.setenv("AGENT_MANAGER_CONTEXT", "4096")
    client = OllamaClient(preferred_model="qwen2.5-coder:3b")

    async def choose_model():
        return "qwen2.5-coder:3b"

    monkeypatch.setattr(client, "choose_model", choose_model)
    captured = []

    class FakeHTTPClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

        async def post(self, url, json):
            captured.append({"url": url, "body": json})
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {"message": {"content": '{"summary":"complete"}'}},
            )

    monkeypatch.setattr(ollama_client.httpx, "AsyncClient", FakeHTTPClient)
    model, data = asyncio.run(client.chat_json("system", "user"))
    assert model == "qwen2.5-coder:3b"
    assert data == {"summary": "complete"}
    assert captured[0]["body"]["keep_alive"] == "0s"
    assert captured[0]["body"]["options"]["num_ctx"] == 4096
    assert captured[0]["url"].endswith("/api/chat")


def test_focus_profile_unloads_models_without_stopping_ollama():
    root = Path(__file__).resolve().parents[1] / "scripts"
    focus = (root / "optimize-windows11-safe.ps1").read_text(encoding="utf-8")
    startup = (root / "start-stack-v4.ps1").read_text(encoding="utf-8")
    assert 'AGENT_MANAGER_OLLAMA_KEEP_ALIVE = "0s"' in focus
    assert '"AGENT_MANAGER_OLLAMA_KEEP_ALIVE" = "0s"' in startup
    assert 'OLLAMA_KEEP_ALIVE              = "0s"' in focus
    assert '"OLLAMA_KEEP_ALIVE" = "0s"' in startup
    assert 'AGENT_MANAGER_SUPERVISOR_ONLY = "1"' in focus
    assert 'Supervisor-only: skip local Project Visibility' in startup
