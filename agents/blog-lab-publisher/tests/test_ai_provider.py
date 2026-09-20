import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import ai_provider


def test_review_grounding_normalizes_external_response(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.setattr(
        ai_provider,
        "_openai_compatible",
        lambda *args, **kwargs: {
            "pass": "false",
            "issues": ["Unsupported group-stage claim"],
            "unsupported_claims": ["group A"],
            "_writer_provider": "external",
        },
    )
    result = ai_provider.review_grounding(
        {"title": "Test", "content": "Claim"},
        [{"url": "https://example.com/a", "summary": "Evidence"}],
        "sport",
    )
    assert result["pass"] is False
    assert result["issues"] == ["Unsupported group-stage claim"]
    assert result["unsupported_claims"] == ["group A"]


def test_review_grounding_fails_over_from_external_to_copilot(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    calls = []

    def external(*args, **kwargs):
        calls.append("external")
        raise ai_provider.AIUnavailable("external unavailable")

    def copilot(*args, **kwargs):
        calls.append("copilot")
        return {
            "pass": True,
            "issues": [],
            "unsupported_claims": [],
            "_writer_provider": "copilot",
        }

    monkeypatch.setattr(ai_provider, "_openai_compatible", external)
    monkeypatch.setattr(ai_provider, "_copilot", copilot)

    result = ai_provider.review_grounding(
        {"title": "Test", "content": "Claim"},
        [{"url": "https://example.com/a", "summary": "Evidence"}],
        "sport",
    )

    assert result["pass"] is True
    assert calls == ["external", "copilot"]
