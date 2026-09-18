import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import command as cmd


@pytest.mark.parametrize("text", [
    "Ustavi objavljanje",
    "Zaustavi agenta",
    "Pavza",
    "Izklopi objave",
    "Nadaljuj objavljanje",
    "Vklopi agenta",
    "resume",
    "Vrni urnik objav",
    "nazaj na termine objav kot na začetku",
    "samostojna objava trikrat na dan",
    "samodejno objavljanje 3x na dan",
    "avtomatska objava tri krat na dan",
])
def test_infer_control_variants(text):
    assert cmd.infer_mode(text) == "control"


@pytest.mark.parametrize("text", [
    "Objavi članek o novem projektu",
    "Napiši članek o športu",
    "napisi o dogodku",
    "Pripravi prispevek",
    "Objavi danes pregled",
])
def test_infer_article_variants(text):
    assert cmd.infer_mode(text) == "article"


@pytest.mark.parametrize("text", [
    "Dodaj novo rubriko Projekti v meni",
    "dodaj in polepšaj izgled strani",
    "Moderniziraj design strani",
    "Dodaj stran Galerija",
])
def test_infer_site_variants(text):
    assert cmd.infer_mode(text) == "site"


def test_control_stop(tmp_path, monkeypatch):
    control = tmp_path / "control.json"
    monkeypatch.setattr(cmd, "CONTROL", control)
    cmd.control_command("Ustavi objavljanje")
    data = json.loads(control.read_text())
    assert data["enabled"] is False


def test_control_resume(tmp_path, monkeypatch):
    control = tmp_path / "control.json"
    control.write_text(json.dumps({"enabled": False, "publish_mode": "draft"}))
    monkeypatch.setattr(cmd, "CONTROL", control)
    cmd.control_command("Nadaljuj samodejno objavljanje")
    data = json.loads(control.read_text())
    assert data["enabled"] is True
    assert data["publish_mode"] == "automatic"


@pytest.mark.parametrize(("command_text", "expected"), [
    ("Preklopi na draft", "draft"),
    ("Shranjuj samo osnutke", "draft"),
    ("Daj v review", "review"),
    ("Pred objavo naj gre v pregled", "review"),
    ("Vklopi automatic način", "automatic"),
    ("Naj deluje avtomatsko", "automatic"),
    ("Naj objavlja samodejno", "automatic"),
    ("Naj objavlja samostojno", "automatic"),
])
def test_control_publish_modes(tmp_path, monkeypatch, command_text, expected):
    control = tmp_path / "control.json"
    monkeypatch.setattr(cmd, "CONTROL", control)
    cmd.control_command(command_text)
    data = json.loads(control.read_text())
    assert data["publish_mode"] == expected


def test_control_schedule_profile(tmp_path, monkeypatch):
    control = tmp_path / "control.json"
    monkeypatch.setattr(cmd, "CONTROL", control)
    cmd.control_command("nazaj na termine objav kot na začetku samostojna objava trikrat na dan")
    data = json.loads(control.read_text())
    assert data["enabled"] is True
    assert data["publish_mode"] == "automatic"
    assert data["schedule_profile"] == "default-3x-daily"
    assert data["schedule"]["timezone"] == "Europe/Ljubljana"
    assert data["schedule"]["slots"] == [
        {"time": "08:17", "category": "sport"},
        {"time": "13:27", "category": "politika"},
        {"time": "19:43", "category": "aktualno"},
    ]


def test_builtin_live_pulse(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    for rel in [
        "src/LivePulse.jsx",
        "agents/live-feed/update.py",
        ".github/workflows/live-feed.yml",
        "public/live-feed.json",
    ]:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ok")
    assert cmd.builtin_site_command("Dodaj na levi stolpec mini aktualno na 30 minut") is True


def test_builtin_live_pulse_missing_files(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    assert cmd.builtin_site_command("Dodaj na levi stolpec mini aktualno na 30 minut") is False


def test_builtin_design_applies_once(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    css = tmp_path / "src/styles.css"
    css.parent.mkdir(parents=True)
    css.write_text("body { color: black; }")
    assert cmd.builtin_site_command("dodaj in polepšaj izgled strani") is True
    first = css.read_text()
    assert cmd.DESIGN_MARKER in first
    assert cmd.builtin_site_command("moderniziraj design strani") is True
    second = css.read_text()
    assert second.count(cmd.DESIGN_MARKER) == 1


def test_article_success_requires_app_change(tmp_path, monkeypatch):
    app = tmp_path / "src/App.jsx"
    app.parent.mkdir(parents=True)
    app.write_text("before")
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "ARTICLE_AGENT", tmp_path / "agent.py")

    def fake_run(*args, **kwargs):
        app.write_text("after")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cmd.subprocess, "run", fake_run)
    cmd.article_command("Objavi članek o testu", "aktualno")


def test_article_nonzero_fails(tmp_path, monkeypatch):
    app = tmp_path / "src/App.jsx"
    app.parent.mkdir(parents=True)
    app.write_text("before")
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "ARTICLE_AGENT", tmp_path / "agent.py")
    monkeypatch.setattr(cmd.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=2))
    with pytest.raises(SystemExit) as exc:
        cmd.article_command("Objavi članek", "aktualno")
    assert exc.value.code == 2


