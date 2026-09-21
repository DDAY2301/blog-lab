import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import ai_provider


def test_review_grounding_normalizes_workers_response(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.setattr(
        ai_provider,
        "_workers_review",
        lambda *args, **kwargs: {
            "pass": "false",
            "issues": ["Unsupported group-stage claim"],
            "unsupported_claims": ["group A"],
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


def test_review_grounding_fails_over_from_workers_to_external(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.setenv("MODEL_API_KEY", "model-test")
    monkeypatch.setenv("MODEL_BASE_URL", "https://model.example/v1/chat/completions")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    calls = []

    def workers(*args, **kwargs):
        calls.append("workers")
        raise ai_provider.AIUnavailable("worker review unavailable")

    def external(*args, **kwargs):
        calls.append("external")
        return {
            "pass": True,
            "issues": [],
            "unsupported_claims": [],
            "_writer_provider": "external",
        }

    monkeypatch.setattr(ai_provider, "_workers_review", workers)
    monkeypatch.setattr(ai_provider, "_openai_compatible", external)

    result = ai_provider.review_grounding(
        {"title": "Test", "content": "Claim"},
        [{"url": "https://example.com/a", "summary": "Evidence"}],
        "sport",
    )

    assert result["pass"] is True
    assert calls == ["workers", "external"]


def test_workers_review_adapter(monkeypatch):
    monkeypatch.setenv("WORKER_AI_TOKEN", "test-token")
    monkeypatch.setenv("WORKER_AI_REVIEW_URL", "https://worker.example/api/ai/review")
    captured = {}

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self):
            return json.dumps({
                "ok": True,
                "review": {
                    "pass": True,
                    "issues": [],
                    "unsupported_claims": [],
                },
            }).encode("utf-8")

    def fake_urlopen(request, timeout=0):
        captured["url"] = request.full_url
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["authorization"] = request.headers.get("Authorization")
        return FakeResponse()

    monkeypatch.setattr(ai_provider, "urlopen", fake_urlopen)
    result = ai_provider._workers_review("system", "review this")

    assert result["pass"] is True
    assert captured["url"] == "https://worker.example/api/ai/review"
    assert captured["body"]["system_prompt"] == "system"
    assert captured["body"]["user_prompt"] == "review this"
    assert captured["authorization"] == "Bearer test-token"


def test_generate_fails_over_from_workers_to_configured_external(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.setenv("MODEL_API_KEY", "model-test")
    monkeypatch.setenv("MODEL_BASE_URL", "https://model.example/v1/chat/completions")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    calls = []

    def workers(*args, **kwargs):
        calls.append("workers")
        raise ai_provider.AIUnavailable("worker quota")

    def external(*args, **kwargs):
        calls.append("external")
        return {
            "title": "Test article",
            "content": "Grounded content",
            "sources": [{"url": "https://example.com/a"}],
            "_writer_provider": "external",
        }

    monkeypatch.setattr(ai_provider, "_workers_ai", workers)
    monkeypatch.setattr(ai_provider, "_openai_compatible", external)

    article = ai_provider.generate(
        "system",
        "task",
        [{"url": "https://example.com/a", "summary": "Evidence"}],
        "aktualno",
    )

    assert article["_writer_provider"] == "external"
    assert calls == ["workers", "external"]


def test_generate_uses_local_fallback_when_remote_providers_unavailable(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    calls = []

    def workers(*args, **kwargs):
        calls.append("workers")
        raise ai_provider.AIUnavailable("worker quota")

    def local(source_items, category):
        calls.append("local")
        return {
            "title": "Local fallback article",
            "content": "Grounded content from local evidence fallback.",
            "sources": [{"url": "https://example.com/a"}],
            "_writer_provider": "local_evidence_ai",
        }

    monkeypatch.setattr(ai_provider, "_workers_ai", workers)
    monkeypatch.setattr(
        ai_provider,
        "_openai_compatible",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("external must not run")),
    )
    monkeypatch.setattr(
        ai_provider,
        "_copilot",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("copilot must not run without a token")),
    )
    monkeypatch.setattr(ai_provider, "_local_evidence_ai", local)

    article = ai_provider.generate(
        "system",
        "task",
        [{"url": "https://example.com/a", "summary": "Evidence"}],
        "aktualno",
    )

    assert article["_writer_provider"] == "local_evidence_ai"
    assert calls == ["workers", "local"]
