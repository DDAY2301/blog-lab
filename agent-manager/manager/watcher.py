from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

from .autopilot import AutonomousRepairExecutor
from .gitops import repo_full_name
from .models import AutopilotRequest


def _run_gh(args: list[str], cwd: Path, timeout: int = 120) -> str:
    proc = subprocess.run(
        ["gh", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "gh failed")[-4000:])
    return proc.stdout


def _state_path() -> Path:
    raw = os.getenv("AGENT_MANAGER_WATCH_STATE", "").strip()
    if raw:
        return Path(raw).expanduser()
    return Path(__file__).resolve().parents[1] / "data" / "watcher.json"


def _load_processed() -> set[int]:
    path = _state_path()
    if not path.exists():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {int(x) for x in payload.get("processed_run_ids", [])}
    except Exception:
        return set()


def _save_processed(processed: set[int]) -> None:
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    values = sorted(processed)[-500:]
    path.write_text(
        json.dumps({"processed_run_ids": values}, indent=2) + "\n",
        encoding="utf-8",
    )


def list_failed_main_runs(root: Path, repository: str, base_branch: str) -> list[dict]:
    raw = _run_gh(
        [
            "run",
            "list",
            "--repo",
            repository,
            "--limit",
            "30",
            "--json",
            "databaseId,workflowName,status,conclusion,headBranch,event,createdAt,url",
        ],
        cwd=root,
    )
    rows = json.loads(raw)
    blocked = {
        "Agent Manager Autopilot",
    }
    out = []
    for row in rows:
        if row.get("status") != "completed" or row.get("conclusion") != "failure":
            continue
        if row.get("headBranch") != base_branch:
            continue
        if row.get("workflowName") in blocked:
            continue
        out.append(row)
    return out


def failed_log(root: Path, repository: str, run_id: int) -> str:
    return _run_gh(
        ["run", "view", str(run_id), "--repo", repository, "--log-failed"],
        cwd=root,
        timeout=180,
    )


def objective_from_failure(row: dict, log: str) -> str:
    clean = log[-3200:]
    return (
        f"Repair the persistent CI failure in workflow {row.get('workflowName')}. "
        "Identify the root cause from the failure log and make the smallest safe code change. "
        "Do not weaken tests or security checks merely to make CI green. "
        "Failure log follows:\n"
        + clean
    )[:3900]


async def watch_once(root: Path, base_branch: str = "main") -> list[dict]:
    repository = repo_full_name(root)
    processed = _load_processed()
    executor = AutonomousRepairExecutor()
    results: list[dict] = []

    for row in reversed(list_failed_main_runs(root, repository, base_branch)):
        run_id = int(row["databaseId"])
        if run_id in processed:
            continue

        try:
            log = failed_log(root, repository, run_id)
            objective = objective_from_failure(row, log)
            result = await executor.execute(
                AutopilotRequest(
                    root=str(root),
                    objective=objective,
                    base_branch=base_branch,
                )
            )
            results.append(
                {
                    "run_id": run_id,
                    "workflow": row.get("workflowName"),
                    "ok": result.ok,
                    "stage": result.stage,
                    "pull_request_url": result.pull_request_url,
                    "summary": result.summary,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "run_id": run_id,
                    "workflow": row.get("workflowName"),
                    "ok": False,
                    "stage": "watcher",
                    "summary": str(exc),
                }
            )
        finally:
            processed.add(run_id)
            _save_processed(processed)

    return results


async def main_async(root: Path, interval: int, once: bool) -> None:
    while True:
        try:
            results = await watch_once(root)
            for item in results:
                print(json.dumps(item, ensure_ascii=False))
        except Exception as exc:
            print(json.dumps({"ok": False, "stage": "watcher-loop", "error": str(exc)}))

        if once:
            return
        time.sleep(max(60, interval))


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent Manager autonomous GitHub failure watcher")
    parser.add_argument("--root", default="..", help="Local git repository root")
    parser.add_argument("--interval", type=int, default=300, help="Polling interval in seconds")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    AutonomousRepairExecutor.assert_write_enabled()

    import asyncio

    asyncio.run(
        main_async(
            Path(args.root).expanduser().resolve(),
            interval=args.interval,
            once=args.once,
        )
    )


if __name__ == "__main__":
    main()
