from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "data" / "terminal-command-test-suite.json"


def load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {rel}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


command = load_module("bloglab_operator_command_test", "agents/operator-terminal/command.py")
compound = load_module("bloglab_compound_control_test", "agents/operator-terminal/compound_control.py")
deferred_articles = load_module("bloglab_deferred_articles_test", "agents/operator-terminal/deferred_articles.py")
deferred_site = load_module("bloglab_deferred_site_test", "agents/operator-terminal/deferred_site_edits.py")


def require(condition, message: str):
    if not condition:
        raise AssertionError(message)


suite = json.loads(SUITE.read_text(encoding="utf-8"))
cases = suite.get("commands") or []
operator_cases = [item for item in cases if item.get("operator_mode")]
routing_failures = []
for item in operator_cases:
    actual = command.infer_mode(item["text"])
    if actual != item["operator_mode"]:
        routing_failures.append({
            "name": item["name"],
            "text": item["text"],
            "expected": item["operator_mode"],
            "actual": actual,
        })
if routing_failures:
    raise AssertionError("Operator routing failures: " + json.dumps(routing_failures, ensure_ascii=False))


with tempfile.TemporaryDirectory(prefix="bloglab-operator-test-") as temp:
    tmp = Path(temp)
    original_control = command.CONTROL
    original_compound_control = compound.CONTROL
    original_catchup_log = compound.CATCHUP_LOG
    original_article_queue = deferred_articles.QUEUE
    original_site_queue = deferred_site.QUEUE

    try:
        control_path = tmp / "agent-control.json"
        control_path.write_text(
            json.dumps({"enabled": True, "publish_mode": "automatic"}, ensure_ascii=False),
            encoding="utf-8",
        )
        command.CONTROL = control_path
        compound.CONTROL = control_path
        compound.CATCHUP_LOG = tmp / "catchup-requests.json"

        def run_control(text: str):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                command.control_command(text)
            return json.loads(control_path.read_text(encoding="utf-8")), out.getvalue()

        ctl, _ = run_control("ustavi agenta in objavljanje")
        require(ctl.get("enabled") is False, "stop command did not disable agent")

        ctl, _ = run_control("nadaljuj objavljanje in vklopi agenta")
        require(ctl.get("enabled") is True, "start command did not enable agent")

        ctl, _ = run_control("preklopi agent na draft način")
        require(ctl.get("publish_mode") == "draft", "draft publish mode failed")

        ctl, _ = run_control("preklopi objavljanje na review mode")
        require(ctl.get("publish_mode") == "review", "review publish mode failed")

        ctl, _ = run_control("preklopi objavljanje na automatic mode")
        require(ctl.get("publish_mode") == "automatic", "automatic publish mode failed")

        ctl, _ = run_control("nastavi objavljanje 3x na dan po urniku")
        slots = ((ctl.get("schedule") or {}).get("slots") or [])
        require(
            [slot.get("time") for slot in slots] == ["08:17", "13:27", "19:43"],
            "default verified schedule changed",
        )
        require(
            [slot.get("category") for slot in slots] == ["sport", "politika", "aktualno"],
            "default schedule categories changed",
        )

        status_before = control_path.read_text(encoding="utf-8")
        status_ctl, status_out = run_control("preveri status agenta")
        require("CONTROL_STATUS" in status_out, "status command did not emit CONTROL_STATUS")
        require(control_path.read_text(encoding="utf-8") == status_before, "status command mutated control state")
        require(status_ctl.get("enabled") is True, "status test unexpectedly changed state")

        for unsupported in (
            "nastavi objavljanje 4x na dan",
            "objavljaj vsako uro",
            "nastavi urnik objav ob 09:00 14:00 20:00",
        ):
            try:
                command.control_command(unsupported)
            except SystemExit as exc:
                require(exc.code == 64, f"unsupported schedule returned {exc.code!r}: {unsupported}")
            else:
                raise AssertionError(f"unsupported schedule was accepted: {unsupported}")

        require(command._safe_site_relpath("src/App.jsx") == "src/App.jsx", "safe site path rejected")
        require(command._safe_site_relpath("public/site-settings.json") == "public/site-settings.json", "public site path rejected")
        for dangerous in (
            "../secret.txt",
            ".github/workflows/pwn.yml",
            "terminal/worker/src/index.js",
            "agents/operator-terminal/command.py",
            "/etc/passwd",
        ):
            try:
                command._safe_site_relpath(dangerous)
            except command.SiteEditError:
                pass
            else:
                raise AssertionError(f"dangerous site path accepted: {dangerous}")

        require(command._requested_theme(command._intent_text("spremeni temo v pastelno modro")) == "pastel-blue", "pastel blue theme intent failed")
        require(command._requested_theme(command._intent_text("change theme to dark")) == "dark", "dark theme intent failed")

        require(
            compound.should_handle("izvedi objave 3 na dan po časovnici"),
            "compound schedule command was not recognized",
        )
        catchup_command = "izvedi objave 3 na dan po časovnici zdaj pa napiši vse članke ki smo jih spustili zaradi popravkov na strani"
        folded = compound.fold(catchup_command)
        require(compound.has_schedule_intent(folded), "compound schedule intent missing")
        require(compound.has_catchup_intent(folded), "compound catch-up intent missing")

        compound.ensure_schedule(catchup_command, "test")
        compound_ctl = json.loads(control_path.read_text(encoding="utf-8"))
        require(compound_ctl.get("enabled") is True, "compound command did not enable agent")
        require(compound_ctl.get("publish_mode") == "automatic", "compound command did not force automatic mode")

        # Deferred queues must de-duplicate the same request ID instead of growing forever.
        payload = tmp / "payload.json"
        payload.write_text(json.dumps({
            "request_id": "same-request",
            "command": "objavi članek o testni temi",
            "category": "aktualno",
            "actor": "test",
        }, ensure_ascii=False), encoding="utf-8")

        deferred_articles.QUEUE = tmp / "deferred-articles.json"
        deferred_articles.append_deferred(str(payload), "same-request", "ARTICLE_AI_UNAVAILABLE")
        deferred_articles.append_deferred(str(payload), "same-request", "ARTICLE_AI_UNAVAILABLE again")
        article_items = json.loads(deferred_articles.QUEUE.read_text(encoding="utf-8"))
        require(len(article_items) == 1, "deferred article queue did not de-duplicate request ID")
        require(deferred_articles.is_writer_capacity_log("ARTICLE_AI_UNAVAILABLE"), "article capacity classifier failed")

        site_payload = tmp / "site-payload.json"
        site_payload.write_text(json.dumps({
            "request_id": "same-site-request",
            "command": "izboljšaj header strani",
            "category": "aktualno",
            "actor": "test",
        }, ensure_ascii=False), encoding="utf-8")
        deferred_site.QUEUE = tmp / "deferred-site-edits.json"
        deferred_site.append_deferred(str(site_payload), "same-site-request", "SITE_AI_CAPACITY_UNAVAILABLE")
        deferred_site.append_deferred(str(site_payload), "same-site-request", "SITE_AI_CAPACITY_UNAVAILABLE again")
        site_items = json.loads(deferred_site.QUEUE.read_text(encoding="utf-8"))
        require(len(site_items) == 1, "deferred site queue did not de-duplicate request ID")
        require(deferred_site.is_capacity_log("SITE_AI_CAPACITY_UNAVAILABLE"), "site capacity classifier failed")

    finally:
        command.CONTROL = original_control
        compound.CONTROL = original_compound_control
        compound.CATCHUP_LOG = original_catchup_log
        deferred_articles.QUEUE = original_article_queue
        deferred_site.QUEUE = original_site_queue


print(json.dumps({
    "ok": True,
    "suite_version": suite.get("version"),
    "operator_routing_cases": len(operator_cases),
    "control_modes": ["stop", "start", "draft", "review", "automatic", "schedule", "status"],
    "unsafe_site_paths_rejected": 5,
    "compound_control": "ok",
    "deferred_queue_dedup": "ok",
}, ensure_ascii=False, indent=2))
