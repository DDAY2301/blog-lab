from __future__ import annotations

import asyncio
import json
from pathlib import Path

from manager.capabilities_v2 import CapabilityRegistryV2
from manager.coder_prompt_v1 import (
    CODER_FIX_PROMPT,
    CODER_FIX_VERSION,
    PROGRAMMER_WORKFLOW_PROMPT,
    PROGRAMMER_WORKFLOW_VERSION,
    coder_fix_prompt_digest,
    programmer_prompt_digest,
)
from manager.db_v3 import StoreV3
from manager.models import RepairPlanRequest
from manager.remote_v4 import _coder_target, _is_coder_command
from manager.repair import RepairPlanner


PATCH = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-print("old")
+print("new")
"""


class FakeAI:
    def __init__(self):
        self.calls = []

    async def chat_json(self, system: str, user: str):
        self.calls.append((system, user))
        return "fake/coder", {
            "summary": "minimal repair",
            "plan": ["patch app", "run tests"],
            "patch": PATCH,
            "tests": ["python app.py"],
            "risk": "low",
        }


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "app.py").write_text('print("old")\n', encoding="utf-8")
    (tmp_path / "test_app.py").write_text("def test_ok(): assert True\n", encoding="utf-8")
    return tmp_path


def test_programmer_and_coder_fix_prompts_are_versioned_and_strict():
    assert PROGRAMMER_WORKFLOW_VERSION == "programmer-workflow-v1.0"
    assert CODER_FIX_VERSION == "coder-fix-v1.0"
    assert len(programmer_prompt_digest()) == 16
    assert len(coder_fix_prompt_digest()) == 16
    assert "Inspect before editing" in PROGRAMMER_WORKFLOW_PROMPT
    assert "root-cause fixes" in PROGRAMMER_WORKFLOW_PROMPT
    assert "Return JSON only" in PROGRAMMER_WORKFLOW_PROMPT
    assert "candidate patch was already applied" in CODER_FIX_PROMPT
    assert "Never hide the failure" in CODER_FIX_PROMPT
    assert "CURRENT candidate worktree" in CODER_FIX_PROMPT


def test_repair_plan_uses_programmer_workflow_prompt(tmp_path):
    async def run():
        ai = FakeAI()
        planner = RepairPlanner(ai)
        result = await planner.plan(
            RepairPlanRequest(root=str(_repo(tmp_path)), objective="Change old to new.")
        )
        assert result.valid is True
        assert ai.calls
        system, user = ai.calls[0]
        payload = json.loads(user)
        assert system == PROGRAMMER_WORKFLOW_PROMPT
        assert payload["prompt_version"] == PROGRAMMER_WORKFLOW_VERSION
        assert payload["prompt_digest"] == programmer_prompt_digest()
        assert payload["objective"] == "Change old to new."

    asyncio.run(run())


def test_failed_candidate_uses_coder_fix_prompt_and_failure_evidence(tmp_path):
    async def run():
        ai = FakeAI()
        planner = RepairPlanner(ai)
        root = _repo(tmp_path)
        result = await planner.fix_failed_candidate(
            root=root,
            objective="Change old to new.",
            failures=[
                {
                    "name": "pytest",
                    "argv": ["python", "-m", "pytest", "-q"],
                    "returncode": 1,
                    "stdout": "1 failed",
                    "stderr": "AssertionError: expected new",
                }
            ],
            changed_files=["app.py"],
            attempt=1,
        )
        assert result.valid is True
        system, user = ai.calls[0]
        payload = json.loads(user)
        assert system == CODER_FIX_PROMPT
        assert payload["prompt_version"] == CODER_FIX_VERSION
        assert payload["attempt"] == 1
        assert payload["changed_files"] == ["app.py"]
        assert payload["validation_failures"][0]["returncode"] == 1
        assert "app.py" in payload["selected_current_candidate_context"]

    asyncio.run(run())


def test_manager_capabilities_advertise_coder_workflow(tmp_path):
    registry = CapabilityRegistryV2(StoreV3(tmp_path / "manager.db"))
    manager = registry.get("manager")
    assert manager is not None
    assert "code.repair.plan" in manager.capabilities
    assert "code.repair.autopilot" in manager.capabilities
    assert "code.test_fix" in manager.capabilities
    assert "git.pull_request" in manager.capabilities


def test_remote_manager_recognizes_programmer_and_coder_fix_commands():
    assert _is_coder_command("programer plan za BlogLab popravi test") is True
    assert _is_coder_command("coder fix Project Visibility: popravi napako") is True
    assert _coder_target("coder fix Project Visibility") == "project_visibility"
    assert _coder_target("programmer plan BlogLab") == "bloglab"
    assert _coder_target("coder fix manager") == "manager"
