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
    process_match: str = ""
    executable: str = ""
    arguments: list[str] | None = None
    working_dir: str = ""
    interval_seconds: int = 60


class ManagedAgentSupervisorV4:
    def __init__(self, store: StoreV3, config_path: Path) -> None:
        self.store = store
        self.config_path = config_path
        self.incidents = IncidentEngineV3(store)
        self.notify = NotificationCenterV4(store)
        self._failure_counts: dict[str, int] = {}
        self._last_repair: dict[str, float] = {}
        self._last_check: dict[str, float] = {}
        self._cached: dict[str, dict[str, Any]] = {}
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
            now = time.time()
            interval = max(30, int(target.interval_seconds or 60))
            if target.id in self._cached and now - self._last_check.get(target.id, 0) < interval:
                result = dict(self._cached[target.id])
                result["cached"] = True
                results.append(result)
                continue
            try:
                result = await self.check(target)
            except Exception as exc:
                result = {"id": target.id, "name": target.name, "ok": False, "error": str(exc)}
            self._last_check[target.id] = now
            self._cached[target.id] = dict(result)
            results.append(result)
            self._persist(target, result)
            await self._incident_and_repair(target, result)
        return results

    async def check(self, target: ManagedTarget) -> dict[str, Any]:
        if target.kind == "http":
            return await self._check_http(target)
        if target.kind == "process":
            return self._check_process(target)
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

    def _check_process(self, target: ManagedTarget) -> dict[str, Any]:
        if not target.process_match:
            return {"id": target.id, "name": target.name, "ok": False, "error": "process_match is required"}
        try:
            import psutil
            needle = target.process_match.lower()
            matches = []
            for proc in psutil.process_iter(["pid","name","cmdline"]):
                try:
                    hay = " ".join([str(proc.info.get("name") or "")] + list(proc.info.get("cmdline") or [])).lower()
                    if needle in hay:
                        matches.append({"pid": proc.info["pid"], "name": proc.info.get("name"), "cmdline": (proc.info.get("cmdline") or [])[:8]})
                except Exception:
                    pass
            return {"id": target.id, "name": target.name, "ok": bool(matches), "process_match": target.process_match, "matches": matches[:20]}
        except Exception as exc:
            return {"id": target.id, "name": target.name, "ok": False, "error": str(exc)}

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
        if not token:
            gh = shutil.which("gh")
            if gh:
                try:
                    probe = subprocess.run(
                        [gh, "auth", "token"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if probe.returncode == 0:
                        token = probe.stdout.strip()
                except Exception:
                    token = ""
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _check_github(self, target: ManagedTarget) -> dict[str, Any]:
        url = f"https://api.github.com/repos/{target.repo}/actions/runs"
        wanted = target.workflows or []
        latest: dict[str, dict[str, Any]] = {}
        pages_checked = 0
        async with httpx.AsyncClient(timeout=15.0) as client:
            for page in range(1, 6):
                params = {"branch": target.branch, "per_page": 100, "page": page}
                r = await client.get(url, headers=self._github_headers(), params=params)
                pages_checked = page
                if r.status_code >= 400:
                    return {
                        "id": target.id,
                        "name": target.name,
                        "ok": False,
                        "repo": target.repo,
                        "status_code": r.status_code,
                        "error": r.text[:300],
                    }
                runs = r.json().get("workflow_runs", [])
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
                if wanted and all(name in latest for name in wanted):
                    break
                if len(runs) < 100:
                    break

        failures = [
            name for name, row in latest.items()
            if row.get("status") == "completed"
            and row.get("conclusion") in {"failure", "cancelled", "timed_out", "action_required"}
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
            "pages_checked": pages_checked,
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
        elif count == 3:
            self.notify.send("P1", title, f"{target.name} failed three consecutive checks. Automatic recovery is being attempted where a safe adapter exists.", target.id)

        if count >= 2 and target.repair_adapter:
            last = self._last_repair.get(target.id, 0)
            if time.time() - last >= self.repair_cooldown:
                repair = self.repair(target)
                self._last_repair[target.id] = time.time()
                self.store.action("maintenance-v4", "repair", target.id, "attempted", repair)
                if repair.get("ok"):
                    self.notify.send("P2", f"{target.name} recovery started", repair.get("summary","Repair action started."), target.id)
                elif count >= 3:
                    self.notify.send("P1", f"{target.name} recovery needs attention", repair.get("summary","Automatic recovery was not available."), target.id)

    def repair(self, target: ManagedTarget) -> dict[str, Any]:
        adapter = target.repair_adapter
        if adapter == "project_visibility_restart":
            return self._restart_project_visibility(target)
        if adapter == "bloglab_self_heal":
            return self._dispatch_bloglab_self_heal(target)
        if adapter == "local_process_restart":
            return self._restart_local_process(target)
        return {"ok": False, "stage": "unsupported", "summary": f"No safe repair adapter registered for {adapter}"}

    def _restart_project_visibility(self, target: ManagedTarget) -> dict[str, Any]:
        root_value = os.getenv(target.local_root_env or "PROJECT_VISIBILITY_ROOT", "").strip()
        if not root_value:
            return {"ok": False, "stage": "config", "summary": "PROJECT_VISIBILITY_ROOT is not configured."}
        root = Path(root_value).expanduser().resolve()
        py = root / ".venv" / "Scripts" / "python.exe"
        secret_file = root / "api" / "data" / ".app-secret"
        if not py.exists():
            return {"ok": False, "stage": "runtime", "summary": f"Project Visibility Python runtime not found: {py}"}

        try:
            import psutil
            for conn in psutil.net_connections(kind="inet"):
                if not conn.laddr or conn.laddr.port != 8000 or conn.status != psutil.CONN_LISTEN or not conn.pid:
                    continue
                try:
                    proc = psutil.Process(conn.pid)
                    cmdline = " ".join(proc.cmdline())
                    cwd = Path(proc.cwd()).resolve()
                    try:
                        in_root = cwd == root or cwd.is_relative_to(root)
                    except AttributeError:
                        in_root = cwd == root or root in cwd.parents
                    belongs = in_root and "api.server:app" in cmdline
                    if belongs:
                        proc.terminate()
                        try:
                            proc.wait(timeout=8)
                        except psutil.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=5)
                    else:
                        return {
                            "ok": False,
                            "stage": "port_conflict",
                            "summary": f"Port 8000 belongs to unrelated PID {conn.pid}; refusing to terminate it.",
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as exc:
            return {"ok": False, "stage": "stop_old", "summary": f"Could not safely inspect/stop old listener: {exc}"}

        env = os.environ.copy()
        env["OLLAMA_BASE_URL"] = env.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        env["OLLAMA_MODEL"] = env.get("PROJECT_VISIBILITY_MODEL", "qwen2.5-coder:3b")
        if secret_file.exists():
            env["APP_SECRET"] = secret_file.read_text(encoding="utf-8").strip()

        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
        try:
            child = subprocess.Popen(
                [str(py), "-m", "uvicorn", "api.server:app", "--host", "127.0.0.1", "--port", "8000"],
                cwd=str(root),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
        except Exception as exc:
            return {"ok": False, "stage": "restart", "summary": str(exc)}

        deadline = time.time() + 25
        health_url = target.health_url or "http://127.0.0.1:8000/health"
        while time.time() < deadline:
            if child.poll() is not None:
                return {
                    "ok": False,
                    "stage": "verify",
                    "summary": f"Replacement Project Visibility process exited with code {child.returncode}.",
                }
            try:
                with httpx.Client(timeout=3.0) as client:
                    response = client.get(health_url)
                if 200 <= response.status_code < 400:
                    return {
                        "ok": True,
                        "stage": "verified_restart",
                        "summary": "Project Visibility restarted and health endpoint recovered.",
                        "pid": child.pid,
                    }
            except Exception:
                pass
            time.sleep(1)

        return {
            "ok": False,
            "stage": "verify",
            "summary": "Replacement process started but health did not recover within 25 seconds.",
            "pid": child.pid,
        }

    def _restart_local_process(self, target: ManagedTarget) -> dict[str, Any]:
        if target.kind != "process":
            return {"ok": False, "stage": "policy", "summary": "local_process_restart is only valid for process targets."}
        if self._check_process(target).get("ok"):
            return {"ok": True, "stage": "already_running", "summary": f"{target.name} is already running."}

        exe = Path(target.executable).expanduser()
        if not exe.is_absolute() or not exe.exists() or not exe.is_file():
            return {"ok": False, "stage": "config", "summary": "A valid absolute executable path is required."}

        workdir = Path(target.working_dir).expanduser() if target.working_dir else exe.parent
        if not workdir.is_absolute() or not workdir.exists() or not workdir.is_dir():
            return {"ok": False, "stage": "config", "summary": "A valid absolute working directory is required."}

        args = target.arguments or []
        if not isinstance(args, list) or not all(isinstance(x, str) for x in args):
            return {"ok": False, "stage": "config", "summary": "arguments must be a list of strings."}

        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
        try:
            child = subprocess.Popen(
                [str(exe), *args],
                cwd=str(workdir),
                env=os.environ.copy(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
                shell=False,
            )
        except Exception as exc:
            return {"ok": False, "stage": "start", "summary": str(exc)}

        deadline = time.time() + 15
        while time.time() < deadline:
            if child.poll() is not None:
                return {
                    "ok": False,
                    "stage": "verify",
                    "summary": f"Process exited with code {child.returncode}.",
                }
            check = self._check_process(target)
            if check.get("ok"):
                return {
                    "ok": True,
                    "stage": "verified_restart",
                    "summary": f"{target.name} restarted and process match recovered.",
                    "pid": child.pid,
                }
            time.sleep(0.5)
        return {
            "ok": False,
            "stage": "verify",
            "summary": "Process started but the configured process match did not recover within 15 seconds.",
            "pid": child.pid,
        }

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

    def save_target(self, payload: dict[str, Any]) -> ManagedTarget:
        allowed_adapters = {"", "project_visibility_restart", "bloglab_self_heal", "local_process_restart"}
        target = ManagedTarget(**payload)
        if target.kind not in {"http", "github_repo", "hybrid", "process"}:
            raise ValueError("kind must be http, github_repo, hybrid, or process")
        if target.repair_adapter not in allowed_adapters:
            raise ValueError("repair_adapter is not allowed")
        target.interval_seconds = max(30, min(int(target.interval_seconds or 60), 3600))
        if target.kind in {"http", "hybrid"} and not target.health_url:
            raise ValueError("health_url is required for http/hybrid targets")
        if target.kind in {"github_repo", "hybrid"} and not target.repo:
            raise ValueError("repo is required for github_repo/hybrid targets")
        if target.kind == "process" and not target.process_match:
            raise ValueError("process_match is required for process targets")
        if target.repair_adapter == "local_process_restart":
            if target.kind != "process":
                raise ValueError("local_process_restart is only valid for process targets")
            exe = Path(target.executable).expanduser()
            if not exe.is_absolute():
                raise ValueError("local_process_restart requires an absolute executable path")
            if target.working_dir and not Path(target.working_dir).expanduser().is_absolute():
                raise ValueError("working_dir must be absolute")
            if target.arguments is not None and not all(isinstance(x, str) for x in target.arguments):
                raise ValueError("arguments must be a list of strings")
        data = {"version": 1, "targets": []}
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        rows = data.setdefault("targets", [])
        replaced = False
        for i, row in enumerate(rows):
            if row.get("id") == target.id:
                rows[i] = target.__dict__
                replaced = True
                break
        if not replaced:
            rows.append(target.__dict__)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.config_path)
        return target

    def remove_target(self, target_id: str) -> bool:
        if not self.config_path.exists():
            return False
        data = json.loads(self.config_path.read_text(encoding="utf-8"))
        rows = data.get("targets", [])
        kept = [row for row in rows if row.get("id") != target_id]
        if len(kept) == len(rows):
            return False
        data["targets"] = kept
        tmp = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.config_path)
        self.store.execute("DELETE FROM managed_target_status WHERE target_id=?", (target_id,))
        return True

    def status_rows(self) -> list[dict[str, Any]]:
        rows = self.store.query("SELECT * FROM managed_target_status ORDER BY name")
        for row in rows:
            try:
                row["details"] = json.loads(row["details"])
            except Exception:
                pass
        return rows
