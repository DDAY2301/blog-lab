from __future__ import annotations

import json

from .models import AIReview, HealthReport, RepoSnapshot
from .ollama_client import OllamaClient


def deterministic_health(snapshot: RepoSnapshot) -> HealthReport:
    checks: dict[str, int] = {}
    findings: list[str] = []

    checks["tests"] = 20 if snapshot.test_files else 0
    if not snapshot.test_files:
        findings.append("No automated tests detected.")

    checks["ci_workflows"] = 15 if snapshot.workflow_files else 0
    if not snapshot.workflow_files:
        findings.append("No GitHub Actions workflow detected.")

    checks["health_recovery"] = 15 if snapshot.health_markers else 0
    if not snapshot.health_markers:
        findings.append("No health/self-heal/guardian marker detected.")

    checks["agent_structure"] = 15 if snapshot.agent_paths else 5
    if not snapshot.agent_paths:
        findings.append("No explicit agent/agents directory detected.")

    checks["prompt_governance"] = 10 if snapshot.prompt_files else 3
    if not snapshot.prompt_files:
        findings.append("No obvious prompt/instruction files detected.")

    checks["documentation"] = 10 if "README missing" not in snapshot.notes else 0
    if "README missing" in snapshot.notes:
        findings.append("README is missing.")

    if snapshot.security_findings:
        checks["security"] = 0
        findings.extend(snapshot.security_findings)
    else:
        checks["security"] = 15

    score = max(0, min(100, sum(checks.values())))
    if score >= 85:
        status = "healthy"
    elif score >= 70:
        status = "watch"
    elif score >= 50:
        status = "degraded"
    else:
        status = "critical"

    return HealthReport(
        repo=snapshot.name,
        score=score,
        status=status,
        checks=checks,
        findings=findings,
    )


class AgentEvaluator:
    def __init__(self, ollama: OllamaClient | None = None) -> None:
        self.ollama = ollama or OllamaClient()

    async def ai_review(self, snapshot: RepoSnapshot, health: HealthReport) -> AIReview:
        system = """You are Agent Manager, a senior AI systems engineer.
Review an AI-agent repository for reliability, autonomy, maintainability, testing,
security, prompt quality, recovery behavior and cost efficiency.

Important rules:
- Do not invent files or capabilities.
- Prefer local/open-source/free solutions.
- Do not recommend paid APIs when a local option exists.
- Separate problems from optional improvements.
- Return valid JSON only.

JSON schema:
{
  "summary": "short summary",
  "strengths": ["..."],
  "problems": ["..."],
  "improvements": ["..."],
  "priority_actions": ["P0 ...", "P1 ..."]
}
"""

        user = json.dumps(
            {
                "snapshot": snapshot.model_dump(),
                "health": health.model_dump(),
            },
            ensure_ascii=False,
            indent=2,
        )

        model, payload = await self.ollama.chat_json(system, user)
        return AIReview(
            model=model,
            summary=str(payload.get("summary", "")),
            strengths=[str(x) for x in payload.get("strengths", [])][:12],
            problems=[str(x) for x in payload.get("problems", [])][:12],
            improvements=[str(x) for x in payload.get("improvements", [])][:12],
            priority_actions=[str(x) for x in payload.get("priority_actions", [])][:12],
            raw=None,
        )
