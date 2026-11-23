import asyncio
from types import SimpleNamespace

from fastapi.testclient import TestClient

from manager import remote_v4
from manager.db_v3 import StoreV3
from manager.job_control_v8 import JobControlV8


def test_fleet_review_requires_session_and_explicit_same_origin(tmp_path, monkeypatch):
    monkeypatch.setenv("FLEET_REMOTE_PASSWORD", "unit-test-password-1234567890")
    store = StoreV3(tmp_path / "fleet-review.sqlite")
    monkeypatch.setattr(remote_v4, "store", store)
    controls = JobControlV8(store)
    rid = controls.request_review(
        "11111111-1111-1111-1111-111111111111",
        "s1", "bloglab", "publish website", "owner@example.com",
    )
    client = TestClient(remote_v4.app)
    assert client.get("/api/reviews").status_code == 401
    assert client.post(f"/api/reviews/{rid}/approve").status_code == 401
    login = client.post("/api/login", json={"password": "unit-test-password-1234567890"})
    assert login.status_code == 200
    assert len(client.get("/api/reviews").json()["reviews"]) == 1
    assert client.post(f"/api/reviews/{rid}/approve", headers={
        "origin": "https://other.invalid",
        "x-agent-review-intent": rid,
    }).status_code == 403
    assert client.post(f"/api/reviews/{rid}/approve", headers={
        "origin": "http://testserver",
    }).status_code == 403
    allowed = client.post(f"/api/reviews/{rid}/approve", headers={
        "origin": "http://testserver",
        "x-agent-review-intent": rid,
    })
    assert allowed.status_code == 200
    assert allowed.json()["executed"] is False
    assert allowed.json()["status"] == "approved"
    assert client.post(f"/api/reviews/{rid}/approve", headers={
        "origin": "http://testserver",
        "x-agent-review-intent": rid,
    }).status_code == 409


def test_github_status_and_rollback_plan_never_modify_repository(monkeypatch):
    calls = []

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def get(self, url, headers=None, params=None):
            calls.append(url)
            if url.endswith("/commits"):
                return SimpleNamespace(
                    status_code=200,
                    json=lambda: [{"sha": "a" * 40,
                                   "commit": {"message": "Last known revision"},
                                   "html_url": "https://github.com/example/commit"}],
                )
            return SimpleNamespace(
                status_code=200,
                json=lambda: {"workflow_runs": [
                    {"name": "CI", "status": "completed",
                     "conclusion": "success",
                     "html_url": "https://github.com/example/actions"}]},
            )
    monkeypatch.setattr(remote_v4.httpx, "AsyncClient", FakeClient)
    status = asyncio.run(remote_v4._manager_command("GITHUB STATUS"))
    assert status["result"]["mode"] == "read_only"
    assert len(status["result"]["repos"]) == 2
    preview = asyncio.run(remote_v4._manager_command("ROLLBACK PLAN PV"))
    assert preview["result"]["mode"] == "plan_only"
    assert "No rollback was performed" in preview["result"]["note"]
    assert calls
    assert all("/commits" in url or "/actions/runs" in url for url in calls)
