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
    "Naredi članke daljše in bolj profesionalne",
    "Izboljšaj pisanje člankov",
    "Spremeni izgled člankov in tipografijo",
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


def test_article_no_sources_becomes_permanent_terminal_error(tmp_path, monkeypatch, capsys):
    app = tmp_path / "src/App.jsx"
    app.parent.mkdir(parents=True)
    app.write_text("before")
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "ARTICLE_AGENT", tmp_path / "agent.py")
    monkeypatch.setattr(cmd.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=3))
    with pytest.raises(SystemExit) as exc:
        cmd.article_command("Objavi članek o zelo ozki temi", "aktualno")
    assert exc.value.code == 64
    assert "ARTICLE_SOURCE_UNAVAILABLE" in capsys.readouterr().err


def test_article_no_change_fails(tmp_path, monkeypatch):
    app = tmp_path / "src/App.jsx"
    app.parent.mkdir(parents=True)
    app.write_text("same")
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "ARTICLE_AGENT", tmp_path / "agent.py")
    monkeypatch.setattr(cmd.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    with pytest.raises(SystemExit, match="without publishing"):
        cmd.article_command("Objavi članek", "aktualno")


def test_site_builtin_does_not_need_workers_ai(monkeypatch):
    monkeypatch.setattr(cmd, "builtin_site_command", lambda command: True)
    called = []
    monkeypatch.setattr(cmd, "workers_ai_site_command", lambda command: called.append(command))
    cmd.site_command("polepšaj stran")
    assert called == []


def test_site_workers_ai_success(monkeypatch):
    monkeypatch.setattr(cmd, "builtin_site_command", lambda command: False)
    called = []
    monkeypatch.setattr(cmd, "workers_ai_site_command", lambda command: called.append(command))
    cmd.site_command("Dodaj posebno novo komponento")
    assert called == ["Dodaj posebno novo komponento"]


def test_site_workers_ai_failure_is_clear_without_copilot(monkeypatch):
    monkeypatch.setattr(cmd, "builtin_site_command", lambda command: False)
    monkeypatch.setattr(
        cmd,
        "workers_ai_site_command",
        lambda command: (_ for _ in ()).throw(cmd.SiteEditError("planner unavailable")),
    )
    monkeypatch.delenv("COPILOT_PERSONAL_TOKEN_CONFIGURED", raising=False)
    with pytest.raises(SystemExit) as exc:
        cmd.site_command("Dodaj posebno novo komponento")
    assert "AI site edit failed" in str(exc.value)
    assert "planner unavailable" in str(exc.value)


def test_apply_site_plan_exact_replace(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "src/example.jsx"
    path.parent.mkdir(parents=True)
    path.write_text("const title = 'Old';\n", encoding="utf-8")
    changed = cmd._apply_site_plan({
        "summary": "update title",
        "edits": [{
            "path": "src/example.jsx",
            "action": "replace",
            "old": "const title = 'Old';",
            "new": "const title = 'New';",
        }],
    })
    assert changed == 1
    assert "New" in path.read_text(encoding="utf-8")


def test_apply_site_plan_rejects_non_unique_replace(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "src/example.jsx"
    path.parent.mkdir(parents=True)
    path.write_text("same\nsame\n", encoding="utf-8")
    with pytest.raises(cmd.SiteEditError, match="unikaten"):
        cmd._apply_site_plan({
            "edits": [{
                "path": "src/example.jsx",
                "action": "replace",
                "old": "same",
                "new": "new",
            }],
        })


def test_apply_site_plan_rejects_protected_path(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    with pytest.raises(cmd.SiteEditError):
        cmd._apply_site_plan({
            "edits": [{
                "path": ".github/workflows/evil.yml",
                "action": "create",
                "new": "name: nope",
            }],
        })


def test_site_context_truncates_huge_app(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "App.jsx").write_text("HEADER\n" + ("x" * 100000) + "\nFOOTER", encoding="utf-8")
    (src / "styles.css").write_text("body{}", encoding="utf-8")
    context = cmd._site_context("spremeni footer")
    app = next(item for item in context if item["path"] == "src/App.jsx")
    total = sum(len(part["content"]) for part in app["snippets"])
    assert total <= 17000
    assert app["complete"] is False


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
    ("objavi članek in polepšaj izgled", "site"),
    ("naredi članke daljše in besedilo bolj profesionalno", "site"),
    ("napiši daljši članek o gospodarstvu", "article"),
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
    assert "--manual" in captured["args"]
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


@pytest.mark.parametrize("text", [
    "Objavljaj enkrat na dan",
    "Objavljaj dvakrat na dan",
    "Objavljaj 4x na dan",
    "Objavljaj štirikrat na dan",
    "Objavljaj vsako uro",
])
def test_unsupported_daily_counts_are_control(text):
    assert cmd.infer_mode(text) == "control"


@pytest.mark.parametrize("text", [
    "Objavljaj enkrat na dan",
    "Objavljaj dvakrat na dan",
    "Objavljaj 4x na dan",
    "Objavljaj štirikrat na dan",
    "Objavljaj vsako uro",
])
def test_unsupported_daily_counts_are_rejected(tmp_path, monkeypatch, text):
    control = tmp_path / "control.json"
    monkeypatch.setattr(cmd, "CONTROL", control)
    with pytest.raises(SystemExit) as exc:
        cmd.control_command(text)
    assert exc.value.code == 64


@pytest.mark.parametrize("text", [
    "Objavi novo stran Projekti",
    "Naredi novo stran Projekti",
    "Kreiraj novo stran Projekti",
    "Objavi novo rubriko Projekti",
])
def test_natural_add_page_verbs_are_builtin(tmp_path, monkeypatch, text):
    rubrics = tmp_path / "site-rubrics.json"
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    assert cmd.manage_rubric(text) is True
    data = json.loads(rubrics.read_text())
    assert data[0]["name"] == "Projekti"


@pytest.mark.parametrize("text", [
    "Naredi stran lepšo",
    "Naredi stran lepso",
    "Daj profesionalen izgled",
    "Naredi premium izgled",
])
def test_more_design_phrases_are_builtin(tmp_path, monkeypatch, text):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    css = tmp_path / "src/styles.css"
    css.parent.mkdir(parents=True)
    css.write_text("body{}")
    assert cmd.builtin_site_command(text) is True
    assert cmd.DESIGN_MARKER in css.read_text()


@pytest.mark.parametrize("text", [
    "Naj objavlja samodejno",
    "Agent naj deluje avtomatsko",
    "Preklopi v automatic mode",
    "Naj dela samostojno objavljanje",
])
def test_publish_mode_phrases_route_to_control(text):
    assert cmd.infer_mode(text) == "control"


@pytest.mark.parametrize("text", [
    "status",
    "preveri status",
    "preveri status agenta",
])
def test_generic_status_phrases_route_to_control(text):
    assert cmd.infer_mode(text) == "control"


def test_rubric_limit_is_explicit(tmp_path, monkeypatch):
    rubrics = tmp_path / "site-rubrics.json"
    rubrics.write_text(json.dumps([
        {"name": f"Rubrika {i}", "slug": f"rubrika-{i}"} for i in range(12)
    ]), encoding="utf-8")
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    with pytest.raises(SystemExit) as exc:
        cmd.manage_rubric("Dodaj rubriko Trinajsta")
    assert exc.value.code == 64
    assert len(json.loads(rubrics.read_text())) == 12


def test_corrupt_control_json_recovers(tmp_path, monkeypatch):
    control = tmp_path / "control.json"
    control.write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(cmd, "CONTROL", control)
    cmd.control_command("Nadaljuj samodejno objavljanje")
    data = json.loads(control.read_text())
    assert data["enabled"] is True
    assert data["publish_mode"] == "automatic"


def test_corrupt_rubrics_json_recovers(tmp_path, monkeypatch):
    rubrics = tmp_path / "site-rubrics.json"
    rubrics.write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(cmd, "RUBRICS", rubrics)
    assert cmd.manage_rubric("Dodaj rubriko Projekti") is True
    assert json.loads(rubrics.read_text()) == [{"name": "Projekti", "slug": "projekti"}]


def test_corrupt_site_settings_json_recovers(tmp_path, monkeypatch):
    settings = tmp_path / "site-settings.json"
    settings.write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(cmd, "SITE_SETTINGS", settings)
    assert cmd.manage_site_settings("Spremeni ime strani v Test Lab") is True
    data = json.loads(settings.read_text())
    assert data["brand"] == "Test Lab"
    assert data["showLivePulse"] is True


def test_safe_agent_log_redacts_token_like_values():
    pat = "github" + "_pat_" + "ABCDEF1234567890_" + "ABCDEFGHIJKLMN"
    ghp = "gh" + "p_" + "123456789012345678901234567890"
    raw = "before " + pat + " after " + ghp
    safe = cmd._safe_agent_log(raw)
    assert "github" + "_pat_" not in safe
    assert "gh" + "p_" not in safe
    assert "[REDACTED]" in safe


def test_main_accepts_exactly_4000_chars(tmp_path, monkeypatch):
    path = tmp_path / "command.json"
    command = "x" * 4000
    path.write_text(json.dumps({"command": command, "mode": "site", "category": "aktualno"}), encoding="utf-8")
    calls = []
    monkeypatch.setattr(cmd, "site_command", lambda value: calls.append(value))
    monkeypatch.setattr(sys, "argv", ["command.py", "--command-file", str(path)])
    assert cmd.main() == 0
    assert calls == [command]


def test_pastel_blue_theme_command(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    css = tmp_path / "src/styles.css"
    css.parent.mkdir(parents=True)
    css.write_text(":root { --green: #176b45; }", encoding="utf-8")
    text = "spremeni celotno stran v drugačen barvni spekter pastel modra recimo"
    assert cmd.infer_mode(text) == "site"
    assert cmd.builtin_site_command(text) is True
    value = css.read_text(encoding="utf-8")
    assert cmd.THEME_START in value
    assert "#7fa9d1" in value
    assert "theme=pastel-blue" not in value


def test_theme_replaces_previous_theme(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    css = tmp_path / "src/styles.css"
    css.parent.mkdir(parents=True)
    css.write_text("body{}", encoding="utf-8")
    assert cmd.apply_theme("pastel-blue") is True
    assert cmd.apply_theme("pink") is True
    value = css.read_text(encoding="utf-8")
    assert value.count(cmd.THEME_START) == 1
    assert "#c887a4" in value
    assert "#7fa9d1" not in value


@pytest.mark.parametrize(("text", "theme"), [
    ("spremeni barve strani v modro", "blue"),
    ("nastavi barvno temo zeleno", "green"),
    ("spremeni paleto v roza", "pink"),
    ("tema strani naj bo pastel vijolična", "lilac"),
    ("nastavi barve strani v bež", "beige"),
    ("spremeni temo strani v temno", "dark"),
])
def test_theme_variants(tmp_path, monkeypatch, text, theme):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    css = tmp_path / "src/styles.css"
    css.parent.mkdir(parents=True)
    css.write_text("body{}", encoding="utf-8")
    assert cmd.builtin_site_command(text) is True
    value = css.read_text(encoding="utf-8")
    assert cmd.THEME_START in value
    assert cmd._requested_theme(text.lower()) == theme


def test_unknown_theme_falls_through_to_ai_site_planner(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    css = tmp_path / "src/styles.css"
    css.parent.mkdir(parents=True)
    css.write_text("body{}", encoding="utf-8")
    assert cmd.builtin_site_command("spremeni barvno temo v koralno") is False


def test_site_quality_guard_rejects_duplicate_article_selector(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    styles = tmp_path / "src/styles.css"
    styles.parent.mkdir(parents=True)
    styles.write_text(
        "/* Blog Lab professional article reading system v3 */\n"
        ".article-page { width: min(100%, 1080px); }\n"
        ".article-body { max-width: 740px; }\n",
        encoding="utf-8",
    )
    with pytest.raises(cmd.SiteEditError, match="CSS quality guard"):
        cmd._apply_site_plan({
            "summary": "bad override",
            "edits": [{
                "path": "src/styles.css",
                "action": "append",
                "new": ".article-page { max-width: 800px; }",
            }],
        })


def test_site_quality_guard_allows_editing_existing_article_rule(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    styles = tmp_path / "src/styles.css"
    styles.parent.mkdir(parents=True)
    styles.write_text(
        "/* Blog Lab professional article reading system v3 */\n"
        ".article-page { width: min(100%, 1080px); }\n"
        ".article-body { max-width: 740px; }\n",
        encoding="utf-8",
    )
    changed = cmd._apply_site_plan({
        "summary": "refine existing rule",
        "edits": [{
            "path": "src/styles.css",
            "action": "replace",
            "old": ".article-body { max-width: 740px; }",
            "new": ".article-body { max-width: 760px; }",
        }],
    })
    assert changed == 1
    assert ".article-body { max-width: 760px; }" in styles.read_text(encoding="utf-8")


def test_site_context_includes_writer_prompts_for_article_length_request(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    files = {
        "src/App.jsx": "export default function App(){ return null }",
        "src/styles.css": "body{}",
        "agents/blog-lab-publisher/prompts/system.md": "SYSTEM RULES",
        "agents/blog-lab-publisher/prompts/task.md": "TASK RULES",
        "agents/blog-lab-publisher/config.yaml": "ai_provider: worker\n",
        "src/ArticleMedia.jsx": "export function ArticleMedia(){ return null }",
    }
    for rel, content in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    context = cmd._site_context("Naredi članke daljše in besedilo bolj profesionalno")
    paths = [item["path"] for item in context]
    assert "agents/blog-lab-publisher/prompts/system.md" in paths
    assert "agents/blog-lab-publisher/prompts/task.md" in paths
    assert "agents/blog-lab-publisher/config.yaml" in paths


def test_apply_site_plan_context_disambiguates_repeated_css_anchor(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "src/styles.css"
    path.parent.mkdir(parents=True)
    path.write_text(
        ".one { color: red; gap: 8px; }\n"
        ".two { color: blue; gap: 8px; }\n"
        ".three { color: green; gap: 8px; }\n"
        ".four { color: black; gap: 8px; }\n",
        encoding="utf-8",
    )
    changed = cmd._apply_site_plan({
        "edits": [{
            "path": "src/styles.css",
            "action": "replace",
            "old": "gap: 8px;",
            "new": "gap: 12px;",
            "before": ".two { color: blue; ",
        }],
    })
    value = path.read_text(encoding="utf-8")
    assert changed == 1
    assert ".two { color: blue; gap: 12px; }" in value
    assert value.count("gap: 8px;") == 3


def test_apply_site_plan_occurrence_disambiguates_repeated_anchor(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "src/example.jsx"
    path.parent.mkdir(parents=True)
    path.write_text("same\nsame\nsame\n", encoding="utf-8")
    changed = cmd._apply_site_plan({
        "edits": [{
            "path": "src/example.jsx",
            "action": "replace",
            "old": "same",
            "new": "middle",
            "occurrence": 2,
        }],
    })
    assert changed == 1
    assert path.read_text(encoding="utf-8") == "same\nmiddle\nsame\n"


def test_apply_site_plan_replace_all_is_explicit_and_bounded(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "src/styles.css"
    path.parent.mkdir(parents=True)
    path.write_text("gap: 8px;\ngap: 8px;\n", encoding="utf-8")
    changed = cmd._apply_site_plan({
        "edits": [{
            "path": "src/styles.css",
            "action": "replace_all",
            "old": "gap: 8px;",
            "new": "gap: 10px;",
        }],
    })
    assert changed == 1
    assert path.read_text(encoding="utf-8").count("gap: 10px;") == 2


def test_apply_site_plan_rewrite_requires_complete_context(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "src/Small.jsx"
    path.parent.mkdir(parents=True)
    path.write_text("export default 1;\n", encoding="utf-8")
    plan = {
        "edits": [{
            "path": "src/Small.jsx",
            "action": "rewrite",
            "new": "export default 2;",
        }],
    }
    with pytest.raises(cmd.SiteEditError, match="complete"):
        cmd._apply_site_plan(plan, [{"path": "src/Small.jsx", "complete": False, "snippets": []}])
    changed = cmd._apply_site_plan(
        plan,
        [{"path": "src/Small.jsx", "complete": True, "snippets": [{"label": "full", "content": "export default 1;"}]}],
    )
    assert changed == 1
    assert path.read_text(encoding="utf-8") == "export default 2;\n"


def test_ambiguous_replace_error_includes_match_locations(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "src/styles.css"
    path.parent.mkdir(parents=True)
    path.write_text(".a { gap: 8px; }\n.b { gap: 8px; }\n", encoding="utf-8")
    with pytest.raises(cmd.SiteEditError) as exc:
        cmd._apply_site_plan({
            "edits": [{
                "path": "src/styles.css",
                "action": "replace",
                "old": "gap: 8px;",
                "new": "gap: 12px;",
            }],
        })
    message = str(exc.value)
    assert "najden 2x" in message
    assert "line 1" in message and "line 2" in message
    assert "before/after" in message


def test_site_context_discovers_relevant_component_outside_fixed_list(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    files = {
        "src/App.jsx": "export default function App(){ return null }",
        "src/styles.css": "body{}",
        "src/components/NewsletterPanel.jsx": "export function NewsletterPanel(){ return <section>newsletter signup</section> }",
        "src/components/Unrelated.jsx": "export function Unrelated(){ return null }",
    }
    for rel, content in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    context = cmd._site_context("uredi newsletter signup komponento")
    paths = [item["path"] for item in context]
    assert "src/components/NewsletterPanel.jsx" in paths


def test_site_context_can_include_index_html_for_favicon_request(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    for rel, content in {
        "src/App.jsx": "export default function App(){ return null }",
        "src/styles.css": "body{}",
        "index.html": "<html><head><title>Blog Lab</title></head></html>",
    }.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    context = cmd._site_context("spremeni favicon in meta naslov strani")
    assert "index.html" in [item["path"] for item in context]


def test_workers_ai_site_command_self_corrects_ambiguous_replace(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "src/styles.css"
    path.parent.mkdir(parents=True)
    path.write_text(
        ".a { gap: 8px; }\n"
        ".b { gap: 8px; }\n"
        ".c { gap: 8px; }\n"
        ".d { gap: 8px; }\n",
        encoding="utf-8",
    )
    (tmp_path / "src/App.jsx").write_text("export default function App(){ return null }", encoding="utf-8")

    plans = [
        {
            "summary": "ambiguous first plan",
            "edits": [{"path": "src/styles.css", "action": "replace", "old": "gap: 8px;", "new": "gap: 12px;"}],
        },
        {
            "summary": "corrected plan",
            "edits": [{
                "path": "src/styles.css",
                "action": "replace",
                "old": "gap: 8px;",
                "new": "gap: 12px;",
                "before": ".c { ",
            }],
        },
    ]
    feedbacks = []

    def fake_request(command, context, feedback=""):
        feedbacks.append(feedback)
        return plans.pop(0)

    monkeypatch.setattr(cmd, "_site_ai_request", fake_request)
    cmd.workers_ai_site_command("spremeni razmik v tretjem CSS pravilu")

    value = path.read_text(encoding="utf-8")
    assert ".c { gap: 12px; }" in value
    assert len(feedbacks) == 2
    assert "najden 4x" in feedbacks[1]


def test_transactional_site_plan_rolls_back_existing_file_on_runtime_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "src/App.jsx"
    path.parent.mkdir(parents=True)
    path.write_text("const value = 'old';\n", encoding="utf-8")

    def fail_runtime(staged):
        assert "new" in next(iter(staged.values()))
        raise cmd.SiteEditError("build failed")

    monkeypatch.setattr(cmd, "_validate_site_runtime", fail_runtime)

    with pytest.raises(cmd.SiteEditError, match="build failed"):
        cmd._apply_site_plan({
            "edits": [{
                "path": "src/App.jsx",
                "action": "replace",
                "old": "'old'",
                "new": "'new'",
            }],
        }, validate_runtime=True)

    assert path.read_text(encoding="utf-8") == "const value = 'old';\n"


def test_transactional_site_plan_removes_created_file_on_runtime_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    (tmp_path / "src").mkdir(parents=True)

    monkeypatch.setattr(
        cmd,
        "_validate_site_runtime",
        lambda staged: (_ for _ in ()).throw(cmd.SiteEditError("invalid build")),
    )

    path = tmp_path / "src/NewPanel.jsx"
    with pytest.raises(cmd.SiteEditError, match="invalid build"):
        cmd._apply_site_plan({
            "edits": [{
                "path": "src/NewPanel.jsx",
                "action": "create",
                "new": "export default function NewPanel(){ return null }",
            }],
        }, validate_runtime=True)

    assert not path.exists()


def test_runtime_validator_rejects_invalid_json_without_npm(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    path = tmp_path / "public/site-settings.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(cmd.SiteEditError, match="JSON validation failed"):
        cmd._validate_site_runtime({path: "{not-json}"})


def test_workers_ai_site_command_retries_after_runtime_validation_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    src = tmp_path / "src"
    src.mkdir(parents=True)
    path = src / "App.jsx"
    path.write_text("const label = 'old';\n", encoding="utf-8")
    (src / "styles.css").write_text("body{}\n", encoding="utf-8")

    plans = [
        {
            "summary": "first patch",
            "edits": [{
                "path": "src/App.jsx",
                "action": "replace",
                "old": "'old'",
                "new": "'broken'",
            }],
        },
        {
            "summary": "repaired patch",
            "edits": [{
                "path": "src/App.jsx",
                "action": "replace",
                "old": "'old'",
                "new": "'good'",
            }],
        },
    ]
    feedbacks = []
    validations = []

    def fake_request(command, context, feedback=""):
        feedbacks.append(feedback)
        return plans.pop(0)

    def fake_runtime(staged):
        content = next(iter(staged.values()))
        validations.append(content)
        if "'broken'" in content:
            raise cmd.SiteEditError("Frontend build failed: synthetic syntax error")

    monkeypatch.setattr(cmd, "_site_ai_request", fake_request)
    monkeypatch.setattr(cmd, "_validate_site_runtime", fake_runtime)

    cmd.workers_ai_site_command("spremeni label")

    assert path.read_text(encoding="utf-8") == "const label = 'good';\n"
    assert len(validations) == 2
    assert "synthetic syntax error" in feedbacks[1]


def test_site_ai_request_fails_over_from_worker_quota_to_external(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.setenv("WORKER_AI_TOKEN", "worker-test")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("MODEL_API_KEY", "model-test")
    monkeypatch.setenv("MODEL_BASE_URL", "https://model.example/v1/chat/completions")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    calls = []

    def worker(system_prompt, request_text, context):
        calls.append("worker")
        raise cmd.SiteProviderUnavailable("Workers AI kvota/kapaciteta je trenutno izčrpana.")

    def external(system_prompt, request_text, context):
        calls.append("external")
        return {
            "summary": "external success",
            "edits": [],
            "_provider": "external",
        }

    def copilot(system_prompt, request_text, context):
        calls.append("copilot")
        return {
            "summary": "copilot success",
            "edits": [],
            "_provider": "copilot",
        }

    monkeypatch.setattr(cmd, "_workers_site_ai_request", worker)
    monkeypatch.setattr(cmd, "_external_site_ai_request", external)
    monkeypatch.setattr(cmd, "_copilot_site_ai_request", copilot)

    plan = cmd._site_ai_request(
        "uredi stran",
        [{"path": "src/App.jsx", "complete": True, "snippets": [{"label": "full", "content": "x"}]}],
    )

    assert plan["_provider"] == "external"
    assert calls == ["worker", "external"]


def test_site_ai_request_fails_over_to_copilot_when_worker_and_external_unavailable(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.setenv("WORKER_AI_TOKEN", "worker-test")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("MODEL_API_KEY", "model-test")
    monkeypatch.setenv("MODEL_BASE_URL", "https://model.example/v1/chat/completions")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    monkeypatch.setenv("COPILOT_GITHUB_TOKEN", "copilot-test")
    calls = []

    def unavailable(name):
        def inner(system_prompt, request_text, context):
            calls.append(name)
            raise cmd.SiteProviderUnavailable(f"{name} unavailable")
        return inner

    def copilot(system_prompt, request_text, context):
        calls.append("copilot")
        return {
            "summary": "copilot success",
            "edits": [],
            "_provider": "copilot",
        }

    monkeypatch.setattr(cmd, "_workers_site_ai_request", unavailable("worker"))
    monkeypatch.setattr(cmd, "_external_site_ai_request", unavailable("external"))
    monkeypatch.setattr(cmd, "_copilot_site_ai_request", copilot)

    plan = cmd._site_ai_request(
        "uredi stran",
        [{"path": "src/App.jsx", "complete": True, "snippets": [{"label": "full", "content": "x"}]}],
    )

    assert plan["_provider"] == "copilot"
    assert calls == ["worker", "external", "copilot"]


def test_workers_site_command_does_not_retry_provider_capacity_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "App.jsx").write_text("export default 1;\n", encoding="utf-8")
    (src / "styles.css").write_text("body{}\n", encoding="utf-8")

    calls = []
    def fail_once(command, context, feedback=""):
        calls.append(feedback)
        raise cmd.SiteProviderUnavailable("AI capacity unavailable")

    monkeypatch.setattr(cmd, "_site_ai_request", fail_once)

    with pytest.raises(cmd.SiteProviderUnavailable, match="capacity unavailable"):
        cmd.workers_ai_site_command("uredi stran")

    assert len(calls) == 1


def test_workers_site_ai_adapter_sends_repository_context(monkeypatch):
    monkeypatch.setenv("WORKER_AI_TOKEN", "test-token")
    monkeypatch.setenv("WORKER_SITE_AI_URL", "https://worker.example/api/ai/edit")
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def read(self):
            return json.dumps({
                "ok": True,
                "plan": {"summary": "ok", "edits": []},
            }).encode("utf-8")

    def fake_urlopen(request, timeout=0):
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(cmd, "urlopen", fake_urlopen)
    context = [{
        "path": "src/App.jsx",
        "complete": True,
        "snippets": [{"label": "full", "content": "export default 1;"}],
    }]

    plan = cmd._workers_site_ai_request(
        "system",
        "OPERATOR REQUEST:\nuredi stran",
        context,
    )

    assert plan["_provider"] == "workers_ai"
    assert captured["body"]["context"] == context
    assert "REPOSITORY CONTEXT" not in captured["body"]["request"]
    assert captured["body"]["request"].startswith("OPERATOR REQUEST:")


def test_auto_site_ai_does_not_call_unconfigured_fallbacks(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "auto")
    monkeypatch.setenv("WORKER_AI_TOKEN", "worker-test")
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("COPILOT_GITHUB_TOKEN", raising=False)
    calls = []

    def worker(system_prompt, request_text, context):
        calls.append("worker")
        return {"summary": "ok", "edits": [], "_provider": "workers_ai"}

    def should_not_run(*args, **kwargs):
        raise AssertionError("unconfigured provider must not run")

    monkeypatch.setattr(cmd, "_workers_site_ai_request", worker)
    monkeypatch.setattr(cmd, "_external_site_ai_request", should_not_run)
    monkeypatch.setattr(cmd, "_copilot_site_ai_request", should_not_run)

    plan = cmd._site_ai_request(
        "uredi stran",
        [{"path": "src/App.jsx", "complete": True, "snippets": [{"label": "full", "content": "x"}]}],
    )
    assert plan["_provider"] == "workers_ai"
    assert calls == ["worker"]


def test_article_ai_unavailable_is_nonretryable(tmp_path, monkeypatch, capsys):
    app = tmp_path / "src/App.jsx"
    app.parent.mkdir(parents=True)
    app.write_text("before")
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    monkeypatch.setattr(cmd, "ARTICLE_AGENT", tmp_path / "agent.py")
    monkeypatch.setattr(cmd.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=4))
    with pytest.raises(SystemExit) as exc:
        cmd.article_command("Objavi članek o dogodku", "aktualno")
    assert exc.value.code == 64
    assert "ARTICLE_AI_UNAVAILABLE" in capsys.readouterr().err


def test_site_command_marks_provider_outage_nonretryable(monkeypatch, capsys):
    monkeypatch.setattr(
        cmd,
        "builtin_site_command",
        lambda command: False,
    )
    monkeypatch.setattr(
        cmd,
        "workers_ai_site_command",
        lambda command: (_ for _ in ()).throw(
            cmd.SiteProviderUnavailable("Workers AI quota exhausted")
        ),
    )
    with pytest.raises(SystemExit) as exc:
        cmd.site_command("uredi izgled strani")
    assert exc.value.code == 64
    assert "SITE_AI_CAPACITY_UNAVAILABLE" in capsys.readouterr().err


@pytest.mark.parametrize(("text", "expected"), [
    ("polespaj strna prosim", "site"),
    ("wrtie artcle about ljubljana", "article"),
    ("publsih post o današnjem športu", "article"),
    ("izklpoi agenta", "control"),
    ("sttaus agenta", "control"),
    ("schdeule automatic publishing", "control"),
    ("make website prettier", "site"),
    ("imrpove desgin of page", "site"),
])
def test_intent_autocorrect_routes_common_typos(text, expected):
    assert cmd.infer_mode(text) == expected


def test_intent_autocorrect_folds_diacritics_and_english_aliases():
    normalized = cmd._normalized_intent("NAPIŠI ARTICLE in polepšaj WEBSITE")
    assert "napisi" in normalized
    assert "clanek" in normalized
    assert "polepsaj" in normalized
    assert "stran" in normalized


def test_intent_autocorrect_preserves_literal_command_text_in_ai_prompt():
    command = "Spremeni ime strani v Project Clanak X"
    context = [{
        "path": "src/App.jsx",
        "complete": True,
        "snippets": [{"label": "full", "content": "export default 1;"}],
    }]
    _, request = cmd._site_ai_prompts(command, context)
    assert command in request
    assert "NORMALIZED INTENT HINT" in request
    assert "preserve names and values exactly" in request


def test_fuzzy_control_command_can_disable_agent(tmp_path, monkeypatch):
    control = tmp_path / "data/agent-control.json"
    control.parent.mkdir(parents=True)
    control.write_text(
        json.dumps({"enabled": True, "publish_mode": "automatic"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(cmd, "CONTROL", control)

    cmd.control_command("izklpoi agenta")

    data = json.loads(control.read_text(encoding="utf-8"))
    assert data["enabled"] is False


def test_fuzzy_design_command_is_handled_by_builtin(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    css = tmp_path / "src/styles.css"
    css.parent.mkdir(parents=True)
    css.write_text("body{}", encoding="utf-8")

    assert cmd.builtin_site_command("polespaj strna prosim") is True
    assert cmd.DESIGN_MARKER in css.read_text(encoding="utf-8")


def test_intent_autocorrect_does_not_force_unknown_topic_into_control():
    assert cmd.infer_mode("Objavi članek o Liverpoolu in Evertonu") == "article"


def test_main_reports_privacy_safe_intent_routing(tmp_path, monkeypatch, capsys):
    path = tmp_path / "command.json"
    path.write_text(
        json.dumps({"command": "wrtie artcle about test", "mode": "auto", "category": "aktualno"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(cmd, "article_command", lambda command, category: None)
    monkeypatch.setattr(sys, "argv", ["command.py", "--command-file", str(path)])

    assert cmd.main() == 0
    output = capsys.readouterr().out
    assert "INTENT_ROUTE" in output
    assert "resolved=article" in output
    assert "autocorrected=true" in output
    assert "wrtie artcle about test" not in output


@pytest.mark.parametrize("text", [
    "article about današnji promet v Ljubljani",
    "write something about današnji šport",
    "wrtie something about lokalnem dogodku",
    "please create article regarding nova razstava",
])
def test_natural_article_phrasing_routes_to_article(text):
    assert cmd.infer_mode(text) == "article"


def test_turn_agent_off_routes_to_control_and_disables(tmp_path, monkeypatch):
    control = tmp_path / "data/agent-control.json"
    control.parent.mkdir(parents=True)
    control.write_text(json.dumps({"enabled": True, "publish_mode": "automatic"}), encoding="utf-8")
    monkeypatch.setattr(cmd, "CONTROL", control)

    assert cmd.infer_mode("turn agent off") == "control"
    cmd.control_command("turn agent off")
    assert json.loads(control.read_text(encoding="utf-8"))["enabled"] is False


@pytest.mark.parametrize(("text", "expected"), [
    ("ugasi agnta molim", "control"),
    ("proveri sttaus agenta", "control"),
    ("pokreni objavljivajne", "control"),
    ("napisi clnak o lokalnom dogadjaju", "article"),
    ("objavi claanak o tehnologiji", "article"),
    ("uredi stranicu i dodaj galerju", "site"),
    ("redizajn sajta za mobilni", "site"),
    ("fix the webiste navigation", "site"),
    ("create an artcle about science", "article"),
    ("shut dwon agent", "control"),
])
def test_multilingual_and_heavy_typo_intent_routing(text, expected):
    assert cmd.infer_mode(text) == expected


@pytest.mark.parametrize(("text", "needle"), [
    ("provjeri status agenta", "preveri status agent"),
    ("uredi stranicu", "uredi stran"),
    ("redesign the website", "izboljsaj dizajn stran"),
    ("turn agent off", "izklopi agent"),
])
def test_phrase_alias_normalization(text, needle):
    assert needle in cmd._normalized_intent(text)
