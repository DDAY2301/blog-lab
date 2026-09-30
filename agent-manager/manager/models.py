from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


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
    status: Literal["healthy", "watch", "degraded", "critical"]
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
