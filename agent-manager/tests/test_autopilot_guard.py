import os

import pytest

from manager.autopilot import AutonomousRepairExecutor, AutopilotDisabled


def test_write_mode_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENT_MANAGER_WRITE_ENABLED", raising=False)
    with pytest.raises(AutopilotDisabled):
        AutonomousRepairExecutor.assert_write_enabled()


def test_write_mode_can_be_enabled_explicitly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_MANAGER_WRITE_ENABLED", "1")
    AutonomousRepairExecutor.assert_write_enabled()
