from __future__ import annotations

import asyncio
from email.utils import parseaddr
from types import SimpleNamespace

from manager.db_v3 import StoreV3
from manager.gmail_v4 import GmailV4
from manager.mail_commands_v4 import GmailCommandLoopV4
from manager.command_bus_v2 import UniversalCommandBusV2
from manager import remote_v4


def _gmail(monkeypatch, tmp_path):
    monkeypatch.setenv("REPORT_TO_EMAIL", "owner@gmail.com")
    monkeypatch.setenv("GMAIL_FROM_EMAIL", "owner@gmail.com")
    monkeypatch.setenv("GMAIL_COMMAND_ALLOWED_SENDERS", "owner@gmail.com")
    monkeypatch.setenv("GMAIL_COMMANDS_ENABLED", "1")
    monkeypatch.setenv("GMAIL_REPORTING_ENABLED", "1")
    monkeypatch.setenv("GMAIL_COMMAND_REQUIRE_AUTH", "1")
    monkeypatch.setenv("GMAIL_OAUTH_CLIENT_FILE", str(tmp_path / "client.json"))
    monkeypatch.setenv("GMAIL_OAUTH_TOKEN_FILE", str(tmp_path / "token.json"))
    return GmailV4()


def _message(subject="[AGENT MANAGER] STATUS", authentication=None, labels=(), message_id="mail-1"):
    headers = [
        {"name": "From", "value": "Operator <owner@gmail.com>"},
        {"name": "Subject", "value": subject},
    ]
    for value in authentication or []:
        headers.append({"name": "Authentication-Results", "value": value})
    return {
        "id": message_id, "threadId": "t1", "labelIds": list(labels),
        "payload": {"headers": headers, "mimeType": "text/plain", "body": {}},
        "snippet": "Phone signature, please ignore",
    }


def test_reject_spoofed_from_with_no_gmail_auth(monkeypatch, tmp_path):
    gmail = _gmail(monkeypatch, tmp_path)
    details = gmail.message_details(_message())
    assert details["sender"] == "owner@gmail.com"
    assert not details["sender_authenticated"]


def test_accept_aligned_authenticated_gmail_from(monkeypatch, tmp_path):
    gmail = _gmail(monkeypatch, tmp_path)
    auth = "mx.google.com; spf=pass; dkim=pass; dmarc=pass (p=NONE) header.from=gmail.com"
    details = gmail.message_details(_message(authentication=[auth]))
    assert details["sender_authenticated"]
    assert details["authentication_method"] == "aligned_dmarc"


def test_accept_owners_sent_message(monkeypatch, tmp_path):
    gmail = _gmail(monkeypatch, tmp_path)
    details = gmail.message_details(_message(labels=["SENT"]))
    assert details["sender_authenticated"]
    assert details["authentication_method"] == "gmail_sent"


def test_cannot_override_google_failure_with_forged_later_result(monkeypatch, tmp_path):
    gmail = _gmail(monkeypatch, tmp_path)
    details = gmail.message_details(_message(authentication=[
        "mx.google.com; dmarc=fail (p=reject) header.from=gmail.com",
        "mx.google.com; dmarc=pass header.from=gmail.com",
    ]))
    assert not details["sender_authenticated"]


def test_rejected_email_is_idempotent_and_not_marked_read(monkeypatch, tmp_path):
    gmail = _gmail(monkeypatch, tmp_path)
    store = StoreV3(tmp_path / "db.sqlite")
    loop = GmailCommandLoopV4(store, gmail)
    calls = []
    monkeypatch.setattr(gmail, "get_message", lambda mid: _message(message_id=mid))
    monkeypatch.setattr(gmail, "mark_read", lambda mid: calls.append(("read", mid)))
    async def execute(*a, **k):
        calls.append(("execute", a))
        return {"status": "completed"}
    monkeypatch.setattr(loop.bus, "execute", execute)
    result = asyncio.run(loop.process_one("mail-1"))
    assert result["status"] == "denied"
    assert result["reason"] == "authentication_not_verified"
    assert not calls
    repeat = asyncio.run(loop.process_one("mail-1"))
    assert repeat["status"] == "duplicate"
    assert not calls


def test_authenticated_email_executes_subject_command_not_signature(monkeypatch, tmp_path):
    gmail = _gmail(monkeypatch, tmp_path)
    store = StoreV3(tmp_path / "db.sqlite")
    loop = GmailCommandLoopV4(store, gmail)
    auth = ["mx.google.com; dmarc=pass header.from=gmail.com"]
    monkeypatch.setattr(gmail, "get_message", lambda mid: _message(
        subject="[AGENT MANAGER] POMOC", authentication=auth, message_id=mid
    ))
    mailed = []
    monkeypatch.setattr(gmail, "send", lambda subject, body, recipient: mailed.append((subject, body, recipient)) or "reply-1")
    monkeypatch.setattr(gmail, "mark_read", lambda mid: None)
    commands = []
    async def execute(command, **kwargs):
        commands.append((command, kwargs))
        return {"status": "completed", "job_id": "job-1"}
    monkeypatch.setattr(loop.bus, "execute", execute)
    result = asyncio.run(loop.process_one("mail-2"))
    assert result["status"] == "completed"
    assert commands[0][0] == "POMOC"
    assert commands[0][1]["explicit_target"] == "manager"
    assert mailed[0][2] == "owner@gmail.com"


def test_short_mail_commands_dont_wake_ollama(monkeypatch, tmp_path):
    store = StoreV3(tmp_path / "db.sqlite")
    bus = UniversalCommandBusV2(store)
    async def must_not_run(*args, **kwargs):
        raise AssertionError("This operator command must not invoke Ollama")
    monkeypatch.setattr(bus.ai, "chat_json", must_not_run)
    for command in ("STATUS", "POMOC", "INCIDENTI", "RAM", "MODELI", "EMAIL STATUS", "OPRAVILA", "PREVERI AGENTE"):
        provider, plan = asyncio.run(bus.plan(command))
        assert provider == "deterministic"
        assert plan["steps"][0]["target"] in {"manager", "all"}


def test_manager_mail_help_returns_actual_capability_status():
    async def run():
        response = await remote_v4._manager_command("POMOC")
        assert response["action"] == "help"
        assert "[AGENT MANAGER]" in response["result"]["subject_formats"]
        assert "Github CI/Pages" in response["result"]["remote_project_visibility"]
    asyncio.run(run())


def test_manager_ram_returns_health_resources_no_inference(monkeypatch):
    async def fake_http(method, url, **kwargs):
        assert method == "GET"
        assert url.endswith("/health")
        return {"ok": True, "resources": {"ram_available_gb": 3.09}}
    monkeypatch.setattr(remote_v4, "_http", fake_http)
    response = asyncio.run(remote_v4._manager_command("RAM"))
    assert response["result"]["ram_available_gb"] == 3.09



def test_all_status_aliases_never_fan_out_remote_agent_commands(monkeypatch):
    calls = []
    async def fake_status():
        calls.append("fleet")
        return {"ok": True, "manager": {"ok": True}}
    async def forbidden(*args, **kwargs):
        raise AssertionError("Status must not become an executable remote command")
    monkeypatch.setattr(remote_v4, "_fleet_status", fake_status)
    monkeypatch.setattr(remote_v4, "_project_command", forbidden)
    monkeypatch.setattr(remote_v4, "_bloglab_command", forbidden)
    for name in ("STATUS", "STATUS VSEH AGENTOV", "PREVERI STATUS", "FLOTA"):
        result = asyncio.run(remote_v4._dispatch("all", name))
        assert result["ok"]
    assert calls == ["fleet"] * 4
