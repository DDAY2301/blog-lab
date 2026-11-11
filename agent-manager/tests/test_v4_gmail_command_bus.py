from __future__ import annotations

from manager.gmail_v4 import COMMAND_SCOPE, SEND_SCOPE, GmailV4
from manager.mail_commands_v4 import GmailCommandLoopV4


def test_gmail_scope_switches_to_modify_for_commands(monkeypatch, tmp_path):
    monkeypatch.setenv("GMAIL_REPORTING_ENABLED", "1")
    monkeypatch.setenv("GMAIL_COMMANDS_ENABLED", "1")
    monkeypatch.setenv("REPORT_TO_EMAIL", "dan.grmusa@gmail.com")
    monkeypatch.setenv("GMAIL_FROM_EMAIL", "dan.grmusa@gmail.com")
    monkeypatch.setenv("GMAIL_OAUTH_CLIENT_FILE", str(tmp_path / "client.json"))
    monkeypatch.setenv("GMAIL_OAUTH_TOKEN_FILE", str(tmp_path / "token.json"))
    gmail = GmailV4()
    assert gmail.scopes == [COMMAND_SCOPE, SEND_SCOPE]
    assert gmail.implementation == "gmail-command-bus-v3"


def test_gmail_scope_stays_send_only_without_commands(monkeypatch, tmp_path):
    monkeypatch.setenv("GMAIL_REPORTING_ENABLED", "1")
    monkeypatch.setenv("GMAIL_COMMANDS_ENABLED", "0")
    monkeypatch.setenv("REPORT_TO_EMAIL", "dan.grmusa@gmail.com")
    monkeypatch.setenv("GMAIL_FROM_EMAIL", "dan.grmusa@gmail.com")
    monkeypatch.setenv("GMAIL_OAUTH_CLIENT_FILE", str(tmp_path / "client.json"))
    monkeypatch.setenv("GMAIL_OAUTH_TOKEN_FILE", str(tmp_path / "token.json"))
    gmail = GmailV4()
    assert gmail.scopes == [SEND_SCOPE]
    assert gmail.implementation == "gmail-send-only-v2"


def test_command_subject_routes():
    assert GmailCommandLoopV4._subject_target("[AGENT ALL] preveri status") == ("all", "preveri status")
    assert GmailCommandLoopV4._subject_target("[AGENT BLOGLAB]") == ("bloglab", "")
    assert GmailCommandLoopV4._subject_target("[AGENT PV] preflight") == ("project_visibility", "preflight")
    assert GmailCommandLoopV4._subject_target("[AGENT MANAGER] maintenance") == ("manager", "maintenance")
    assert GmailCommandLoopV4._subject_target("[AGENT]") == ("", "")
    assert GmailCommandLoopV4._subject_target("normal email") == (None, "")
