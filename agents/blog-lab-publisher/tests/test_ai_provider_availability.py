import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "agents" / "blog-lab-publisher" / "services" / "ai_provider.py"

spec = importlib.util.spec_from_file_location("ai_provider_availability", MODULE_PATH)
ai_provider = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ai_provider
spec.loader.exec_module(ai_provider)


def test_copilot_auto_ready_with_github_token(monkeypatch):
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "github-actions-token")
    assert ai_provider._copilot_token_ready() is True


def test_copilot_auto_ready_with_dedicated_token(monkeypatch):
    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "copilot-token")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    assert ai_provider._copilot_token_ready() is True


def test_copilot_auto_not_ready_without_token(monkeypatch):
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert ai_provider._copilot_token_ready() is False
