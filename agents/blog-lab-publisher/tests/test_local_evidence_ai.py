import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SERVICE_DIR = ROOT / "agents" / "blog-lab-publisher"
sys.path.insert(0, str(SERVICE_DIR))
MODULE_PATH = SERVICE_DIR / "services" / "ai_provider.py"

spec = importlib.util.spec_from_file_location("ai_provider_local", MODULE_PATH)
ai_provider = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ai_provider
spec.loader.exec_module(ai_provider)


def _items():
    return [
        {
            "title": "Preizkusna aktualna zgodba iz Slovenije",
            "summary": "Prvi vir poroča o preverljivi zgodbi z več javno navedenimi podatki. Zapis ostaja omejen na to, kar je v viru navedeno.",
            "source_name": "Testni vir",
            "published": "Sun, 20 Sep 2026 18:00:00 GMT",
            "url": "https://example.com/novica-1",
        },
        {
            "title": "Drugi vir dodaja kontekst",
            "summary": "Drugi vir dodaja kontekst o isti temi in ne uvaja nepovezanih trditev.",
            "source_name": "Drugi vir",
            "published": "Sun, 20 Sep 2026 18:05:00 GMT",
            "url": "https://example.com/novica-2",
        },
    ]


def test_generate_falls_back_to_local_evidence_ai(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.delenv("WORKER_AI_TOKEN", raising=False)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    article = ai_provider.generate("system", "task", _items(), "aktualno")
    assert article["_writer_provider"] == "local_evidence_ai"
    assert article["title"]
    assert article["content"]


def test_review_grounding_local_pass_when_external_unavailable(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.delenv("WORKER_AI_TOKEN", raising=False)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    review = ai_provider.review_grounding({"title": "x", "content": "y"}, _items(), "aktualno")
    assert review["pass"] is True
