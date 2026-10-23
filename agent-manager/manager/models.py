from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


HealthStatus = Literal["healthy", "watch", "degraded", "critical"]


class RepoSnapshot(BaseModel):
    name: str
    root: str
    files: int = 0
    languages: dict[str, int] = Field(default_factory=dict)
    agent_paths: list[str] = Field(default_factory=list)
    workflow_files: list[str] = Field(default_factory=list)
    test_files: list[str] = Field(default_factory=list)
    prompt_files: list[str] = Field(default_factory=list)
    health_markers: list[str] = Field(default_factory=list)
    security_findings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class HealthReport(BaseModel):
    repo: str
    score: int = Field(ge=0, le=100)
    status: HealthStatus
    checks: dict[str, int] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)


class AIReview(BaseModel):
    model: str
    summary: str
    strengths: list[str] = Field(default_factory=list)
    problems: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    priority_actions: list[str] = Field(default_factory=list)
    raw: str | None = None


class ReviewResult(BaseModel):
    snapshot: RepoSnapshot
    health: HealthReport
    ai_review: AIReview | None = None


class ScanRequest(BaseModel):
    roots: list[str] = Field(default_factory=list)


class ReviewRequest(BaseModel):
    root: str
    use_ai: bool = True


class AgentRecord(BaseModel):
    id: str
    name: str
    root: str
    first_seen_at: str
    last_seen_at: str
    health_score: int = Field(ge=0, le=100)
    previous_score: int | None = Field(default=None, ge=0, le=100)
    status: HealthStatus
    languages: dict[str, int] = Field(default_factory=dict)
    agent_paths: list[str] = Field(default_factory=list)
    workflow_files: list[str] = Field(default_factory=list)
    prompt_files: list[str] = Field(default_factory=list)
    security_findings: list[str] = Field(default_factory=list)


class DiscoverResult(BaseModel):
    agents: list[AgentRecord] = Field(default_factory=list)
    errors: list[dict[str, str]] = Field(default_factory=list)


class RepairPlanRequest(BaseModel):
    root: str
    objective: str = Field(min_length=3, max_length=4000)


class RepairPlanResult(BaseModel):
    model: str
    objective: str
    summary: str
    plan: list[str] = Field(default_factory=list)
    patch: str = ""
    tests: list[str] = Field(default_factory=list)
    risk: str = "high"
    valid: bool = False
    validation_errors: list[str] = Field(default_factory=list)


class AutopilotRequest(BaseModel):
    root: str
    objective: str = Field(min_length=3, max_length=4000)
    base_branch: str = Field(default="main", min_length=1, max_length=200)


class AutopilotResult(BaseModel):
    ok: bool
    objective: str
    stage: str
    summary: str = ""
    branch: str | None = None
    commit_sha: str | None = None
    pull_request_url: str | None = None
    changed_files: list[str] = Field(default_factory=list)
    baseline_score: int | None = Field(default=None, ge=0, le=100)
    candidate_score: int | None = Field(default=None, ge=0, le=100)
    tests: list[dict[str, Any]] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)
