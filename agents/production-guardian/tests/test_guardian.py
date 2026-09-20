from __future__ import annotations

import json

from agents.production_guardian_import import load_guardian


def test_redact_removes_token_like_values():
    guardian = load_guardian()
    text = guardian.redact("Bearer abcdefghijklmnopqrstuvwxyz1234567890 and ghp_abcdefghijklmnopqrstuvwxyz123456")
    assert "Bearer [REDACTED]" in text
    assert "ghp_" not in text


def test_desired_package_json_adds_guardian_scripts():
    guardian = load_guardian()
    content, changed = guardian.desired_package_json({"scripts": {"build": "vite build"}})
    assert changed is True
    data = json.loads(content)
    assert data["scripts"]["guardian:check"].startswith("python agents/production-guardian/guardian.py")
    assert data["scripts"]["test:guardian"] == "python -m pytest -q agents/production-guardian/tests"


def test_manifest_contains_safe_autoupdate_mode():
    guardian = load_guardian()
    data = json.loads(guardian.manifest_json())
    assert data["mode"] == "safe-autoupdate"
    assert "validated pull-request based auto-update" in data["capabilities"]


def test_report_builds_without_remote_calls(monkeypatch):
    guardian = load_guardian()
    monkeypatch.setenv("GUARDIAN_SKIP_REMOTE", "1")
    report = guardian.build_report(skip_remote=True)
    assert report["name"] == "Blog Lab Production Guardian"
    assert report["counts"]["skip"] >= 1
    assert any(item["id"] == "required-files" for item in report["findings"])
