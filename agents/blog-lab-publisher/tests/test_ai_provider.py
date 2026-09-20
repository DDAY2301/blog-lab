import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import ai_provider


def test_review_grounding_normalizes_worker_response(monkeypatch):
    monkeypatch.setattr(
        ai_provider,
        "_workers_ai",
        lambda *args, **kwargs: {
            "pass": "false",
            "issues": ["Unsupported group-stage claim"],
            "unsupported_claims": ["group A"],
            "_writer_provider": "workers_ai",
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
