from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from .db_v3 import StoreV3, utcnow
from .incidents_v3 import IncidentEngineV3
from .notifications_v4 import NotificationCenterV4


@dataclass
class ManagedTarget:
    id: str
    name: str
    kind: str
    enabled: bool = True
    health_url: str = ""
    repo: str = ""
    branch: str = "main"
    workflows: list[str] | None = None
    repair_adapter: str = ""
    local_root_env: str = ""


class ManagedAgentSupervisorV4:
    def __init__(self, store: StoreV3, config_path: Path) -> None:
        self.store = store
        self.config_path = config_path
        self.incidents = IncidentEngineV3(store)
        self.notify = NotificationCenterV4(store)
        self._failure_counts: dict[str, int] = {}
        self._last_repair: dict[str, float] = {}
        self.repair_cooldown = max(300, int(os.getenv("AGENT_MANAGER_REPAIR_COOLDOWN", "1800")))

    def targets(self) -> list[ManagedTarget]:
        if not self.config_path.exists():
            return []
        data = json.loads(self.config_path.read_text(encoding="utf-8"))
        rows = data.get("targets", [])
        out: list[ManagedTarget] = []
        for row in rows:
            try:
                out.append(ManagedTarget(**row))
            except TypeError:
                continue
        return [x for x in out if x.enabled]

    async def check_all(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for target in self.targets():
            try:
                result = await self.check(target)
            except Exception as exc:
                result = {"id": target.id, "name": target.name, "ok": False, "error": str(exc)}
            results.append(result)
            self._persist(target, result)
            await self._incident_and_repair(target, result)
        return results

    async def check(self, target: ManagedTarget) -> dict[str, Any]:
        if target.kind == "http":
            return await self._check_http(target)
        if target.kind == "github_repo":
            return await self._check_github(target)
        if target.kind == "hybrid":
            http_result = await self._check_http(target) if target.health_url else {"ok": True}
            gh_result = await self._check_github(target) if target.repo else {"ok": True}
            return {
                "id": target.id,
                "name": target.name,
                "ok": bool(http_result.get("ok") and gh_result.get("ok")),
                "http": http_result,
                "github": gh_result,
            }
        return {"id": target.id, "name": target.name, "ok": False, "error": f"Unknown target kind: {target.kind}"}

    async def _check_http(self, target: ManagedTarget) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                r = await client.get(target.health_url)
            ok = 200 <= r.status_code < 400
            return {
                "id": target.id,
                "name": target.name,
                "ok": ok,
                "status_code": r.status_code,
                "latency_ms": round((time.perf_counter() - start) * 1000, 1),
                "url": target.health_url,
                "body": r.text[:500],
            }
        except Exception as exc:
            return {
                "id": target.id,
                "name": target.name,
                "ok": False,
                "latency_ms": round((time.perf_counter() - start) * 1000, 1),
                "url": target.health_url,
                "error": str(exc),
            }

    def _github_headers(self) -> dict[str, str]:
        token = os.getenv("GITHUB_TOKEN", "").strip() or os.getenv("GH_TOKEN", "").strip()
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _check_github(self, target: ManagedTarget) -> dict[str, Any]:
        url = f"https://api.github.com/repos/{target.repo}/actions/runs"
        params = {"branch": target.branch, "per_page": 50}
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, headers=self._github_headers(), params=params)
        if r.status_code >= 400:
            return {"id": target.id, "name": target.name, "ok": False, "repo": target.repo, "status_code": r.status_code, "error": r.text[:300]}
        runs = r.json().get("workflow_runs", [])
        wanted = target.workflows or []
        latest: dict[str, dict[str, Any]] = {}
        for run in runs:
            name = str(run.get("name") or run.get("workflow_name") or "")
            if wanted and name not in wanted:
                continue
            if name not in latest:
                latest[name] = {
                    "status": run.get("status"),
                    "conclusion": run.get("conclusion"),
                    "created_at": run.get("created_at"),
                    "updated_at": run.get("updated_at"),
                    "html_url": run.get("html_url"),
                    "run_attempt": run.get("run_attempt"),
                }
        failures = [
            name for name, row in latest.items()
            if row.get("status") == "completed" and row.get("conclusion") in {"failure", "cancelled", "timed_out", "action_required"}
        ]
        missing = [name for name in wanted if name not in latest]
        return {
            "id": target.id,
            "name": target.name,
            "ok": not failures and not missing,
            "repo": target.repo,
            "workflows": latest,
            "failed_workflows": failures,
            "missing_workflows": missing,
        }

    def _persist(self, target: ManagedTarget, result: dict[str, Any]) -> None:
        now = utcnow()
        self.store.execute(
            """
            INSERT INTO managed_target_status(target_id,name,kind,ok,last_check,details)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(target_id) DO UPDATE SET
              name=excluded.name,kind=excluded.kind,ok=excluded.ok,last_check=excluded.last_check,details=excluded.details
            """,
            (target.id, target.name, target.kind, 1 if result.get("ok") else 0, now, json.dumps(result, ensure_ascii=False)),
        )

    async def _incident_and_repair(self, target: ManagedTarget, result: dict[str, Any]) -> None:
        title = f"{target.name} health degraded"
        if result.get("ok"):
            self._failure_counts[target.id] = 0
            self.incidents.resolve_matching(target.id, title, {"health": result})
            return

        count = self._failure_counts.get(target.id, 0) + 1
        self._failure_counts[target.id] = count
        severity = "P1" if count >= 3 else "P2"
        incident = self.incidents.raise_or_update(target.id, title, severity, [json.dumps(result, ensure_ascii=False)[:2000]])
        if count == 1:
            self.notify.send(severity, title, f"Manager detected a problem with {target.name}.", target.id)

        if count >= 2 and target.repair_adapter:
            last = self._last_repair.get(target.id, 0)
            if time.time() - last >= self.repair_cooldown:
                repair = self.repair(target)
                self._last_repair[target.id] = time.time()
                self.store.action("maintenance-v4", "repair", target.id, "attempted", repair)
                if repair.get("ok"):
                    self.notify.send("P2", f"{target.name} recovery started", repair.get("summary","Repair action started."), target.id)

    def repair(self, target: ManagedTarget) -> dict[str, Any]:
        adapter = target.repair_adapter
        if adapter == "project_visibility_restart":
            return self._restart_project_visibility(target)
        if adapter == "bloglab_self_heal":
            return self._dispatch_bloglab_self_heal(target)
        return {"ok": False, "stage": "unsupported", "summary": f"No safe repair adapter registered for {adapter}"}

    def _restart_project_visibility(self, target: ManagedTarget) -> dict[str, Any]:
        root_value = os.getenv(target.local_root_env or "PROJECT_VISIBILITY_ROOT", "").strip()
        if not root_value:
            return {"ok": False, "stage": "config", "summary": "PROJECT_VISIBILITY_ROOT is not configured."}
        root = Path(root_value).expanduser()
        py = root / ".venv" / "Scripts" / "python.exe"
        secret_file = root / "api" / "data" / ".app-secret"
        if not py.exists():
            return {"ok": False, "stage": "runtime", "summary": f"Project Visibility Python runtime not found: {py}"}

        env = os.environ.copy()
        env["OLLAMA_BASE_URL"] = env.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        env["OLLAMA_MODEL"] = env.get("PROJECT_VISIBILITY_MODEL", "qwen2.5-coder:3b")
        if secret_file.exists():
            env["APP_SECRET"] = secret_file.read_text(encoding="utf-8").strip()

        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
        try:
            subprocess.Popen(
                [str(py), "-m", "uvicorn", "api.server:app", "--host", "127.0.0.1", "--port", "8000"],
                cwd=str(root),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
            return {"ok": True, "stage": "restart", "summary": "Project Visibility background restart launched."}
        except Exception as exc:
            return {"ok": False, "stage": "restart", "summary": str(exc)}

    def _dispatch_bloglab_self_heal(self, target: ManagedTarget) -> dict[str, Any]:
        gh = shutil.which("gh")
        if not gh:
            return {"ok": False, "stage": "auth_required", "summary": "GitHub CLI is not installed/authenticated; Blog Lab remains monitor-only."}
        try:
            auth = subprocess.run([gh, "auth", "status"], capture_output=True, text=True, timeout=20)
            if auth.returncode != 0:
                return {"ok": False, "stage": "auth_required", "summary": "GitHub CLI is not authenticated."}
            run = subprocess.run(
                [gh, "workflow", "run", "self-heal.yml", "--repo", target.repo, "--ref", target.branch],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if run.returncode != 0:
                return {"ok": False, "stage": "dispatch", "summary": (run.stderr or run.stdout)[-1000:]}
            return {"ok": True, "stage": "dispatch", "summary": "Blog Lab Self Heal workflow dispatched."}
        except Exception as exc:
            return {"ok": False, "stage": "dispatch", "summary": str(exc)}

    def status_rows(self) -> list[dict[str, Any]]:
        rows = self.store.query("SELECT * FROM managed_target_status ORDER BY name")
        for row in rows:
            try:
                row["details"] = json.loads(row["details"])
            except Exception:
                pass
        return rows
