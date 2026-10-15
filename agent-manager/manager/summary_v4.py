from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from .db_v3 import StoreV3, utcnow
from .notifications_v4 import NotificationCenterV4


class SummaryReporterV4:
    def __init__(self, store: StoreV3, notify: NotificationCenterV4) -> None:
        self.store = store
        self.notify = notify
        self.interval = max(300, int(os.getenv("AGENT_MANAGER_SUMMARY_INTERVAL", "3600")))
        self.last_at = 0.0
        self.output = Path(os.getenv("AGENT_MANAGER_SUMMARY_FILE", "./data/latest-summary.json")).expanduser()
        if not self.output.is_absolute():
            self.output = Path(__file__).resolve().parents[1] / self.output

    def due(self) -> bool:
        return time.time() - self.last_at >= self.interval

    def build(self, targets: list[dict[str, Any]], providers: dict[str, Any]) -> dict[str, Any]:
        failing = [x for x in targets if not x.get("ok")]
        incidents = self.store.query(
            "SELECT id,severity,status,component,title,last_seen,occurrence_count "
            "FROM incidents WHERE status!='resolved' ORDER BY last_seen DESC LIMIT 25"
        )
        state = "HEALTHY" if not failing and not any(x.get("severity") in {"P0","P1"} for x in incidents) else "DEGRADED"
        return {
            "generated_at": utcnow(),
            "state": state,
            "managed_total": len(targets),
            "managed_ok": len(targets) - len(failing),
            "managed_failing": len(failing),
            "failing_targets": [
                {"id": x.get("id"), "name": x.get("name"), "error": x.get("error"), "status_code": x.get("status_code")}
                for x in failing
            ],
            "open_incidents": incidents,
            "providers": providers,
        }

    def emit(self, targets: list[dict[str, Any]], providers: dict[str, Any]) -> dict[str, Any] | None:
        if not self.due():
            return None
        report = self.build(targets, providers)
        self.output.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.output.with_suffix(self.output.suffix + ".tmp")
        tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.output)
        self.store.event("HOURLY_SUMMARY", "summary-v4", "info", report)
        if report["state"] == "DEGRADED":
            self.notify.send(
                "P1",
                "Agent Manager: system degraded",
                f'{report["managed_failing"]} managed target(s) failing; {len(report["open_incidents"])} incident(s) open.',
                "summary-v4",
            )
        self.last_at = time.time()
        return report
