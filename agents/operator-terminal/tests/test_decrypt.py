import base64
import json
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import decrypt as decrypt_module


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def test_decrypt_reads_payload_from_github_event(tmp_path, monkeypatch):
    key = bytes(range(1, 33))
    iv = bytes(range(12))
    original = {
        "request_id": "11111111-2222-3333-4444-555555555555",
        "command": "Ustavi objavljanje",
        "mode": "control",
        "category": "aktualno",
        "actor": "operator@example.test",
        "created_at": "2026-09-18T15:00:00.000Z",
    }
    plaintext = json.dumps(original).encode("utf-8")
    encrypted = AESGCM(key).encrypt(iv, plaintext, None)
    payload = _b64url(iv + encrypted)

    event = tmp_path / "event.json"
    event.write_text(json.dumps({"inputs": {"payload": payload}}), encoding="utf-8")
    output = tmp_path / "command.json"

    monkeypatch.delenv("TERMINAL_PAYLOAD", raising=False)
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("TERMINAL_COMMAND_KEY", base64.b64encode(key).decode("ascii"))
    monkeypatch.setattr(sys, "argv", ["decrypt.py", str(output)])

    assert decrypt_module.main() == 0
    assert json.loads(output.read_text(encoding="utf-8")) == original
