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
    assert "Workers AI site edit failed" in str(exc.value)
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


def test_unknown_theme_is_explicitly_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(cmd, "BASE", tmp_path)
    css = tmp_path / "src/styles.css"
    css.parent.mkdir(parents=True)
    css.write_text("body{}", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        cmd.builtin_site_command("spremeni barvno temo v koralno")
    assert exc.value.code == 64


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
