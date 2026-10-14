"""Low-memory GitHub workflow receipt reconciler for Agent Manager V8.

GitHub 204 dispatch means SUBMITTED, never COMPLETED. This watcher only
closes jobs after matching the exact workflow run and expected preview artifact.
It never launches the production PV agent or changes a repository.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from .db_v3 import StoreV3, utcnow

REPO = "DDAY2301/PROJEKT"
WORKFLOW = "pv-remote-preview-v8.yml"
REQUEST_ID = re.compile(r"^[0-9a-f]{32}$")
RUN_PREFIX = "PV Preview V8 "
MAX_AGE = timedelta(hours=24)


class RemoteRunWatcherV8:
    def __init__(self, store: StoreV3, *, interval: int = 90):
        self.store = store
        self.interval = max(60, interval)
        self.last: dict[str, Any] = {"status": "not_started"}
        self._stop = asyncio.Event()

    def stop(self) -> None:
        self._stop.set()

    def _token(self) -> str:
        return (
            os.getenv("AGENT_MANAGER_GITHUB_TOKEN", "").strip()
            or os.getenv("GITHUB_TOKEN", "").strip()
            or os.getenv("GH_TOKEN", "").strip()
        )

    async def cycle(self) -> dict[str, Any]:
        candidates = self.store.query(
            """SELECT s.job_id,s.step_id,s.result_json,j.updated_at
               FROM command_steps s JOIN command_jobs j ON j.id=s.job_id
               WHERE s.status IN ('submitted','running')
               AND j.status IN ('submitted','running')
               ORDER BY j.updated_at LIMIT 25"""
        )
        relevant = []
        for row in candidates:
            try:
                receipt = json.loads(row.get("result_json") or "{}")
                if (receipt.get("workflow") == WORKFLOW and
                    receipt.get("repo") == REPO and
                    receipt.get("operation") == "remote_preview" and
                    REQUEST_ID.fullmatch(str(receipt.get("request_id") or ""))):
                    relevant.append((row, receipt))
            except (TypeError, ValueError):
                continue

        if not relevant:
            self.last = {"status": "idle", "checked": 0, "ts": utcnow()}
            return self.last
        token = self._token()
        if not token:
            self.last = {
                "status": "credentials_missing",
                "checked": len(relevant),
                "ts": utcnow(),
            }
            return self.last
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        url = (
            f"https://api.github.com/repos/{REPO}/actions/workflows/"
            f"{WORKFLOW}/runs"
        )
        updated = 0
        async with httpx.AsyncClient(timeout=18.0) as client:
            response = await client.get(
                url, headers=headers,
                params={"event": "workflow_dispatch", "branch": "main", "per_page": 100},
            )
            if response.status_code != 200:
                self.last = {
                    "status": "github_unavailable",
                    "http_status": response.status_code,
                    "checked": len(relevant),
                    "ts": utcnow(),
                }
                return self.last
            runs = response.json().get("workflow_runs", [])
            indexed = {
                str(r.get("display_title") or ""): r
                for r in runs if r.get("event") == "workflow_dispatch"
                and r.get("head_branch") == "main"
            }
            now = datetime.now(timezone.utc)
            for row, receipt in relevant:
                rid = receipt["request_id"]
                run = indexed.get(RUN_PREFIX + rid)
                if not run:
                    age = now - datetime.fromisoformat(row["updated_at"])
                    if age > MAX_AGE:
                        self._finish(row, receipt, "failed", "No matching GitHub run within 24 hours.")
                        updated += 1
                    continue
                run_id = run.get("id")
                if not isinstance(run_id, int) or run_id <= 0:
                    continue
                receipt["run_id"] = run_id
                receipt["run_url"] = (
                    f"https://github.com/{REPO}/actions/runs/{run_id}"
                )
                if run.get("status") != "completed":
                    self._save_receipt(row, receipt, "running")
                    updated += 1
                    continue
                if run.get("conclusion") != "success":
                    self._finish(
                        row, receipt, "failed",
                        f"GitHub workflow ended: {str(run.get('conclusion'))[:60]}",
                    )
                    updated += 1
                    continue
                artifact_response = await client.get(
                    f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/artifacts",
                    headers=headers, params={"per_page": 100},
                )
                if artifact_response.status_code != 200:
                    continue
                expected = f"pv-preview-{run_id}"
                artifact = next(
                    (a for a in artifact_response.json().get("artifacts", [])
                     if a.get("name") == expected and not a.get("expired")),
                    None,
                )
                if artifact is None:
                    # A successful workflow with no verified artifact is not done.
                    if now - datetime.fromisoformat(row["updated_at"]) > timedelta(hours=2):
                        self._finish(row, receipt, "failed", "Successful run missing preview artifact.")
                        updated += 1
                    continue
                receipt["artifact"] = {
                    "name": expected,
                    "id": artifact.get("id"),
                    "size_in_bytes": artifact.get("size_in_bytes"),
                }
                self._finish(row, receipt, "completed", "")
                updated += 1
        self.last = {
            "status": "checked", "checked": len(relevant),
            "updated": updated, "ts": utcnow(),
        }
        return self.last

    def _save_receipt(self, row: dict[str, Any], receipt: dict, status: str) -> None:
        self.store.execute(
            """UPDATE command_steps SET status=?,result_json=?
               WHERE job_id=? AND step_id=? AND status IN ('submitted','running')""",
            (status, json.dumps(receipt, ensure_ascii=False),
             row["job_id"], row["step_id"]),
        )

    def _finish(self, row: dict[str, Any], receipt: dict,
                status: str, error: str) -> None:
        self.store.execute(
            """UPDATE command_steps
               SET status=?,finished_at=?,result_json=?,error=?
               WHERE job_id=? AND step_id=? AND status IN ('submitted','running')""",
            (status, utcnow(), json.dumps(receipt, ensure_ascii=False),
             error or None, row["job_id"], row["step_id"]),
        )
        other = self.store.query(
            "SELECT status FROM command_steps WHERE job_id=?",
            (row["job_id"],),
        )
        statuses = {x["status"] for x in other}
        if statuses <= {"completed"}:
            job_status = "completed"
        elif "failed" in statuses:
            job_status = "partial" if "completed" in statuses else "failed"
        elif "waiting_approval" in statuses:
            job_status = "waiting_approval"
        else:
            job_status = "running"
        self.store.execute(
            """UPDATE command_jobs SET status=?,updated_at=?,error=?
               WHERE id=? AND status IN ('submitted','running')""",
            (job_status, utcnow(), error or None, row["job_id"]),
        )
        self.store.action(
            "remote-run-watcher-v8", "preview_verified", row["job_id"],
            status, {"request_id": receipt["request_id"],
                     "run_url": receipt.get("run_url", ""), "error": error[:200]},
        )
        # Queue one final email to the authenticated owner; the existing
        # Gmail sender retries delivery separately without executing commands.
        owner = self.store.query(
            "SELECT sender FROM job_control_v8 WHERE job_id=?", (row["job_id"],),
        )
        if owner:
            subject = (
                f"[AGENT RESULT] JOB {row['job_id']} - {job_status.upper()}"
            )
            existing = self.store.query(
                "SELECT id FROM email_queue WHERE kind=? AND subject=?",
                ("v8-remote-pv", subject),
            )
            if not existing:
                artifact = receipt.get("artifact") or {}
                message = (
                    f"Project Visibility remote preview: {status.upper()}\n"
                    f"Job: {row['job_id']}\n"
                    f"GitHub run: {receipt.get('run_url', '')}\n"
                    f"Artifact: {artifact.get('name', 'unavailable')}\n"
                    f"Error: {error or 'none'}\n"
                    "A verified preview is not a production deployment."
                )
                self.store.execute(
                    """INSERT INTO email_queue(
                        created_at,kind,priority,recipient,subject,body,status
                    ) VALUES(?,?,?,?,?,?,'pending')""",
                    (utcnow(), "v8-remote-pv", 3, owner[0]["sender"],
                     subject, message),
                )

    async def run(self) -> None:
        while not self._stop.is_set():
            try:
                await self.cycle()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.last = {
                    "status": "error", "error": f"{type(exc).__name__}: {exc}"[:200],
                    "ts": utcnow(),
                }
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass
