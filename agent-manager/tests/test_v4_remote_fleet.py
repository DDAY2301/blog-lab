from fastapi.testclient import TestClient


def test_fleet_remote_login_roundtrip(monkeypatch):
    monkeypatch.setenv("FLEET_REMOTE_PASSWORD", "test-password-1234567890")
    monkeypatch.setenv("FLEET_LOCAL_TOKEN", "local-token-test")
    monkeypatch.setenv("FLEET_AGENT_TOKEN", "blog-token-test")

    from manager.remote_v4 import app

    client = TestClient(app)
    response = client.post("/api/login", json={"password": "test-password-1234567890"})
    assert response.status_code == 200
    assert response.json()["ok"] is True

    root = client.get("/")
    assert root.status_code == 200
    assert "Agent Fleet Control" in root.text
    assert "Pošlji ukaz" in root.text


def test_fleet_remote_rejects_bad_password(monkeypatch):
    monkeypatch.setenv("FLEET_REMOTE_PASSWORD", "test-password-1234567890")

    from manager.remote_v4 import app

    client = TestClient(app)
    response = client.post("/api/login", json={"password": "wrong-password"})
    assert response.status_code == 401
