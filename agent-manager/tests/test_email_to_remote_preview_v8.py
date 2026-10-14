"""End-to-end *simulated* owner email -> PV dispatch -> run verify -> mail reply.

No real OAuth, public GitHub traffic or production publication is performed.
"""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

from manager.db_v3 import StoreV3
from manager.gmail_v4 import GmailV4
from manager.mail_commands_v4 import GmailCommandLoopV4
from manager.remote_run_watcher_v8 import RemoteRunWatcherV8
from manager import remote_v4
from manager import remote_run_watcher_v8

RID = "0123456789abcdef0123456789abcdef"


def test_owner_email_to_verified_remote_artifact(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORT_TO_EMAIL", "owner@gmail.com")
    monkeypatch.setenv("GMAIL_FROM_EMAIL", "owner@gmail.com")
    monkeypatch.setenv("GMAIL_COMMAND_ALLOWED_SENDERS", "owner@gmail.com")
    monkeypatch.setenv("GMAIL_COMMANDS_ENABLED", "1")
    monkeypatch.setenv("GMAIL_REPORTING_ENABLED", "1")
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    monkeypatch.setenv("AGENT_MANAGER_EMAIL_V8_ENABLED", "1")
    monkeypatch.setenv("AGENT_MANAGER_GITHUB_TOKEN", "unit-test-gh-token")
    store = StoreV3(tmp_path / "end-to-end.sqlite")
    gmail = GmailV4()
    loop = GmailCommandLoopV4(store, gmail)
    brief = '{"name":"Example","pages":[{"slug":"index","title":"Home"}]}'
    message = {
        "id": "owner-mail-1", "threadId": "thread-1", "labelIds": ["SENT"],
        "payload": {
            "headers": [
                {"name": "From", "value": "owner@gmail.com"},
                {"name": "Subject", "value": "[AGENT PV] PREVIEW_JSON " + brief},
            ],
            "mimeType": "text/plain", "body": {},
        },
        "snippet": "",
    }
    monkeypatch.setattr(gmail, "get_message", lambda mid: message)
    monkeypatch.setattr(gmail, "mark_read", lambda mid: None)
    replies = []
    monkeypatch.setattr(gmail, "send", lambda sub, body, to: replies.append(
        (sub, body, to)) or "outbound-mail-1")
    async def pv_dispatch(command):
        assert command.startswith("PREVIEW_JSON ")
        return {
            "ok": True, "accepted": True, "completed": False,
            "operation": "remote_preview", "workflow": "pv-remote-preview-v8.yml",
            "repo": "DDAY2301/PROJEKT", "request_id": RID,
        }
    monkeypatch.setattr(remote_v4, "_project_command", pv_dispatch)
    result = asyncio.run(loop.process_one("owner-mail-1"))
    assert result["status"] == "submitted"
    assert len(replies) == 1
    job_id = result["job_id"]
    assert store.query("SELECT status FROM command_jobs")[0]["status"] == "submitted"

    class MockGithub:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def get(self, url, headers=None, params=None):
            assert headers["Authorization"] == "Bearer unit-test-gh-token"
            if url.endswith("/artifacts"):
                return SimpleNamespace(
                    status_code=200,
                    json=lambda: {"artifacts": [
                        {"id": 41, "name": "pv-preview-101",
                         "size_in_bytes": 1000, "expired": False},
                    ]},
                )
            return SimpleNamespace(
                status_code=200,
                json=lambda: {"workflow_runs": [
                    {"id": 101, "display_title": "PV Preview V8 " + RID,
                     "event": "workflow_dispatch", "head_branch": "main",
                     "status": "completed", "conclusion": "success"},
                ]},
            )
    monkeypatch.setattr(remote_run_watcher_v8.httpx, "AsyncClient", MockGithub)
    watcher = RemoteRunWatcherV8(store)
    assert asyncio.run(watcher.cycle())["updated"] == 1
    assert store.query(
        "SELECT status FROM command_jobs WHERE id=?", (job_id,)
    )[0]["status"] == "completed"
    queued = store.query(
        "SELECT * FROM email_queue WHERE kind='v8-remote-pv'"
    )
    assert len(queued) == 1
    assert job_id in queued[0]["subject"]
    assert queued[0]["recipient"] == "owner@gmail.com"
    assert queued[0]["status"] == "pending"
    assert "pv-preview-101" in queued[0]["body"]
    assert asyncio.run(watcher.cycle())["status"] == "idle"
    assert len(store.query(
        "SELECT * FROM email_queue WHERE kind='v8-remote-pv'"
    )) == 1
