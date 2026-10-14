from manager.roles_v8 import EmailRolesV8


def test_default_role_is_least_privilege(monkeypatch):
    monkeypatch.delenv("GMAIL_COMMAND_ROLES", raising=False)
    roles = EmailRolesV8("owner@example.com")
    assert roles.role("OWNER@example.com") == "owner"
    assert roles.role("colleague@example.com") == "viewer"
    assert roles.allowed("colleague@example.com", "all", "STATUS")
    assert not roles.allowed("colleague@example.com", "bloglab", "publish blog")
    assert not roles.allowed("colleague@example.com", "manager", "restart manager")


def test_operator_can_trigger_pv_diagnostics_only(monkeypatch):
    monkeypatch.setenv("GMAIL_COMMAND_ROLES", '{"colleague@example.com":"operator"}')
    roles = EmailRolesV8("owner@example.com")
    assert roles.allowed("colleague@example.com", "project_visibility", "TEST API")
    assert roles.allowed("colleague@example.com", "project_visibility",
                         'PREVIEW_JSON {"name":"Studio","pages":[{"slug":"index","title":"Home"}]}')
    assert not roles.allowed("colleague@example.com", "bloglab", "objavi clanek")
    assert not roles.allowed("colleague@example.com", "project_visibility", "deploy main")


def test_explicit_owner_override_is_conservative(monkeypatch):
    monkeypatch.setenv("GMAIL_COMMAND_ROLES", '{"teammate@example.com":"viewer"}')
    roles = EmailRolesV8("owner@example.com")
    assert roles.role("owner@example.com") == "owner"
    assert roles.role("teammate@example.com") == "viewer"
