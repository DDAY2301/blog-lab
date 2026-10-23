from __future__ import annotations

import asyncio
import base64

from manager.artifacts_v2 import ArtifactStoreV2
from manager.command_bus_v2 import UniversalCommandBusV2
from manager.db_v3 import StoreV3
from manager.gmail_v4 import GmailV4
from manager.manager_prompt_v5 import MANAGER_PROMPT_VERSION, planner_prompt, prompt_digest


def _store(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_ARTIFACT_ROOT", str(tmp_path / "artifacts"))
    return StoreV3(tmp_path / "manager.db")


def test_artifact_store_is_bounded_and_public_view_hides_local_path(tmp_path, monkeypatch):
    store = _store(tmp_path, monkeypatch)
    artifacts = ArtifactStoreV2(store)
    row = artifacts.save_bytes(
        source="gmail",
        source_id="msg-1",
        filename="../brief.txt",
        mime_type="text/plain",
        data=b"hello world",
    )
    assert row["filename"] == "brief.txt"
    assert artifacts.text_excerpt(row) == "hello world"
    public = artifacts.public_view(row)
    assert public["filename"] == "brief.txt"
    assert "local_path" not in public


def test_gmail_message_details_discovers_inline_image(monkeypatch, tmp_path):
    monkeypatch.setenv("GMAIL_COMMANDS_ENABLED", "1")
    monkeypatch.setenv("GMAIL_REPORTING_ENABLED", "1")
    monkeypatch.setenv("REPORT_TO_EMAIL", "dan.grmusa@gmail.com")
    monkeypatch.setenv("GMAIL_FROM_EMAIL", "dan.grmusa@gmail.com")
    monkeypatch.setenv("GMAIL_OAUTH_CLIENT_FILE", str(tmp_path / "client.json"))
    monkeypatch.setenv("GMAIL_OAUTH_TOKEN_FILE", str(tmp_path / "token.json"))
    gmail = GmailV4()
    image = base64.urlsafe_b64encode(b"fake-image-bytes").decode("ascii").rstrip("=")
    message = {
        "id": "m1",
        "threadId": "t1",
        "payload": {
            "headers": [
                {"name": "From", "value": "Dan <dan.grmusa@gmail.com>"},
                {"name": "Subject", "value": "[AGENT BLOGLAB] article"},
            ],
            "mimeType": "multipart/mixed",
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": base64.urlsafe_b64encode(b"use the image").decode("ascii")},
                },
                {
                    "mimeType": "image/png",
                    "filename": "hero.png",
                    "body": {"data": image, "size": 16},
                },
            ],
        },
    }
    details = gmail.message_details(message)
    assert details["body"] == "use the image"
    assert len(details["attachments"]) == 1
    assert details["attachments"][0]["filename"] == "hero.png"
    assert gmail.attachment_bytes("m1", details["attachments"][0]) == b"fake-image-bytes"


def test_explicit_bloglab_command_uploads_image_and_passes_url(tmp_path, monkeypatch):
    async def run():
        store = _store(tmp_path, monkeypatch)
        bus = UniversalCommandBusV2(store)
        artifact = bus.artifacts.save_bytes(
            source="gmail",
            source_id="msg-2",
            filename="hero.jpg",
            mime_type="image/jpeg",
            data=b"jpeg-data",
        )
        captured = {}

        async def fake_upload(row, cache):
            return {"ok": True, "url": "https://example.invalid/hero.jpg"}

        async def fake_dispatch(target, command):
            captured["target"] = target
            captured["command"] = command
            return {"accepted": True}

        monkeypatch.setattr(bus, "_upload_bloglab_image", fake_upload)
        monkeypatch.setattr("manager.command_bus_v2._dispatch", fake_dispatch)

        result = await bus.execute(
            "Dodaj članek s priloženo sliko.",
            source="gmail",
            source_id="msg-2",
            explicit_target="bloglab",
            artifacts=[artifact],
        )
        assert result["status"] == "completed"
        assert captured["target"] == "bloglab"
        assert "https://example.invalid/hero.jpg" in captured["command"]
        assert "hero.jpg" in captured["command"]

    asyncio.run(run())

def test_ai_plan_can_execute_independent_multi_agent_steps(tmp_path, monkeypatch):
    async def run():
        store = _store(tmp_path, monkeypatch)
        bus = UniversalCommandBusV2(store)
        calls = []

        async def fake_chat(system, user):
            return "ollama/test", {
                "summary": "two independent tasks",
                "steps": [
                    {"id": "s1", "target": "manager", "command": "status", "depends_on": []},
                    {"id": "s2", "target": "bloglab", "command": "status", "depends_on": []},
                ],
            }

        async def fake_dispatch(target, command):
            calls.append((target, command))
            return {"ok": True}

        monkeypatch.setattr(bus.ai, "chat_json", fake_chat)
        monkeypatch.setattr("manager.command_bus_v2._dispatch", fake_dispatch)

        result = await bus.execute(
            "Preveri manager in BlogLab.",
            source="test",
            source_id="req-1",
        )
        assert result["status"] == "completed"
        assert {target for target, _ in calls} == {"manager", "bloglab"}
        assert len(result["steps"]) == 2

    asyncio.run(run())



def test_manager_brain_prompt_has_core_orchestration_rules():
    prompt = planner_prompt(max_steps=8, concurrency=2)
    assert MANAGER_PROMPT_VERSION == "manager-brain-v5.0"
    assert len(prompt_digest()) == 16
    assert "Prefer the simplest plan" in prompt
    assert "Parallelize independent work" in prompt
    assert "Verify meaningful changes" in prompt
    assert "Never use an unregistered target id" in prompt
    assert "attachments" in prompt.lower()
    assert "Return JSON only" in prompt


def test_ai_planner_receives_manager_brain_v5(tmp_path, monkeypatch):
    async def run():
        store = _store(tmp_path, monkeypatch)
        bus = UniversalCommandBusV2(store)
        seen = {}

        async def fake_chat(system, user):
            seen["system"] = system
            seen["user"] = user
            return "ollama/test", {
                "summary": "status check",
                "steps": [
                    {"id": "s1", "target": "manager", "command": "status", "depends_on": []}
                ],
            }

        monkeypatch.setattr(bus.ai, "chat_json", fake_chat)
        provider, plan = await bus.plan("Preveri manager.")
        assert provider == "ollama/test"
        assert plan["steps"][0]["target"] == "manager"
        assert MANAGER_PROMPT_VERSION in seen["user"]
        assert "PRIORITIES — IN THIS ORDER" in seen["system"]
        assert "REGISTERED AGENTS" in seen["user"]

    asyncio.run(run())
