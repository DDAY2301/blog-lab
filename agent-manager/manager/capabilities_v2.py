from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse

from .db_v3 import StoreV3, utcnow


@dataclass(frozen=True)
class AgentCapability:
    id: str
    name: str
    description: str
    capabilities: tuple[str, ...]
    artifact_support: tuple[str, ...]
    command_examples: tuple[str, ...]
    max_parallel: int = 1
    dispatch_kind: str = "builtin"
    command_url: str = ""
    token_env: str = ""
    token_header: str = "authorization"
    token_prefix: str = "Bearer "

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class CapabilityRegistryV2:
    """Extensible capability manifest used by the natural-language planner."""

    def __init__(self, store: StoreV3 | None = None) -> None:
        self.store = store
        self._builtin: dict[str, AgentCapability] = {
            "manager": AgentCapability(
                id="manager",
                name="Agent Manager V4",
                description="Fleet orchestration plus evidence-based code review, repair planning, test-driven coder-fix and safe PR creation.",
                capabilities=(
                    "fleet.status",
                    "fleet.health",
                    "fleet.maintenance",
                    "fleet.self_heal",
                    "fleet.incidents",
                    "fleet.providers",
                    "fleet.agent_check",
                    "service.restart",
                    "code.review",
                    "code.repair.plan",
                    "code.repair.autopilot",
                    "code.test_fix",
                    "git.worktree",
                    "git.pull_request",
                ),
                artifact_support=("text/*", "application/json"),
                command_examples=(
                    "preveri vse agente",
                    "preglej in popravi",
                    "pokaži incidente",
                    "status",
                    "programer plan za BlogLab: popravi ...",
                    "coder fix Project Visibility: popravi ...",
                    "preglej kodo in pripravi varen patch",
                ),
                max_parallel=1,
            ),
            "project_visibility": AgentCapability(
                id="project_visibility",
                name="Project Visibility",
                description="Local website production agent with preflight, QA, model routing, queue and autonomous supervisor.",
                capabilities=(
                    "website.preflight",
                    "website.qa",
                    "website.models",
                    "website.capabilities",
                    "website.queue",
                    "website.self_heal",
                ),
                artifact_support=("text/plain", "text/markdown", "application/json"),
                command_examples=(
                    "preflight",
                    "preglej in popravi",
                    "capabilities",
                    "queue",
                ),
                max_parallel=1,
            ),
            "bloglab": AgentCapability(
                id="bloglab",
                name="BlogLab",
                description="Blog content, publishing, live site editing, media upload and BlogLab agent control.",
                capabilities=(
                    "blog.article.create",
                    "blog.article.edit",
                    "blog.article.publish",
                    "blog.media.upload",
                    "blog.site.edit",
                    "blog.site.qa",
                    "blog.publisher.control",
                    "blog.status",
                ),
                artifact_support=("image/jpeg", "image/png", "image/webp", "image/gif", "text/*"),
                command_examples=(
                    "objavi članek o ...",
                    "dodaj članek s priloženo sliko",
                    "uredi stran",
                    "preveri objave",
                ),
                max_parallel=2,
            ),
        }

    def _dynamic(self) -> dict[str, AgentCapability]:
        if not self.store:
            return {}
        rows = self.store.query(
            "SELECT * FROM agent_capabilities WHERE enabled=1 ORDER BY id"
        )
        out: dict[str, AgentCapability] = {}
        for row in rows:
            try:
                out[str(row["id"])] = AgentCapability(
                    id=str(row["id"]),
                    name=str(row["name"]),
                    description=str(row["description"]),
                    capabilities=tuple(json.loads(row.get("capabilities") or "[]")),
                    artifact_support=tuple(json.loads(row.get("artifact_support") or "[]")),
                    command_examples=tuple(json.loads(row.get("command_examples") or "[]")),
                    max_parallel=max(1, min(8, int(row.get("max_parallel") or 1))),
                    dispatch_kind=str(row.get("dispatch_kind") or "http"),
                    command_url=str(row.get("command_url") or ""),
                    token_env=str(row.get("token_env") or ""),
                    token_header=str(row.get("token_header") or "authorization"),
                    token_prefix=str(row.get("token_prefix") or "Bearer "),
                )
            except Exception:
                continue
        return out

    def all(self) -> dict[str, AgentCapability]:
        merged = dict(self._builtin)
        merged.update(self._dynamic())
        return merged

    def get(self, target: str) -> AgentCapability | None:
        return self.all().get(str(target or "").strip().lower())

    def targets(self) -> list[str]:
        return list(self.all())

    def manifest(self) -> dict[str, dict[str, Any]]:
        return {key: item.as_dict() for key, item in self.all().items()}

    def planner_text(self) -> str:
        rows: list[str] = []
        for item in self.all().values():
            rows.append(
                f"- {item.id}: {item.description} "
                f"Capabilities={','.join(item.capabilities)} "
                f"Artifacts={','.join(item.artifact_support)}"
            )
        return "\n".join(rows)

    @staticmethod
    def _valid_http_target(url: str) -> bool:
        parsed = urlparse(str(url or "").strip())
        if parsed.scheme not in {"http", "https"}:
            return False
        host = (parsed.hostname or "").lower()
        if not host:
            return False
        if parsed.scheme == "http" and host not in {"127.0.0.1", "::1", "localhost"}:
            return False
        return True

    def save_dynamic(self, payload: dict[str, Any]) -> AgentCapability:
        if not self.store:
            raise RuntimeError("Capability registry persistence is unavailable.")
        target_id = str(payload.get("id") or "").strip().lower()
        if not target_id or not target_id.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Capability id must be alphanumeric with optional - or _.")
        if target_id in self._builtin:
            raise ValueError("Built-in capability records cannot be overwritten.")

        dispatch_kind = str(payload.get("dispatch_kind") or "http").strip().lower()
        if dispatch_kind != "http":
            raise ValueError("Dynamic agents currently support dispatch_kind=http only.")
        command_url = str(payload.get("command_url") or "").strip()
        if not self._valid_http_target(command_url):
            raise ValueError("Dynamic command_url must be HTTPS or loopback HTTP.")

        item = AgentCapability(
            id=target_id,
            name=str(payload.get("name") or target_id).strip()[:120],
            description=str(payload.get("description") or "").strip()[:1000],
            capabilities=tuple(str(x).strip()[:120] for x in payload.get("capabilities") or [] if str(x).strip()),
            artifact_support=tuple(str(x).strip()[:120] for x in payload.get("artifact_support") or [] if str(x).strip()),
            command_examples=tuple(str(x).strip()[:300] for x in payload.get("command_examples") or [] if str(x).strip()),
            max_parallel=max(1, min(8, int(payload.get("max_parallel") or 1))),
            dispatch_kind="http",
            command_url=command_url,
            token_env=str(payload.get("token_env") or "").strip()[:120],
            token_header=str(payload.get("token_header") or "authorization").strip().lower()[:120],
            token_prefix=str(payload.get("token_prefix") if payload.get("token_prefix") is not None else "Bearer ")[:40],
        )
        self.store.execute(
            """
            INSERT INTO agent_capabilities(
              id,name,description,capabilities,artifact_support,command_examples,max_parallel,
              dispatch_kind,command_url,token_env,token_header,token_prefix,enabled,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1,?)
            ON CONFLICT(id) DO UPDATE SET
              name=excluded.name,
              description=excluded.description,
              capabilities=excluded.capabilities,
              artifact_support=excluded.artifact_support,
              command_examples=excluded.command_examples,
              max_parallel=excluded.max_parallel,
              dispatch_kind=excluded.dispatch_kind,
              command_url=excluded.command_url,
              token_env=excluded.token_env,
              token_header=excluded.token_header,
              token_prefix=excluded.token_prefix,
              enabled=1,
              updated_at=excluded.updated_at
            """,
            (
                item.id,
                item.name,
                item.description,
                json.dumps(list(item.capabilities), ensure_ascii=False),
                json.dumps(list(item.artifact_support), ensure_ascii=False),
                json.dumps(list(item.command_examples), ensure_ascii=False),
                item.max_parallel,
                item.dispatch_kind,
                item.command_url,
                item.token_env,
                item.token_header,
                item.token_prefix,
                utcnow(),
            ),
        )
        return item

    def disable_dynamic(self, target_id: str) -> bool:
        if not self.store:
            return False
        rows = self.store.query("SELECT id FROM agent_capabilities WHERE id=?", (target_id,))
        if not rows:
            return False
        self.store.execute(
            "UPDATE agent_capabilities SET enabled=0,updated_at=? WHERE id=?",
            (utcnow(), target_id),
        )
        return True
