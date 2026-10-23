"""No local PV worker: only trusted GitHub-hosted diagnostics are dispatchable."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from manager import remote_v4


def test_pv_status_uses_github_monitor_not_local_port(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    async def fake_http(method, url, **kwargs):
        assert method == "GET"
        assert url.endswith("/managed-agents")
        return {"status": [
            {
                "target_id": "project_visibility_github",
                "ok": 1,
                "last_check": "2026-10-11T12:00Z",
                "details": {"workflows": {"Agent API CI": {"conclusion": "success"}}},
            }
        ]}
    monkeypatch.setattr(remote_v4, "_http", fake_http)
    result = asyncio.run(remote_v4._project_command("status"))
    assert result["ok"]
    assert result["monitor_type"] == "github_workflows_not_live_agent"


def test_pv_supervisor_refuses_arbitrary_live_commands(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    async def run():
        with pytest.raises(RuntimeError, match="no local PV process"):
            await remote_v4._project_command("zgradi spletno stran brez omejitev")
    asyncio.run(run())


def test_pv_ci_requires_token(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    for name in ("AGENT_MANAGER_GITHUB_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    async def run():
        with pytest.raises(RuntimeError, match="fine-grained token"):
            await remote_v4._project_command("test api")
    asyncio.run(run())


def test_pv_ci_dispatches_allowlisted_workflow(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    monkeypatch.setenv("AGENT_MANAGER_GITHUB_TOKEN", "unit-test-do-not-use")
    called = []

    class Client:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc, tb):
            return False
        async def post(self, url, headers=None, json=None):
            called.append((url, headers, json))
            return SimpleNamespace(status_code=204)

    monkeypatch.setattr(remote_v4.httpx, "AsyncClient", Client)
    result = asyncio.run(remote_v4._project_command("TEST API"))
    assert result["accepted"] and not result["completed"]
    assert result["workflow"] == "agent-api-ci.yml"
    assert called[0][0].endswith("/actions/workflows/agent-api-ci.yml/dispatches")
    assert called[0][2] == {"ref": "main"}
    assert called[0][1]["Authorization"] == "Bearer unit-test-do-not-use"
    assert "unit-test-do-not-use" not in str(result)


def test_pv_frontend_benchmark_is_explicitly_allowed(monkeypatch):
    monkeypatch.setenv("AGENT_MANAGER_SUPERVISOR_ONLY", "1")
    calls = []
    async def fake_dispatch(workflow):
        calls.append(workflow)
        return {"accepted": True, "completed": False}
    monkeypatch.setattr(remote_v4, "_pv_github_workflow_dispatch", fake_dispatch)
    result = asyncio.run(remote_v4._project_command("frontend benchmark"))
    assert result["accepted"]
    assert calls == ["frontend-benchmark.yml"]


def test_pv_dispatch_rejects_unlisted_workflow():
    async def run():
        with pytest.raises(RuntimeError, match="allowlist"):
            await remote_v4._pv_github_workflow_dispatch("dangerous.yml")
    asyncio.run(run())
