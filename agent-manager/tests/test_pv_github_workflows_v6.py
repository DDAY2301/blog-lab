"""Regression tests for Project Visibility GitHub health noise and pagination."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from manager.db_v3 import StoreV3
from manager.managed_agents_v4 import ManagedAgentSupervisorV4, ManagedTarget


def _supervisor(tmp_path):
    return ManagedAgentSupervisorV4(
        StoreV3(tmp_path / "manager.sqlite"),
        Path(__file__).resolve().parents[1] / "data" / "managed_agents.json",
    )


def _mock_http(monkeypatch, pages):
    from manager import managed_agents_v4
    requests = []

    class Client:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, headers=None, params=None):
            page = params["page"]
            requests.append(page)
            rows = pages.get(page, [])
            return SimpleNamespace(
                status_code=200, text="",
                json=lambda: {"workflow_runs": rows},
            )

    monkeypatch.setattr(managed_agents_v4.httpx, "AsyncClient", Client)
    return requests


def _run(name, conclusion, status="completed"):
    return {
        "name": name, "conclusion": conclusion, "status": status,
        "html_url": f"https://github.com/example/example/actions/runs/{name}",
        "created_at": "2026-10-11T11:39:08Z",
    }


def test_project_visibility_scope_tracks_current_workflows(tmp_path):
    sup = _supervisor(tmp_path)
    pv = next(t for t in sup.targets() if t.id == "project_visibility_github")
    assert pv.workflows == [
        "Agent API CI", "Objavi spletno stran", "pages build and deployment",
    ]
    assert pv.repo == "DDAY2301/PROJEKT"


def test_retired_workflow_failure_not_current_outage(tmp_path, monkeypatch):
    sup = _supervisor(tmp_path)
    monkeypatch.setattr(sup, "_github_headers", lambda: {})
    wanted = ["Agent API CI", "Objavi spletno stran", "pages build and deployment"]
    target = ManagedTarget(
        id="project_visibility_github", name="PV", kind="github_repo",
        repo="DDAY2301/PROJEKT", branch="main", workflows=wanted,
    )
    page = [_run(name, "success") for name in wanted] + [
        _run(".github/workflows/agent-api-ci.yml", "failure")
    ]
    requests = _mock_http(monkeypatch, {1: page})
    result = asyncio.run(sup._check_github(target))
    assert result["ok"] is True
    assert result["failed_workflows"] == []
    assert requests == [1]


def test_current_workflow_failure_still_detected(tmp_path, monkeypatch):
    sup = _supervisor(tmp_path)
    monkeypatch.setattr(sup, "_github_headers", lambda: {})
    target = ManagedTarget(
        id="project_visibility_github", name="PV", kind="github_repo",
        repo="DDAY2301/PROJEKT", branch="main", workflows=["Agent API CI"],
    )
    requests = _mock_http(
        monkeypatch, {1: [_run("Agent API CI", "failure")]},
    )
    result = asyncio.run(sup._check_github(target))
    assert result["ok"] is False
    assert result["failed_workflows"] == ["Agent API CI"]
    assert requests == [1]


def test_unscoped_checks_only_recent_page(tmp_path, monkeypatch):
    sup = _supervisor(tmp_path)
    monkeypatch.setattr(sup, "_github_headers", lambda: {})
    target = ManagedTarget(
        id="project_visibility_github", name="PV", kind="github_repo",
        repo="DDAY2301/PROJEKT", branch="main", workflows=None,
    )
    requests = _mock_http(
        monkeypatch, {1: [_run("Agent API CI", "success")] * 100,
                      2: [_run("Retired Workflow", "failure")]},
    )
    result = asyncio.run(sup._check_github(target))
    assert result["ok"] is True
    assert requests == [1]
