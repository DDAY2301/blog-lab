"""V8 migration is opt-in; existing V7 mail commands keep working by default."""
from __future__ import annotations

import asyncio

from manager.command_bus_v2 import UniversalCommandBusV2
from manager.db_v3 import StoreV3
from manager.gmail_v4 import GmailV4
from manager.mail_commands_v4 import GmailCommandLoopV4


def test_v7_keeps_existing_freeform_dispatch_by_default(monkeypatch, tmp_path):
    monkeypatch.delenv("AGENT_MANAGER_EMAIL_V8_ENABLED", raising=False)
    store = StoreV3(tmp_path / "legacy.sqlite")
    store.execute(
        """INSERT INTO mail_commands(message_id,thread_id,sender,subject,target,
           command_text,status,received_at) VALUES(?,?,?,?,?,?,?,?)""",
        ("m1", "t1", "owner@example.com", "[AGENT BLOGLAB]", "bloglab",
         "objavi clanek", "processing", "now"),
    )
    bus = UniversalCommandBusV2(store)
    assert bus.v8_enabled is False
    calls = []
    async def _fake(target, command):
        calls.append((target, command))
        return {"ok": True}
    monkeypatch.setattr("manager.command_bus_v2._dispatch", _fake)
    result = asyncio.run(bus.execute(
        "objavi clanek", source="gmail", source_id="m1",
        explicit_target="bloglab",
    ))
    assert result["status"] == "completed"
    assert calls == [("bloglab", "objavi clanek")]
    assert not store.query(
        "SELECT job_id FROM job_control_v8 WHERE sender=?", ("owner@example.com",)
    )


def test_v8_role_and_queue_not_enabled_until_operator_optin(monkeypatch, tmp_path):
    monkeypatch.delenv("AGENT_MANAGER_EMAIL_V8_ENABLED", raising=False)
    monkeypatch.setenv("REPORT_TO_EMAIL", "owner@example.com")
    monkeypatch.setenv("GMAIL_FROM_EMAIL", "owner@example.com")
    gmail = GmailV4()
    store = StoreV3(tmp_path / "manager.sqlite")
    loop = GmailCommandLoopV4(store, gmail)
    assert not loop.v8_enabled
    assert loop.status()["email_control_version"] == "v7-compat"

    monkeypatch.setenv("AGENT_MANAGER_EMAIL_V8_ENABLED", "1")
    enabled = GmailCommandLoopV4(store, gmail)
    assert enabled.v8_enabled
    assert enabled.status()["email_control_version"] == "v8-preview"
