import asyncio

from manager.db_v3 import StoreV3
from manager.gmail_v4 import GmailV4
from manager.mail_commands_v4 import GmailCommandLoopV4


def _make_loop(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORT_TO_EMAIL", "owner@gmail.com")
    monkeypatch.setenv("GMAIL_FROM_EMAIL", "owner@gmail.com")
    monkeypatch.setenv("GMAIL_COMMAND_ALLOWED_SENDERS", "owner@gmail.com")
    monkeypatch.setenv("GMAIL_COMMANDS_ENABLED", "1")
    monkeypatch.setenv("GMAIL_REPORTING_ENABLED", "1")
    store = StoreV3(tmp_path / "manager.db")
    gmail = GmailV4()
    loop = GmailCommandLoopV4(store, gmail)
    responses = []
    monkeypatch.setattr(gmail, "send", lambda subject, body, recipient:
                       responses.append((subject, body, recipient)) or "reply-1")
    monkeypatch.setattr(gmail, "mark_read", lambda message_id: None)
    return store, gmail, loop, responses


def _mail(message_id, subject, body=""):
    return {
        "id": message_id, "threadId": "thread-123", "labelIds": ["SENT"],
        "payload": {
            "headers": [
                {"name": "From", "value": "Owner <owner@gmail.com>"},
                {"name": "Subject", "value": subject},
            ],
            "mimeType": "text/plain",
            "body": {},
        },
        "snippet": body,
    }


def test_status_job_email_is_owner_checked(tmp_path, monkeypatch):
    store, gmail, loop, responses = _make_loop(tmp_path, monkeypatch)
    jid = "12345678-1234-1234-1234-123456789abc"
    store.execute(
        """INSERT INTO command_jobs(id,source,source_id,request_text,status,created_at,updated_at)
           VALUES(?,?,?,?,?,?,?)""",
        (jid, "gmail", "old-1", "status", "completed", "now", "now"),
    )
    loop.bus.controls.bind(jid, "owner@gmail.com", "thread-123")
    monkeypatch.setattr(gmail, "get_message", lambda mid: _mail(
        mid, f"[AGENT] STATUS JOB {jid}", "phone signature"
    ))
    result = asyncio.run(loop.process_one("new-1"))
    assert result["status"] == "completed"
    assert result["result"]["job"]["id"] == jid
    assert jid in responses[0][1]


def test_continue_links_new_job_not_rerun_original(tmp_path, monkeypatch):
    store, gmail, loop, responses = _make_loop(tmp_path, monkeypatch)
    jid = "12345678-1234-1234-1234-123456789abc"
    store.execute(
        """INSERT INTO command_jobs(id,source,source_id,request_text,status,created_at,updated_at)
           VALUES(?,?,?,?,?,?,?)""",
        (jid, "gmail", "old-1", "status", "completed", "now", "now"),
    )
    loop.bus.controls.bind(jid, "owner@gmail.com", "thread-123")
    monkeypatch.setattr(gmail, "get_message", lambda mid: _mail(
        mid, f"[AGENT MANAGER] CONTINUE JOB {jid}", "status"
    ))
    async def fake_dispatch(target, command):
        return {"ok": True, "command": command}
    monkeypatch.setattr("manager.command_bus_v2._dispatch", fake_dispatch)
    result = asyncio.run(loop.process_one("new-2"))
    assert result["status"] == "completed"
    next_job = result["result"]["job_id"]
    assert next_job != jid
    assert loop.bus.controls.inspect(next_job, "owner@gmail.com")["parent_id"] == jid


def test_approval_email_never_executes_pending_mutation(tmp_path, monkeypatch):
    store, gmail, loop, responses = _make_loop(tmp_path, monkeypatch)
    jid = "12345678-1234-1234-1234-123456789abc"
    loop.bus.controls.bind(jid, "owner@gmail.com")
    rid = loop.bus.controls.request_review(
        jid, "s1", "bloglab", "objavi clanek", "owner@gmail.com"
    )
    monkeypatch.setattr(gmail, "get_message", lambda mid: _mail(
        mid, f"[AGENT] APPROVE {rid}", "sent from my phone"
    ))
    result = asyncio.run(loop.process_one("new-3"))
    assert result["status"] == "completed"
    assert result["result"]["executed"] is False
    assert "Independent authenticated review" in result["result"]["message"]
