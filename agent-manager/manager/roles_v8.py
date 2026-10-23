"""Least-privilege command roles, enforced *after* Gmail authentication."""
from __future__ import annotations

import json
import os

READ_ONLY = {
    "status", "stanje", "health", "preveri status",
    "status vseh agentov", "flota", "fleet status",
    "pomoc", "help", "incidenti", "incidents", "napake",
    "ram", "pomnilnik", "memory", "modeli", "models",
    "providers", "email status", "gmail status",
    "opravila", "jobs", "queue",
    "github status", "rollback plan bloglab", "rollback plan pv",
}
PV_DIAGNOSTICS = {
    "test api", "ci", "preveri ci", "frontend benchmark", "lighthouse",
}


class EmailRolesV8:
    def __init__(self, owner: str):
        self.owner = owner.strip().lower()
        self.config_error = ""
        try:
            overrides = json.loads(os.getenv("GMAIL_COMMAND_ROLES", "{}"))
            if not isinstance(overrides, dict):
                raise ValueError("Role overrides must be a JSON object.")
            if any(role not in {"owner", "operator", "viewer"}
                   for role in overrides.values()):
                raise ValueError("Unsupported Gmail role.")
            self.roles = {str(k).lower(): str(v) for k, v in overrides.items()}
        except (ValueError, TypeError):
            # Never take down the 24/7 Manager over a configuration typo.
            # All mail execution is disabled until the operator corrects it.
            self.roles = {}
            self.config_error = "GMAIL_COMMAND_ROLES is invalid; no email commands allowed."

    def role(self, sender: str) -> str:
        sender = sender.strip().lower()
        if sender == self.owner and self.owner:
            return "owner"
        return self.roles.get(sender, "viewer")

    def allowed(self, sender: str, target: str, command: str) -> bool:
        role = self.role(sender)
        if role == "owner":
            return True
        text = " ".join(command.lower().split())
        if target == "all":
            return text in {
                "status", "stanje", "health", "preveri status",
                "status vseh agentov", "flota", "fleet status",
            }
        if text in READ_ONLY:
            return True
        if role == "viewer":
            return False
        # Operators can request bounded off-host diagnostics/previews.
        # Arbitrary edits and deployments stay in review queue, never bypassed.
        if target == "project_visibility":
            return text in PV_DIAGNOSTICS or (
                text.startswith("preview_json ") and len(command) <= 4000
            )
        return False
