from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from typing import Any

import httpx

from .ai_router_v4 import AIRouterV4
from .artifacts_v2 import ArtifactStoreV2
from .capabilities_v2 import CapabilityRegistryV2
from .db_v3 import StoreV3, utcnow
from .remote_v4 import _dispatch

BLOG_LAB_BASE = os.getenv("BLOG_LAB_WORKER_URL", "https://blog-lab.dan-grmusa.workers.dev").rstrip("/")
MAX_STEPS = max(1, min(12, int(os.getenv("AGENT_MANAGER_MAX_PLAN_STEPS", "8"))))
COMMAND_CONCURRENCY = max(1, min(4, int(os.getenv("AGENT_MANAGER_COMMAND_CONCURRENCY", "2"))))


class UniversalCommandBusV2:
    """Plan, route and execute natural-language work across registered agents."""

    def __init__(self, store: StoreV3) -> None:
        self.store = store
        self.registry = CapabilityRegistryV2(store)
        self.artifacts = ArtifactStoreV2(store)
        self.ai = AIRouterV4()
        self._execution_gate = asyncio.Semaphore(COMMAND_CONCURRENCY)

    @staticmethod
    def _fold(value: str) -> str:
        text = str(value or "").lower()
        text = text.translate(str.maketrans({"č": "c", "š": "s", "ž": "z", "ć": "c", "đ": "d"}))
        return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())

    def _fallback_target(self, command: str) -> str:
        low = self._fold(command)
        if any(x in low for x in ("bloglab", "blog lab", "clanek", "objavi", "blog ", "rubrika")):
            return "bloglab"
        if any(x in low for x in ("project visibility", "preflight", "website", "spletna stran", "builder", "queue")):
            return "project_visibility"
        if any(x in low for x in ("agent manager", "incident", "maintenance", "provider", "model", "health")):
            return "manager"
        return "all"

    def _fallback_plan(self, command: str) -> dict[str, Any]:
        return {
            "summary": "Deterministic single-step fallback plan.",
            "steps": [
                {
                    "id": "s1",
                    "target": self._fallback_target(command),
                    "command": command,
                    "depends_on": [],
                    "use_artifacts": True,
                }
            ],
        }

    def _validate_plan(self, raw: Any, command: str) -> dict[str, Any]:
        if not isinstance(raw, dict):
            return self._fallback_plan(command)
        rows = raw.get("steps")
        if not isinstance(rows, list) or not rows:
            return self._fallback_plan(command)

        valid: list[dict[str, Any]] = []
        seen: set[str] = set()
        targets = set(self.registry.targets()) | {"all"}
        for index, item in enumerate(rows[:MAX_STEPS], start=1):
            if not isinstance(item, dict):
                continue
            step_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(item.get("id") or f"s{index}")).strip("-")[:40] or f"s{index}"
            if step_id in seen:
                step_id = f"s{index}"
            target = str(item.get("target") or "").strip().lower()
            step_command = str(item.get("command") or "").strip()
            if target not in targets or not step_command:
                continue
            depends = [
                str(x).strip()
                for x in (item.get("depends_on") or [])
                if str(x).strip() and str(x).strip() != step_id
            ][:MAX_STEPS]
            valid.append(
                {
                    "id": step_id,
                    "target": target,
                    "command": step_command[:4000],
                    "depends_on": depends,
                    "use_artifacts": bool(item.get("use_artifacts", True)),
                }
            )
            seen.add(step_id)

        if not valid:
            return self._fallback_plan(command)
        valid_ids = {row["id"] for row in valid}
        for row in valid:
            row["depends_on"] = [x for x in row["depends_on"] if x in valid_ids]
        return {
            "summary": str(raw.get("summary") or "Multi-agent execution plan.")[:1200],
            "steps": valid,
        }

    async def plan(
        self,
        command: str,
        *,
        explicit_target: str = "",
        artifacts: list[dict[str, Any]] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        target = str(explicit_target or "").strip().lower()
        if target:
            if target not in set(self.registry.targets()) | {"all"}:
                raise ValueError("Unknown explicit target.")
            return "explicit", {
                "summary": f"Explicit target: {target}",
                "steps": [
                    {
                        "id": "s1",
                        "target": target,
                        "command": command,
                        "depends_on": [],
                        "use_artifacts": True,
                    }
                ],
            }

        artifact_view = [self.artifacts.public_view(x) for x in (artifacts or [])]
        system = (
            "You are the planner for a local multi-agent command bus. "
            "Split the operator request into the smallest useful executable steps. "
            "Use only registered targets. Independent steps may have no dependencies; "
            "dependent steps must name earlier step ids. Never invent credentials or shell commands. "
            "Return JSON only with shape: "
            "{\"summary\":\"...\",\"steps\":[{\"id\":\"s1\",\"target\":\"REGISTERED_TARGET_ID_OR_all\","
            "\"command\":\"...\",\"depends_on\":[],\"use_artifacts\":true}]}. "
            "The target value must exactly match one registered agent id or all."
        )
        user = (
            f"REGISTERED AGENTS:\n{self.registry.planner_text()}\n\n"
            f"ARTIFACTS:\n{json.dumps(artifact_view, ensure_ascii=False)}\n\n"
            f"OPERATOR REQUEST:\n{command[:12000]}"
        )
        try:
            provider, raw = await self.ai.chat_json(system, user)
            return provider, self._validate_plan(raw, command)
        except Exception:
            return "deterministic", self._fallback_plan(command)

    def _create_job(
        self,
        *,
        source: str,
        source_id: str,
        request_text: str,
        planner: str,
        plan: dict[str, Any],
        artifacts: list[dict[str, Any]],
    ) -> str:
        job_id = str(uuid.uuid4())
        now = utcnow()
        self.store.execute(
            """
            INSERT INTO command_jobs(
              id,source,source_id,request_text,status,planner,plan_json,created_at,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                job_id,
                source,
                source_id,
                request_text,
                "planned",
                planner,
                json.dumps(plan, ensure_ascii=False),
                now,
                now,
            ),
        )
        artifact_ids = [str(x.get("id")) for x in artifacts if x.get("id")]
        for step in plan["steps"]:
            self.store.execute(
                """
                INSERT INTO command_steps(
                  job_id,step_id,target,command_text,status,depends_on,artifacts
                ) VALUES(?,?,?,?,?,?,?)
                """,
                (
                    job_id,
                    step["id"],
                    step["target"],
                    step["command"],
                    "pending",
                    json.dumps(step.get("depends_on") or []),
                    json.dumps(artifact_ids if step.get("use_artifacts", True) else []),
                ),
            )
        return job_id

    async def _upload_bloglab_image(
        self,
        artifact: dict[str, Any],
        cache: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        artifact_id = str(artifact.get("id") or "")
        if artifact_id in cache:
            return cache[artifact_id]
        token = os.getenv("FLEET_AGENT_TOKEN", "").strip()
        if not token:
            raise RuntimeError("FLEET_AGENT_TOKEN is not configured.")
        raw = self.artifacts.read_bytes(artifact)
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.post(
                f"{BLOG_LAB_BASE}/api/fleet/media",
                headers={"authorization": f"Bearer {token}"},
                files={
                    "file": (
                        str(artifact.get("filename") or "image"),
                        raw,
                        str(artifact.get("mime_type") or "application/octet-stream"),
                    )
                },
            )
        try:
            data = response.json()
        except Exception:
            data = {"text": response.text[:1000]}
        if response.status_code >= 400:
            raise RuntimeError(f"BlogLab media upload HTTP {response.status_code}: {data}")
        cache[artifact_id] = data
        return data

    async def _enrich_command(
        self,
        target: str,
        command: str,
        artifacts: list[dict[str, Any]],
        upload_cache: dict[str, dict[str, Any]],
    ) -> str:
        if not artifacts:
            return command[:4000]

        lines: list[str] = []
        budget = 2600
        for artifact in artifacts[:12]:
            name = str(artifact.get("filename") or "artifact")
            mime = str(artifact.get("mime_type") or "application/octet-stream")
            size = int(artifact.get("size_bytes") or 0)
            if target == "bloglab" and mime.startswith("image/"):
                uploaded = await self._upload_bloglab_image(artifact, upload_cache)
                url = str(uploaded.get("url") or uploaded.get("path") or "")
                role = "Use this attached image in the requested work"
                lines.append(f"- {name} ({mime}, {size} bytes): {role}. URL={url}")
                continue

            excerpt = self.artifacts.text_excerpt(artifact)
            if excerpt and budget > 0:
                clipped = excerpt[: min(1800, budget)]
                budget -= len(clipped)
                lines.append(f"- {name} ({mime}):\n{clipped}")
            else:
                lines.append(f"- {name} ({mime}, {size} bytes), artifact_id={artifact.get('id')}")

        if not lines:
            return command[:4000]
        suffix = "\n\nATTACHED ARTIFACTS (trusted operator data):\n" + "\n".join(lines)
        remaining = max(200, 4000 - len(suffix))
        return command[:remaining] + suffix[: 4000 - remaining]

    async def _dispatch_dynamic(
        self,
        target: str,
        command: str,
        artifacts: list[dict[str, Any]],
    ) -> Any:
        capability = self.registry.get(target)
        if not capability or capability.dispatch_kind != "http" or not capability.command_url:
            raise RuntimeError(f"No dispatch adapter is registered for target {target}.")
        headers: dict[str, str] = {"content-type": "application/json"}
        if capability.token_env:
            token = os.getenv(capability.token_env, "").strip()
            if not token:
                raise RuntimeError(
                    f"Required token environment variable {capability.token_env} is not configured."
                )
            headers[capability.token_header or "authorization"] = f"{capability.token_prefix}{token}"
        payload = {
            "command": command,
            "artifacts": [self.artifacts.public_view(x) for x in artifacts],
            "actor": "agent-manager-v4",
        }
        async with httpx.AsyncClient(timeout=180.0, follow_redirects=True) as client:
            response = await client.post(capability.command_url, headers=headers, json=payload)
        try:
            data = response.json()
        except Exception:
            data = {"text": response.text[:3000]}
        if response.status_code >= 400:
            raise RuntimeError(
                f"Dynamic agent {target} returned HTTP {response.status_code}: {data}"
            )
        return data

    async def _execute_target(
        self,
        target: str,
        command: str,
        artifacts: list[dict[str, Any]],
        upload_cache: dict[str, dict[str, Any]],
    ) -> Any:
        if target == "all":
            async def one(name: str):
                enriched = await self._enrich_command(name, command, artifacts, upload_cache)
                try:
                    if name in {"manager", "project_visibility", "bloglab"}:
                        result = await _dispatch(name, enriched)
                    else:
                        result = await self._dispatch_dynamic(name, enriched, artifacts)
                    return name, {"ok": True, "result": result}
                except Exception as exc:
                    return name, {"ok": False, "error": str(exc)[:1800]}

            rows = await asyncio.gather(*(one(name) for name in self.registry.targets()))
            return {"targets": dict(rows)}

        enriched = await self._enrich_command(target, command, artifacts, upload_cache)
        if target in {"manager", "project_visibility", "bloglab"}:
            return await _dispatch(target, enriched)
        return await self._dispatch_dynamic(target, enriched, artifacts)

    async def _run_step(
        self,
        job_id: str,
        step: dict[str, Any],
        artifacts: list[dict[str, Any]],
        upload_cache: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        step_id = step["id"]
        started = utcnow()
        self.store.execute(
            "UPDATE command_steps SET status='running',started_at=? WHERE job_id=? AND step_id=?",
            (started, job_id, step_id),
        )
        try:
            async with self._execution_gate:
                result = await self._execute_target(
                    step["target"],
                    step["command"],
                    artifacts if step.get("use_artifacts", True) else [],
                    upload_cache,
                )
            self.store.execute(
                """
                UPDATE command_steps
                SET status='completed',finished_at=?,result_json=?,error=NULL
                WHERE job_id=? AND step_id=?
                """,
                (utcnow(), json.dumps(result, ensure_ascii=False, default=str)[:50000], job_id, step_id),
            )
            return {"id": step_id, "target": step["target"], "status": "completed", "result": result}
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            self.store.execute(
                """
                UPDATE command_steps
                SET status='failed',finished_at=?,error=?
                WHERE job_id=? AND step_id=?
                """,
                (utcnow(), error[:4000], job_id, step_id),
            )
            return {"id": step_id, "target": step["target"], "status": "failed", "error": error}

    async def execute(
        self,
        command: str,
        *,
        source: str,
        source_id: str,
        explicit_target: str = "",
        artifacts: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        artifact_rows = list(artifacts or [])
        planner, plan = await self.plan(command, explicit_target=explicit_target, artifacts=artifact_rows)
        job_id = self._create_job(
            source=source,
            source_id=source_id,
            request_text=command,
            planner=planner,
            plan=plan,
            artifacts=artifact_rows,
        )
        self.store.execute(
            "UPDATE command_jobs SET status='running',updated_at=? WHERE id=?",
            (utcnow(), job_id),
        )
        self.store.action(
            "universal-command-bus-v2",
            "job_started",
            explicit_target or "auto",
            "running",
            {"job_id": job_id, "planner": planner, "steps": len(plan["steps"]), "artifacts": len(artifact_rows)},
        )

        pending = {step["id"]: dict(step) for step in plan["steps"]}
        results: dict[str, dict[str, Any]] = {}
        upload_cache: dict[str, dict[str, Any]] = {}

        while pending:
            ready: list[dict[str, Any]] = []
            blocked: list[str] = []
            for step_id, step in pending.items():
                deps = step.get("depends_on") or []
                if any(dep in results and results[dep].get("status") != "completed" for dep in deps):
                    blocked.append(step_id)
                elif all(dep in results for dep in deps):
                    ready.append(step)

            for step_id in blocked:
                step = pending.pop(step_id)
                result = {
                    "id": step_id,
                    "target": step["target"],
                    "status": "skipped",
                    "error": "A dependency did not complete successfully.",
                }
                results[step_id] = result
                self.store.execute(
                    "UPDATE command_steps SET status='skipped',finished_at=?,error=? WHERE job_id=? AND step_id=?",
                    (utcnow(), result["error"], job_id, step_id),
                )

            if not ready:
                if pending:
                    # Cyclic or invalid dependency graph: fail closed rather than hang forever.
                    for step_id, step in list(pending.items()):
                        result = {
                            "id": step_id,
                            "target": step["target"],
                            "status": "failed",
                            "error": "Planner dependency graph could not make progress.",
                        }
                        results[step_id] = result
                        self.store.execute(
                            "UPDATE command_steps SET status='failed',finished_at=?,error=? WHERE job_id=? AND step_id=?",
                            (utcnow(), result["error"], job_id, step_id),
                        )
                        pending.pop(step_id, None)
                break

            batch = await asyncio.gather(
                *(self._run_step(job_id, step, artifact_rows, upload_cache) for step in ready)
            )
            for row in batch:
                results[row["id"]] = row
                pending.pop(row["id"], None)

        ordered = [results.get(step["id"], {"id": step["id"], "status": "unknown"}) for step in plan["steps"]]
        failed = any(row.get("status") in {"failed", "skipped"} for row in ordered)
        status = "partial" if failed and any(row.get("status") == "completed" for row in ordered) else "failed" if failed else "completed"
        response = {
            "ok": status == "completed",
            "job_id": job_id,
            "status": status,
            "planner": planner,
            "plan_summary": plan.get("summary"),
            "steps": ordered,
            "artifacts": [self.artifacts.public_view(x) for x in artifact_rows],
        }
        self.store.execute(
            "UPDATE command_jobs SET status=?,updated_at=?,result_json=?,error=? WHERE id=?",
            (
                status,
                utcnow(),
                json.dumps(response, ensure_ascii=False, default=str)[:100000],
                None if status == "completed" else "One or more steps failed.",
                job_id,
            ),
        )
        self.store.action(
            "universal-command-bus-v2",
            "job_finished",
            job_id,
            status,
            {"planner": planner, "steps": len(ordered), "failed": failed},
        )
        return response
