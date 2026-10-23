"""Preview receipt reconciliation must never confuse queue acceptance and success."""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

from manager.db_v3 import StoreV3, utcnow
from manager.job_control_v8 import JobControlV8
from manager.remote_run_watcher_v8 import RemoteRunWatcherV8


REQUEST = "0123456789abcdef0123456789abcdef"


def _store(tmp_path):
    store = StoreV3(tmp_path / "watcher.sqlite")
    store.execute(
        """INSERT INTO command_jobs(
            id,source,source_id,request_text,status,plan_json,created_at,updated_at
            ) VALUES(?,?,?,?,?,?,?,?)""",
        ("job-1", "gmail", "mail-1", "preview", "submitted",
         "{}", utcnow(), utcnow()),
    )
    JobControlV8(store).bind("job-1", "owner@example.com", "mail-thread-1")
    receipt = {
        "operation": "remote_preview", "workflow": "pv-remote-preview-v8.yml",
        "repo": "DDAY2301/PROJEKT", "request_id": REQUEST,
        "accepted": True, "completed": False,
    }
    store.execute(
        """INSERT INTO command_steps(
            job_id,step_id,target,command_text,status,result_json
            ) VALUES(?,?,?,?,?,?)""",
        ("job-1", "step-1", "project_visibility", "preview",
         "submitted", json.dumps(receipt)),
    )
    return store


def _fake_http(monkeypatch, *, state="completed", conclusion="success",
               include_artifact=True, run_id=501):
    from manager import remote_run_watcher_v8
    urls = []
    class Client:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def get(self, url, headers=None, params=None):
            urls.append(url)
            assert headers["Authorization"] == "Bearer test-gh-token"
            if url.endswith("/artifacts"):
                return SimpleNamespace(
                    status_code=200,
                    json=lambda: {"artifacts": ([{
                        "id": 801, "name": f"pv-preview-{run_id}",
                        "size_in_bytes": 32510, "expired": False,
                    }] if include_artifact else [])},
                )
            return SimpleNamespace(
                status_code=200,
                json=lambda: {"workflow_runs": [{
                    "id": run_id,
                    "display_title": "PV Preview V8 " + REQUEST,
                    "status": state, "conclusion": conclusion,
                    "event": "workflow_dispatch", "head_branch": "main",
                }]},
            )
    monkeypatch.setattr(remote_run_watcher_v8.httpx, "AsyncClient", Client)
    return urls


def test_succeeds_only_with_matching_run_and_artifact(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_MANAGER_GITHUB_TOKEN", "test-gh-token")
    store = _store(tmp_path)
    urls = _fake_http(monkeypatch)
    watcher = RemoteRunWatcherV8(store)
    result = asyncio.run(watcher.cycle())
    assert result["updated"] == 1
    assert any(u.endswith("/501/artifacts") for u in urls)
    step = store.query("SELECT status,result_json FROM command_steps")[0]
    assert step["status"] == "completed"
    receipt = json.loads(step["result_json"])
    assert receipt["run_id"] == 501
    assert receipt["artifact"]["name"] == "pv-preview-501"
    assert store.query("SELECT status FROM command_jobs")[0]["status"] == "completed"
    emails = store.query("SELECT * FROM email_queue WHERE kind='v8-remote-pv'")
    assert len(emails) == 1
    assert emails[0]["recipient"] == "owner@example.com"
    assert "pv-preview-501" in emails[0]["body"]
    assert asyncio.run(watcher.cycle())["status"] == "idle"


def test_failed_remote_run_marks_job_failed(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_MANAGER_GITHUB_TOKEN", "test-gh-token")
    store = _store(tmp_path)
    _fake_http(monkeypatch, conclusion="failure")
    asyncio.run(RemoteRunWatcherV8(store).cycle())
    assert store.query("SELECT status FROM command_jobs")[0]["status"] == "failed"
    assert store.query("SELECT status FROM command_steps")[0]["status"] == "failed"


def test_in_progress_is_not_falsely_completed(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_MANAGER_GITHUB_TOKEN", "test-gh-token")
    store = _store(tmp_path)
    urls = _fake_http(monkeypatch, state="in_progress", conclusion=None)
    asyncio.run(RemoteRunWatcherV8(store).cycle())
    assert store.query("SELECT status FROM command_jobs")[0]["status"] == "submitted"
    assert store.query("SELECT status FROM command_steps")[0]["status"] == "running"
    assert not any(x.endswith("/artifacts") for x in urls)


def test_missing_artifact_keeps_job_pending(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_MANAGER_GITHUB_TOKEN", "test-gh-token")
    store = _store(tmp_path)
    _fake_http(monkeypatch, include_artifact=False)
    asyncio.run(RemoteRunWatcherV8(store).cycle())
    assert store.query("SELECT status FROM command_steps")[0]["status"] == "submitted"


def test_no_token_does_not_claim_success(monkeypatch, tmp_path):
    for name in ("AGENT_MANAGER_GITHUB_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    store = _store(tmp_path)
    result = asyncio.run(RemoteRunWatcherV8(store).cycle())
    assert result["status"] == "credentials_missing"
    assert store.query("SELECT status FROM command_jobs")[0]["status"] == "submitted"


def test_only_approved_workflow_reconciled(monkeypatch, tmp_path):
    monkeypatch.setenv("AGENT_MANAGER_GITHUB_TOKEN", "test-gh-token")
    store = _store(tmp_path)
    store.execute(
        "UPDATE command_steps SET result_json=?",
        (json.dumps({"workflow": "arbitrary.yml",
                     "repo": "DDAY2301/PROJEKT", "operation": "remote_preview",
                     "request_id": REQUEST}),),
    )
    assert asyncio.run(RemoteRunWatcherV8(store).cycle())["status"] == "idle"
