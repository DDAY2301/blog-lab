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


MAX_CODER_FIX_ATTEMPTS = max(
    0,
    min(3, int(os.getenv("AGENT_MANAGER_CODER_FIX_ATTEMPTS", "2"))),
)


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
            if not commands:
                return AutopilotResult(
                    ok=False,
                    objective=request.objective,
                    stage="tests",
                    summary="No reliable automated validation command could be detected.",
                    branch=branch,
                    changed_files=changed_files,
                    baseline_score=baseline_health.score,
                    tests=[],
                )

            all_test_runs: list[dict] = []
            results = run_tests(worktree.path, commands)

            def record_test_run(attempt: int, rows) -> None:
                for item in rows:
                    all_test_runs.append(
                        {
                            "attempt": attempt,
                            "name": item.name,
                            "argv": item.argv,
                            "cwd": item.cwd,
                            "returncode": item.returncode,
                            "passed": item.passed,
                            "stdout": item.stdout,
                            "stderr": item.stderr,
                        }
                    )

            record_test_run(0, results)
            fix_validation_errors: list[str] = []

            for fix_attempt in range(1, MAX_CODER_FIX_ATTEMPTS + 1):
                if all(item.passed for item in results):
                    break

                failures = [
                    {
                        "name": item.name,
                        "argv": item.argv,
                        "cwd": item.cwd,
                        "returncode": item.returncode,
                        "stdout": item.stdout,
                        "stderr": item.stderr,
                    }
                    for item in results
                    if not item.passed
                ]
                fix_plan = await self.planner.fix_failed_candidate(
                    root=worktree.path,
                    objective=request.objective,
                    failures=failures,
                    changed_files=changed_files,
                    attempt=fix_attempt,
                )
                if not fix_plan.valid:
                    fix_validation_errors.extend(
                        fix_plan.validation_errors
                        or [f"Coder-fix attempt {fix_attempt} produced no safe incremental patch."]
                    )
                    break

                incremental_files = apply_patch(worktree.path, fix_plan.patch)
                if not incremental_files:
                    fix_validation_errors.append(
                        f"Coder-fix attempt {fix_attempt} produced no changed files."
                    )
                    break

                changed_files = sorted(set(changed_files) | set(incremental_files))
                commands = detect_test_commands(worktree.path, changed_files)
                if not commands:
                    fix_validation_errors.append(
                        f"Coder-fix attempt {fix_attempt} left no detectable validation commands."
                    )
                    break
                results = run_tests(worktree.path, commands)
                record_test_run(fix_attempt, results)

            if any(not item.passed for item in results):
                return AutopilotResult(
                    ok=False,
                    objective=request.objective,
                    stage="tests",
                    summary=(
                        "Candidate repair still failed automated validation after "
                        f"{min(MAX_CODER_FIX_ATTEMPTS, max((x.get('attempt', 0) for x in all_test_runs), default=0))} "
                        "bounded coder-fix attempt(s)."
                    ),
                    branch=branch,
                    changed_files=changed_files,
                    baseline_score=baseline_health.score,
                    tests=all_test_runs,
                    validation_errors=fix_validation_errors,
                )

            tests_payload = all_test_runs
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
