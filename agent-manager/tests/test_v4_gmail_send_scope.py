from __future__ import annotations

import base64
from email import message_from_bytes

from manager.gmail_v4 import GmailV4


def test_send_uses_configured_sender_without_profile_scope(monkeypatch, tmp_path):
    monkeypatch.setenv("GMAIL_REPORTING_ENABLED", "1")
    monkeypatch.setenv("REPORT_TO_EMAIL", "dan.grmusa@gmail.com")
    monkeypatch.setenv("GMAIL_FROM_EMAIL", "dan.grmusa@gmail.com")
    monkeypatch.setenv("GMAIL_OAUTH_CLIENT_FILE", str(tmp_path / "client.json"))
    monkeypatch.setenv("GMAIL_OAUTH_TOKEN_FILE", str(tmp_path / "token.json"))

    gmail = GmailV4()
    monkeypatch.setattr(gmail, "_credentials", lambda: object())

    captured = {}

    class Execute:
        def execute(self):
            return {"id": "msg-123"}

    class Messages:
        def send(self, userId, body):
            captured["userId"] = userId
            captured["raw"] = body["raw"]
            return Execute()

    class Users:
        # Intentionally no getProfile method: gmail.send scope should be enough.
        def messages(self):
            return Messages()

    class Service:
        def users(self):
            return Users()

    import googleapiclient.discovery

    monkeypatch.setattr(
        googleapiclient.discovery,
        "build",
        lambda *args, **kwargs: Service(),
    )

    message_id = gmail.send("scope test", "hello")
    assert message_id == "msg-123"
    assert captured["userId"] == "me"

    raw = base64.urlsafe_b64decode(captured["raw"].encode("ascii"))
    msg = message_from_bytes(raw)
    assert msg["From"] == "dan.grmusa@gmail.com"
    assert msg["To"] == "dan.grmusa@gmail.com"
    assert msg["Subject"] == "scope test"
