import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import ai_provider


def test_review_grounding_normalizes_external_response(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("MODEL_API_KEY", "model-test")
    monkeypatch.setenv("MODEL_BASE_URL", "https://model.example/v1/chat/completions")
    monkeypatch.setenv("MODEL_NAME", "test-model")
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
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("MODEL_API_KEY", "model-test")
    monkeypatch.setenv("MODEL_BASE_URL", "https://model.example/v1/chat/completions")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "copilot-test")
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


def test_generate_fails_over_from_workers_to_github_models(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.setenv("GITHUB_TOKEN", "actions-token")
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    calls = []

    def workers(*args, **kwargs):
        calls.append("workers")
        raise ai_provider.AIUnavailable("worker quota")

    def github_models(*args, **kwargs):
        calls.append("github_models")
        return {
            "title": "Test article",
            "content": "Grounded content",
            "sources": [{"url": "https://example.com/a"}],
            "_writer_provider": "github_models",
        }

    monkeypatch.setattr(ai_provider, "_workers_ai", workers)
    monkeypatch.setattr(ai_provider, "_github_models", github_models)

    article = ai_provider.generate(
        "system",
        "task",
        [{"url": "https://example.com/a", "summary": "Evidence"}],
        "aktualno",
    )

    assert article["_writer_provider"] == "github_models"
    assert calls == ["workers", "github_models"]


def test_github_models_writer_adapter(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "actions-token")
    monkeypatch.setenv("GITHUB_MODELS_MODEL", "openai/gpt-4.1")
    captured = {}

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self):
            return json.dumps({
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "title": "Verified story",
                            "content": "Evidence-based content",
                            "sources": [{"url": "https://example.com/source"}],
                        })
                    }
                }]
            }).encode("utf-8")

    def fake_urlopen(request, timeout=0):
        captured["url"] = request.full_url
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["authorization"] = request.headers.get("Authorization")
        return FakeResponse()

    monkeypatch.setattr(ai_provider, "urlopen", fake_urlopen)
    article = ai_provider._github_models("system", "user")

    assert article["_writer_provider"] == "github_models"
    assert captured["url"] == "https://models.github.ai/inference/chat/completions"
    assert captured["body"]["model"] == "openai/gpt-4.1"
    assert captured["authorization"] == "Bearer actions-token"


def test_review_grounding_prefers_github_models_in_auto(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.setenv("GITHUB_TOKEN", "actions-token")
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)

    monkeypatch.setattr(
        ai_provider,
        "_github_models",
        lambda *args, **kwargs: {
            "pass": True,
            "issues": [],
            "unsupported_claims": [],
            "_writer_provider": "github_models",
        },
    )

    result = ai_provider.review_grounding(
        {"title": "Test", "content": "Claim"},
        [{"url": "https://example.com/a", "summary": "Evidence"}],
        "sport",
    )
    assert result["pass"] is True
