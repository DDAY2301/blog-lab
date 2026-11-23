from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

from manager.command_bus_v2 import UniversalCommandBusV2
from manager.db_v3 import StoreV3
from manager import remote_v4


def test_pv_preview_dispatch_is_remote_and_never_claims_complete(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    monkeypatch.setenv("AGENT_MANAGER_GITHUB_TOKEN", "fake-token-unit-test")
    calls = []

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def post(self, url, **kwargs):
            calls.append((url, kwargs))
            return SimpleNamespace(status_code=204)

    monkeypatch.setattr(remote_v4.httpx, "AsyncClient", FakeClient)
    config = {
        "name": "Example public preview",
        "pages": [{"slug": "index", "title": "Home"}],
    }
    result = asyncio.run(remote_v4._project_command(
        "PREVIEW_JSON " + json.dumps(config)
    ))
    assert result["accepted"] is True
    assert result["completed"] is False
    assert len(result["request_id"]) == 32
    assert len(calls) == 1
    assert calls[0][0].endswith("/pv-remote-preview-v8.yml/dispatches")
    assert calls[0][1]["json"]["inputs"]["request_id"] == result["request_id"]
    assert "fake-token" not in json.dumps(result)


def test_pv_unstructured_preview_rejected(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    async def run():
        try:
            await remote_v4._project_command("PREVIEW_JSON not-json")
            raise AssertionError("Invalid JSON must be rejected")
        except ValueError:
            pass
    asyncio.run(run())


def test_async_dispatch_receipt_has_submitted_status(tmp_path, monkeypatch):
    store = StoreV3(tmp_path / "manager.sqlite")
    store.execute(
        """INSERT INTO mail_commands(message_id,sender,subject,target,command_text,status,received_at)
           VALUES(?,?,?,?,?,?,?)""",
        ("m1", "owner@example.com", "[AGENT PV]", "project_visibility",
         "TEST API", "processing", "now"),
    )
    monkeypatch.setenv("AGENT_MANAGER_EMAIL_V8_ENABLED", "1")
    bus = UniversalCommandBusV2(store)

    async def remote_dispatch(target, command):
        return {"ok": True, "accepted": True, "completed": False,
                "request_id": "abcd" * 8}
    monkeypatch.setattr("manager.command_bus_v2._dispatch", remote_dispatch)
    result = asyncio.run(bus.execute(
        "TEST API", source="gmail", source_id="m1",
        explicit_target="project_visibility",
    ))
    assert result["status"] == "submitted"
    assert result["steps"][0]["status"] == "submitted"
    info = bus.controls.inspect(result["job_id"], "owner@example.com")
    assert info["job"]["status"] == "submitted"
    assert "abcd" in info["steps"][0]["result_json"]