def test_article_no_change_fails(tmp_path, monkeypatch):
    app = tmp_path / "src/App.jsx"
    app.parent.mkdir(parents=True)
    app.write_text("same")
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "ARTICLE_AGENT", tmp_path / "agent.py")
    monkeypatch.setattr(cmd.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    with pytest.raises(SystemExit, match="without publishing"):
        cmd.article_command("Objavi članek", "aktualno")


def test_site_builtin_does_not_need_copilot(monkeypatch):
    monkeypatch.setattr(cmd, "builtin_site_command", lambda command: True)
    monkeypatch.setattr(cmd.shutil, "which", lambda name: None)
    cmd.site_command("polepšaj stran")


def test_site_missing_copilot_fails(monkeypatch):
    monkeypatch.setattr(cmd, "builtin_site_command", lambda command: False)
    monkeypatch.setattr(cmd.shutil, "which", lambda name: None)
    with pytest.raises(SystemExit, match="not installed"):
        cmd.site_command("Dodaj posebno novo komponento")


def test_site_copilot_success(monkeypatch, tmp_path):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "builtin_site_command", lambda command: False)
    monkeypatch.setattr(cmd.shutil, "which", lambda name: "/usr/bin/copilot")
    monkeypatch.setattr(cmd.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout="", stderr=""))
    cmd.site_command("Dodaj posebno novo komponento")


def test_site_policy_denied_is_permanent(monkeypatch, tmp_path):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "builtin_site_command", lambda command: False)
    monkeypatch.setattr(cmd.shutil, "which", lambda name: "/usr/bin/copilot")
    denied = "Error: Access denied by policy settings"
    monkeypatch.setattr(cmd.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr=denied))
    with pytest.raises(SystemExit) as exc:
        cmd.site_command("Dodaj posebno novo komponento")
    assert exc.value.code == 78


def test_site_other_copilot_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "builtin_site_command", lambda command: False)
    monkeypatch.setattr(cmd.shutil, "which", lambda name: "/usr/bin/copilot")
    monkeypatch.setattr(cmd.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=2, stdout="", stderr="network timeout"))
    with pytest.raises(SystemExit) as exc:
        cmd.site_command("Dodaj posebno novo komponento")
    assert "exit code 2" in str(exc.value)


def _run_main(tmp_path, monkeypatch, payload, expected_call):
    path = tmp_path / "command.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    calls = []
    monkeypatch.setattr(cmd, "control_command", lambda command: calls.append(("control", command)))
    monkeypatch.setattr(cmd, "article_command", lambda command, category: calls.append(("article", command, category)))
    monkeypatch.setattr(cmd, "site_command", lambda command: calls.append(("site", command)))
    monkeypatch.setattr(sys, "argv", ["command.py", "--command-file", str(path)])
    assert cmd.main() == 0
    assert calls == [expected_call]


def test_main_auto_control(tmp_path, monkeypatch):
    _run_main(tmp_path, monkeypatch, {"command": "ustavi objavljanje", "mode": "auto", "category": "aktualno"}, ("control", "ustavi objavljanje"))


def test_main_auto_article(tmp_path, monkeypatch):
    _run_main(tmp_path, monkeypatch, {"command": "objavi članek o testu", "mode": "auto", "category": "sport"}, ("article", "objavi članek o testu", "sport"))


def test_main_auto_site(tmp_path, monkeypatch):
    _run_main(tmp_path, monkeypatch, {"command": "dodaj stran projekti", "mode": "auto", "category": "aktualno"}, ("site", "dodaj stran projekti"))


def test_main_explicit_modes(tmp_path, monkeypatch):
    _run_main(tmp_path, monkeypatch, {"command": "karkoli", "mode": "control", "category": "politika"}, ("control", "karkoli"))
    _run_main(tmp_path, monkeypatch, {"command": "karkoli", "mode": "article", "category": "politika"}, ("article", "karkoli", "politika"))
    _run_main(tmp_path, monkeypatch, {"command": "karkoli", "mode": "site", "category": "politika"}, ("site", "karkoli"))


