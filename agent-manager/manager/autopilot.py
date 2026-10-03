from __future__ import annotations

import os
from pathlib import Path

from .discovery import RepositoryScanner
from .evaluator import deterministic_health
from .gitops import (
    GitOpsError,
    apply_patch,
    commit_and_push,
    create_pull_request,
    create_worktree,
    repo_full_name,
    unique_branch,
)
from .models import AutopilotRequest, AutopilotResult, RepairPlanRequest
from .repair import RepairPlanner
from .test_runner import detect_test_commands, run_tests


class AutopilotDisabled(RuntimeError):
    pass


class AutonomousRepairExecutor:
    def __init__(self, planner: RepairPlanner | None = None) -> None:
        self.planner = planner or RepairPlanner()
        self.scanner = RepositoryScanner()

    @staticmethod
    def assert_write_enabled() -> None:
        enabled = os.getenv("AGENT_MANAGER_WRITE_ENABLED", "").strip().lower()
        if enabled not in {"1", "true", "yes", "on"}:
            raise AutopilotDisabled(
                "Autonomous writes are disabled. Set AGENT_MANAGER_WRITE_ENABLED=1 "
                "only on the trusted local Agent Manager host."
            )

    async def execute(self, request: AutopilotRequest) -> AutopilotResult:
        self.assert_write_enabled()

        root = Path(request.root).expanduser().resolve()
        if not (root / ".git").exists():
            raise ValueError(f"Not a git repository: {root}")

        baseline_snapshot = self.scanner.scan(root)
        baseline_health = deterministic_health(baseline_snapshot)

        plan = await self.planner.plan(
            RepairPlanRequest(root=str(root), objective=request.objective)
        )
        if not plan.valid:
            return AutopilotResult(
                ok=False,
                objective=request.objective,
                stage="plan",
                summary=plan.summary,
                baseline_score=baseline_health.score,
                validation_errors=plan.validation_errors or ["Repair planner produced no safe patch."],
            )

        branch = unique_branch()
        worktree = create_worktree(root, base_ref=request.base_branch, branch=branch)
        try:
            changed_files = apply_patch(worktree.path, plan.patch)
            if not changed_files:
                return AutopilotResult(
                    ok=False,
                    objective=request.objective,
                    stage="apply",
                    summary="Patch produced no changed files.",
                    branch=branch,
                    baseline_score=baseline_health.score,
                )

            commands = detect_test_commands(worktree.path, changed_files)
            results = run_tests(worktree.path, commands)
            tests_payload = [
                {
                    "name": item.name,
                    "argv": item.argv,
                    "cwd": item.cwd,
                    "returncode": item.returncode,
                    "passed": item.passed,
                    "stdout": item.stdout,
                    "stderr": item.stderr,
                }
                for item in results
            ]
            if not commands:
                return AutopilotResult(
                    ok=False,
                    objective=request.objective,
                    stage="tests",
                    summary="No reliable automated validation command could be detected.",
                    branch=branch,
                    changed_files=changed_files,
                    baseline_score=baseline_health.score,
                    tests=tests_payload,
                )
            if any(not item.passed for item in results):
                return AutopilotResult(
                    ok=False,
                    objective=request.objective,
                    stage="tests",
                    summary="Candidate repair failed automated validation.",
                    branch=branch,
                    changed_files=changed_files,
                    baseline_score=baseline_health.score,
                    tests=tests_payload,
                )

            candidate_snapshot = self.scanner.scan(worktree.path)
            candidate_health = deterministic_health(candidate_snapshot)
            if candidate_health.score < baseline_health.score:
                return AutopilotResult(
                    ok=False,
                    objective=request.objective,
                    stage="regression",
                    summary="Candidate repair reduced the deterministic health score.",
                    branch=branch,
                    changed_files=changed_files,
                    baseline_score=baseline_health.score,
                    candidate_score=candidate_health.score,
                    tests=tests_payload,
                )

            sha = commit_and_push(
                worktree.path,
                branch,
                f"Agent Manager: {request.objective[:120]}",
            )
            repository = repo_full_name(root)
            pr_url = await create_pull_request(
                repository=repository,
                branch=branch,
                base=request.base_branch,
                title=f"Agent Manager repair: {request.objective[:90]}",
                body=(
                    "Autonomous Agent Manager repair.\n\n"
                    f"Objective: {request.objective}\n\n"
                    f"Baseline health: {baseline_health.score}/100\n"
                    f"Candidate health: {candidate_health.score}/100\n"
                    f"Changed files: {', '.join(changed_files)}\n\n"
                    "The candidate was applied in an isolated git worktree and "
                    "all detected validation commands passed before this PR was opened. "
                    "This workflow intentionally does not merge directly into the protected base branch."
                ),
            )

            return AutopilotResult(
                ok=True,
                objective=request.objective,
                stage="pull_request",
                summary=plan.summary,
                branch=branch,
                commit_sha=sha,
                pull_request_url=pr_url,
                changed_files=changed_files,
                baseline_score=baseline_health.score,
                candidate_score=candidate_health.score,
                tests=tests_payload,
            )
        except GitOpsError as exc:
            return AutopilotResult(
                ok=False,
                objective=request.objective,
                stage="git",
                summary=str(exc),
                branch=branch,
                baseline_score=baseline_health.score,
            )
        finally:
            worktree.cleanup()
