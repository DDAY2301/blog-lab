import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import command as command_module
from command import infer_mode


@pytest.mark.parametrize("text", [
    "Objavi članek o novem projektu",
    "objavi clanek o športu",
    "Napiši prispevek o dogodku",
    "napiši o današnjem prometu",
    "Objavi novico o dogodku",
    "pripravi članek z naslovno fotografijo",
])
def test_article_intents(text):
    assert infer_mode(text) == "article"


@pytest.mark.parametrize("text", [
    "Ustavi objavljanje",
    "zaustavi agenta",
    "izklopi objavljanje",
    "pavza",
    "nadaljuj objavljanje",
    "vklopi agenta",
    "Vrni samodejno objavljanje 3x na dan",
    "sedaj pa nazaj na termine objav kot na začetku samostojna objava trikrat na dan",
    "objavljaj trikrat na dan",
    "samostojno objavljanje po urniku",
    "nastavi termine objave",
])
def test_control_intents(text):
    assert infer_mode(text) == "control"


@pytest.mark.parametrize("text", [
    "Dodaj novo rubriko Projekti v meni",
    "dodaj in polepšaj izgled strani",
    "Objavi novo stran Projekti",
    "dodaj novo stran Partnerji",
    "spremeni header",
    "izboljšaj navigacijo",
    "dodaj footer",
    "naredi responsive layout",
    "dodaj galerijo na stran",
    "dodaj levi stolpec z aktualnimi novicami",
    "spremeni CSS kartic",
    "dodaj hero sekcijo",
    "zamenjaj logo",
    "dodaj gumb Kontakt",
])
def test_site_intents(text):
    assert infer_mode(text) == "site"


def test_site_noun_wins_over_publish_verb():
    assert infer_mode("objavi novo spletno stran za projekte") == "site"


def test_schedule_wins_over_article_wording():
    assert infer_mode("objavi članek trikrat na dan") == "control"


def test_control_command_stop_and_resume(tmp_path, monkeypatch):
    control = tmp_path / "agent-control.json"
    monkeypatch.setattr(command_module, "CONTROL", control)
    command_module.control_command("ustavi objavljanje")
    data = json.loads(control.read_text(encoding="utf-8"))
    assert data["enabled"] is False
    command_module.control_command("nadaljuj samodejno objavljanje")
    data = json.loads(control.read_text(encoding="utf-8"))
    assert data["enabled"] is True
    assert data["publish_mode"] == "automatic"


def test_control_schedule_profile(tmp_path, monkeypatch):
    control = tmp_path / "agent-control.json"
    monkeypatch.setattr(command_module, "CONTROL", control)
    command_module.control_command("vrni samostojno objavljanje trikrat na dan")
    data = json.loads(control.read_text(encoding="utf-8"))
    assert data["enabled"] is True
    assert data["publish_mode"] == "automatic"
    assert data["schedule_profile"] == "default-3x-daily"
    assert data["schedule"]["timezone"] == "Europe/Ljubljana"
    assert [slot["time"] for slot in data["schedule"]["slots"]] == ["08:17", "13:27", "19:43"]


def test_control_draft_and_review(tmp_path, monkeypatch):
    control = tmp_path / "agent-control.json"
    monkeypatch.setattr(command_module, "CONTROL", control)
    command_module.control_command("preklopi v osnutek draft")
    assert json.loads(control.read_text(encoding="utf-8"))["publish_mode"] == "draft"
    command_module.control_command("preklopi na pregled review")
    assert json.loads(control.read_text(encoding="utf-8"))["publish_mode"] == "review"


def test_builtin_design_upgrade(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    styles = src / "styles.css"
    styles.write_text("body{}\n", encoding="utf-8")
    monkeypatch.setattr(command_module, "BASE", tmp_path)
    assert command_module.builtin_site_command("dodaj in polepšaj izgled strani") is True
    once = styles.read_text(encoding="utf-8")
    assert command_module.DESIGN_MARKER in once
    assert command_module.builtin_site_command("izboljšaj design strani") is True
    twice = styles.read_text(encoding="utf-8")
    assert twice.count(command_module.DESIGN_MARKER) == 1


def test_builtin_live_pulse_detection(tmp_path, monkeypatch):
    for rel in [
        "src/LivePulse.jsx",
        "agents/live-feed/update.py",
        ".github/workflows/live-feed.yml",
        "public/live-feed.json",
    ]:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok", encoding="utf-8")
    monkeypatch.setattr(command_module, "BASE", tmp_path)
    assert command_module.builtin_site_command("dodaj levi stolpec z mini aktualnimi stvarmi na 30 minut") is True


def test_policy_denied_is_non_retryable(monkeypatch):
    monkeypatch.setattr(command_module.shutil, "which", lambda _: "/usr/bin/copilot")
    proc = SimpleNamespace(returncode=1, stdout="", stderr="Error: Access denied by policy settings")
    monkeypatch.setattr(command_module.subprocess, "run", lambda *a, **k: proc)
    with pytest.raises(SystemExit) as exc:
        command_module.site_command("dodaj nekaj popolnoma novega")
    assert exc.value.code == 78


def test_article_command_requires_real_app_change(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    app = src / "App.jsx"
    app.write_text("before", encoding="utf-8")
    monkeypatch.setattr(command_module, "BASE", tmp_path)
    monkeypatch.setattr(command_module, "ARTICLE_AGENT", tmp_path / "fake-agent.py")

    def fake_run(*args, **kwargs):
        app.write_text("after", encoding="utf-8")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(command_module.subprocess, "run", fake_run)
    command_module.article_command("objavi članek", "aktualno")


def test_article_command_rejects_noop(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "App.jsx").write_text("unchanged", encoding="utf-8")
    monkeypatch.setattr(command_module, "BASE", tmp_path)
    monkeypatch.setattr(command_module, "ARTICLE_AGENT", tmp_path / "fake-agent.py")
    monkeypatch.setattr(command_module.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    with pytest.raises(SystemExit):
        command_module.article_command("objavi članek", "aktualno")


@pytest.mark.parametrize("mode", ["article", "site", "control"])
def test_explicit_mode_overrides_auto_inference(tmp_path, monkeypatch, mode):
    payload = {"command": "Objavi članek o testu", "mode": mode, "category": "aktualno"}
    command_file = tmp_path / "command.json"
    command_file.write_text(json.dumps(payload), encoding="utf-8")
    called = []
    monkeypatch.setattr(sys, "argv", ["command.py", "--command-file", str(command_file)])
    monkeypatch.setattr(command_module, "article_command", lambda *a: called.append("article"))
    monkeypatch.setattr(command_module, "site_command", lambda *a: called.append("site"))
    monkeypatch.setattr(command_module, "control_command", lambda *a: called.append("control"))
    assert command_module.main() == 0
    assert called == [mode]