def test_main_invalid_mode_falls_back_to_auto(tmp_path, monkeypatch):
    _run_main(tmp_path, monkeypatch, {"command": "objavi članek", "mode": "nonsense", "category": "sport"}, ("article", "objavi članek", "sport"))


def test_main_invalid_category_falls_back_to_aktualno(tmp_path, monkeypatch):
    _run_main(tmp_path, monkeypatch, {"command": "objavi članek", "mode": "article", "category": "banana"}, ("article", "objavi članek", "aktualno"))


@pytest.mark.parametrize("command", ["", "   ", "x" * 4001])
def test_main_rejects_invalid_command(tmp_path, monkeypatch, command):
    path = tmp_path / "command.json"
    path.write_text(json.dumps({"command": command, "mode": "auto", "category": "aktualno"}), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["command.py", "--command-file", str(path)])
    with pytest.raises(SystemExit, match="invalid command"):
        cmd.main()


@pytest.mark.parametrize(("text", "expected"), [
    ("objavi novo stran Projekti", "site"),
    ("objavi novo rubriko Dogodki", "site"),
    ("objavi članek in polepšaj izgled", "article"),
    ("dodaj video v članek", "site"),
    ("spremeni header", "site"),
    ("preveri status agenta", "control"),
    ("ali agent deluje", "control"),
])
def test_ambiguous_routing(text, expected):
    assert cmd.infer_mode(text) == expected


def test_control_status_is_non_mutating(tmp_path, monkeypatch, capsys):
    control = tmp_path / "control.json"
    original = {
        "enabled": True,
        "publish_mode": "automatic",
        "schedule": {
            "timezone": "Europe/Ljubljana",
            "slots": [
                {"time": "08:17", "category": "sport"},
                {"time": "13:27", "category": "politika"},
                {"time": "19:43", "category": "aktualno"},
            ],
        },
    }
    control.write_text(json.dumps(original), encoding="utf-8")
    monkeypatch.setattr(cmd, "CONTROL", control)
    cmd.control_command("preveri status agenta")
    assert json.loads(control.read_text()) == original
    assert "CONTROL_STATUS" in capsys.readouterr().out


@pytest.mark.parametrize("text", [
    "Spremeni urnik objav ob 09:00, 14:00 in 20:00",
    "Termini objav naj bodo 9:30 14:30 20:30",
])
def test_custom_schedule_is_rejected(tmp_path, monkeypatch, text):
    control = tmp_path / "control.json"
    monkeypatch.setattr(cmd, "CONTROL", control)
    with pytest.raises(SystemExit) as exc:
        cmd.control_command(text)
    assert exc.value.code == 64


def test_default_explicit_schedule_is_accepted(tmp_path, monkeypatch):
    control = tmp_path / "control.json"
    monkeypatch.setattr(cmd, "CONTROL", control)
    cmd.control_command("Urnik naj bo 08:17 13:27 19:43")
    data = json.loads(control.read_text())
    assert data["schedule_profile"] == "default-3x-daily"


def test_add_rubric(tmp_path, monkeypatch):
    rubrics = tmp_path / "site-rubrics.json"
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    assert cmd.manage_rubric("Dodaj novo rubriko Projekti v meni") is True
    data = json.loads(rubrics.read_text())
    assert data == [{"name": "Projekti", "slug": "projekti"}]


def test_add_rubric_is_idempotent(tmp_path, monkeypatch):
    rubrics = tmp_path / "site-rubrics.json"
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    cmd.manage_rubric("Dodaj novo rubriko Projekti v meni")
    cmd.manage_rubric("Dodaj rubriko Projekti")
    data = json.loads(rubrics.read_text())
    assert len(data) == 1


def test_remove_rubric(tmp_path, monkeypatch):
    rubrics = tmp_path / "site-rubrics.json"
    rubrics.write_text(json.dumps([{"name": "Projekti", "slug": "projekti"}]), encoding="utf-8")
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    assert cmd.manage_rubric("Odstrani rubriko Projekti") is True
    assert json.loads(rubrics.read_text()) == []


def test_remove_missing_rubric_is_safe(tmp_path, monkeypatch):
    rubrics = tmp_path / "site-rubrics.json"
    rubrics.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    assert cmd.manage_rubric("Odstrani rubriko Neobstojeca") is True
    assert json.loads(rubrics.read_text()) == []


def test_invalid_long_rubric_name_is_rejected(tmp_path, monkeypatch):
    rubrics = tmp_path / "site-rubrics.json"
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    with pytest.raises(SystemExit):
        cmd.manage_rubric("Dodaj rubriko " + "A" * 41)


