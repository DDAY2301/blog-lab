from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class AgentCapability:
    id: str
    name: str
    description: str
    capabilities: tuple[str, ...]
    artifact_support: tuple[str, ...]
    command_examples: tuple[str, ...]
    max_parallel: int = 1

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class CapabilityRegistryV2:
    """Extensible manifest used by the planner instead of hard-coded one-command routing."""

    def __init__(self) -> None:
        self._items: dict[str, AgentCapability] = {
            "manager": AgentCapability(
                id="manager",
                name="Agent Manager V4",
                description="Fleet health, maintenance, incidents, providers, self-heal and orchestration.",
                capabilities=(
                    "fleet.status",
                    "fleet.health",
                    "fleet.maintenance",
                    "fleet.self_heal",
                    "fleet.incidents",
                    "fleet.providers",
                    "fleet.agent_check",
                    "service.restart",
                ),
                artifact_support=("text/*", "application/json"),
                command_examples=(
                    "preveri vse agente",
                    "preglej in popravi",
                    "pokaži incidente",
                    "status",
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

    def get(self, target: str) -> AgentCapability | None:
        return self._items.get(str(target or "").strip().lower())

    def targets(self) -> list[str]:
        return list(self._items)

    def manifest(self) -> dict[str, dict[str, Any]]:
        return {key: item.as_dict() for key, item in self._items.items()}

    def planner_text(self) -> str:
        rows: list[str] = []
        for item in self._items.values():
            rows.append(
                f"- {item.id}: {item.description} "
                f"Capabilities={','.join(item.capabilities)} "
                f"Artifacts={','.join(item.artifact_support)}"
            )
        return "\n".join(rows)
