"""Prevent recursive GitHub workflow_run cascades between guardian and self-heal."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "Blog Lab Production Guardian": ".github/workflows/production-guardian.yml",
    "Blog Lab Self Heal": ".github/workflows/self-heal.yml",
}
triggers = {}
for name, relative in FILES.items():
    workflow = yaml.load((ROOT / relative).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    on = workflow.get("on", {})
    workflow_run = on.get("workflow_run", {}) if isinstance(on, dict) else {}
    triggers[name] = set(workflow_run.get("workflows", []))
if (
    "Blog Lab Self Heal" in triggers["Blog Lab Production Guardian"]
    and "Blog Lab Production Guardian" in triggers["Blog Lab Self Heal"]
):
    raise SystemExit("WORKFLOW_RUN_CYCLE: Guardian and Self Heal trigger each other")
print("WORKFLOW_TRIGGER_GRAPH_OK: no reciprocal Guardian/Self Heal cycle")