def test_article_in_named_rubric_passes_output_category(tmp_path, monkeypatch):
    app = tmp_path / "src/App.jsx"
    app.parent.mkdir(parents=True)
    app.write_text("before")
    rubrics = tmp_path / "site-rubrics.json"
    rubrics.write_text(json.dumps([{"name": "Projekti", "slug": "projekti"}]), encoding="utf-8")
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    monkeypatch.setattr(cmd, "ARTICLE_AGENT", tmp_path / "agent.py")
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        app.write_text("after")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cmd.subprocess, "run", fake_run)
    cmd.article_command("Objavi članek o Erasmus projektu v rubriki Projekti", "aktualno")
    assert "--output-category" in captured["args"]
    idx = captured["args"].index("--output-category")
    assert captured["args"][idx + 1] == "Projekti"


def test_article_unknown_rubric_does_not_invent_category(tmp_path, monkeypatch):
    app = tmp_path / "src/App.jsx"
    app.parent.mkdir(parents=True)
    app.write_text("before")
    rubrics = tmp_path / "site-rubrics.json"
    rubrics.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    monkeypatch.setattr(cmd, "ARTICLE_AGENT", tmp_path / "agent.py")
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        app.write_text("after")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cmd.subprocess, "run", fake_run)
    cmd.article_command("Objavi članek o testu v rubriki Neobstojeca", "aktualno")
    assert "--output-category" not in captured["args"]


@pytest.mark.parametrize("text", [
    "skrij tekoče",
    "odstrani mini novice",
    "izklopi live pulse",
    "pokaži tekoče",
    "prikaži mini novice",
    "vklopi live pulse",
])
def test_live_pulse_settings_route_to_site(text):
    assert cmd.infer_mode(text) == "site"


def test_site_settings_brand(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)
    assert cmd.manage_site_settings("Spremeni ime strani v Novi Blog") is True
    data = json.loads(settings.read_text())
    assert data["brand"] == "Novi Blog"
    assert data["showLivePulse"] is True


def test_site_settings_hero_title(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)
    assert cmd.manage_site_settings("Spremeni glavni naslov v Aktualne zgodbe") is True
    assert json.loads(settings.read_text())["heroTitle"] == "Aktualne zgodbe"


def test_site_settings_subtitle(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)
    assert cmd.manage_site_settings("Nastavi podnaslov na Dnevni pregled aktualnih dogodkov") is True
    assert json.loads(settings.read_text())["heroSubtitle"] == "Dnevni pregled aktualnih dogodkov"


def test_site_settings_footer(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)
    assert cmd.manage_site_settings("Spremeni footer v Neodvisen prostor za zgodbe") is True
    assert json.loads(settings.read_text())["footerText"] == "Neodvisen prostor za zgodbe"


def test_site_settings_hide_show_live_pulse(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)
    assert cmd.manage_site_settings("Skrij tekoče") is True
    assert json.loads(settings.read_text())["showLivePulse"] is False
    assert cmd.manage_site_settings("Pokaži tekoče") is True
    assert json.loads(settings.read_text())["showLivePulse"] is True


def test_site_settings_unrelated_command_returns_false(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)
    assert cmd.manage_site_settings("Dodaj povsem novo kompleksno komponento") is False
    assert not settings.exists()


def test_site_settings_rejects_empty_or_overlong_value(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)
    with pytest.raises(SystemExit):
        cmd.manage_site_settings("Spremeni ime strani v " + "A" * 61)


def test_site_settings_preimenuj_blog_lab(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)
    assert cmd.manage_site_settings("Preimenuj Blog Lab v Dnevni Lab") is True
    assert json.loads(settings.read_text())["brand"] == "Dnevni Lab"


def test_site_settings_emphasis_eyebrow_cta_and_reset(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)

    assert cmd.manage_site_settings("Spremeni poudarjeni naslov v Vsak dan sveže") is True
    assert json.loads(settings.read_text())["heroEmphasis"] == "Vsak dan sveže"

    assert cmd.manage_site_settings("Spremeni oznako nad naslovom v AKTUALNO") is True
    assert json.loads(settings.read_text())["heroEyebrow"] == "AKTUALNO"

    assert cmd.manage_site_settings("Spremeni gumb na naslovnici v Preberi novice") is True
    assert json.loads(settings.read_text())["heroCta"] == "Preberi novice"

    assert cmd.manage_site_settings("Ponastavi besedila strani") is True
    data = json.loads(settings.read_text())
    assert data["brand"] == "Blog Lab"
    assert data["heroEmphasis"] == "Objavljamo preprosto."
    assert data["showLivePulse"] is True
