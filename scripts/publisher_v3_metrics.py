"""Publisher V3 measurement: article output, fallback QA and sampled GitHub workflow use."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r'(?m)^  \{\s*\n\s*(?:"id"|id):\s*"([^"]+)"')


def ids_in_app(value: str) -> set[str]:
    return set(ID.findall(value))


def outcome_from_text(before: str, after: str, failed: list[dict] | None = None) -> dict:
    added = sorted(ids_in_app(after) - ids_in_app(before))
    reasons, rejections = Counter(), 0
    for row in failed or []:
        for attempt in row.get("attempts") or [{"errors": row.get("errors") or []}]:
            rejections += 1
            reasons.update(str(x) for x in attempt.get("errors") or [])
    return dict(published_count=len(added), new_article_ids=added,
                outcome="published" if added else "no_article",
                qa_rejected_attempts_observed=rejections,
                qa_reasons_observed=dict(reasons))


def publisher_report() -> dict:
    before = subprocess.run(
        ["git", "show", "HEAD:src/App.jsx"], cwd=ROOT, check=True,
        capture_output=True, text=True, encoding="utf-8",
    ).stdout
    after = (ROOT / "src/App.jsx").read_text(encoding="utf-8")
    try:
        started = float(os.getenv("PUBLISHER_V3_START_EPOCH") or 0)
    except ValueError:
        started = 0
    failures = []
    if started:
        for p in (ROOT / "logs").glob("fallback-failed-*.json"):
            if p.stat().st_mtime < started - 2:
                continue
            try:
                failures.append(json.loads(p.read_text(encoding="utf-8")))
            except (ValueError, OSError):
                continue
    result = outcome_from_text(before, after, failures)
    # V4: count new atomic JSON articles before the verified commit.
    atomic_dir = ROOT / "src" / "articles" / "published"
    tracked_paths = set(subprocess.run(
        ["git", "ls-files", "--", "src/articles/published"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.splitlines())
    new_ids = set(result["new_article_ids"])
    if atomic_dir.is_dir():
        for path in atomic_dir.glob("*.json"):
            relative = path.relative_to(ROOT).as_posix()
            if relative in tracked_paths:
                continue
            record = json.loads(path.read_text(encoding="utf-8"))
            if record.get("id") != path.stem:
                raise RuntimeError(f"Atomic publication ID mismatch: {relative}")
            new_ids.add(path.stem)
    result["new_article_ids"] = sorted(new_ids)
    result["published_count"] = len(new_ids)
    result["outcome"] = "published" if new_ids else "no_article"
    result.update(schema="bloglab.publisher.v3",
                  github_run_id=os.getenv("GITHUB_RUN_ID", ""),
                  category=os.getenv("PUBLISHER_CATEGORY", ""),
                  slot=os.getenv("PUBLISHER_SLOT", ""),
                  qa_scope="new fallback diagnostic files only; primary writer QA unmeasured")
    return result


def _date(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def summarize_workflows(runs: list[dict], total: int, complete: bool) -> dict:
    groups = defaultdict(lambda: dict(runs=0, success=0, failure=0, cancelled=0, other=0, wall_minutes=0.0))
    for item in runs:
        row = groups[str(item.get("name") or "unknown")]
        row["runs"] += 1
        outcome = item.get("conclusion")
        row[outcome if outcome in ("success", "failure", "cancelled") else "other"] += 1
        start = _date(item.get("run_started_at") or item.get("created_at") or "")
        end = _date(item.get("updated_at") or "")
        if start and end and end >= start:
            row["wall_minutes"] += (end - start).total_seconds() / 60
    for row in groups.values():
        row["wall_minutes"] = round(row["wall_minutes"], 1)
    return dict(schema="bloglab.workflow-budget.v3", observed=len(runs),
                api_day_total=total, pagination_complete=complete,
                note="Wall time is NOT billable GitHub/Cloudflare build minutes; sample may be incomplete.",
                workflows=dict(sorted(groups.items())))


def usage_report(repo: str, hours: int = 24) -> dict:
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Missing read-only GitHub Actions token")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Unsafe repository")
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    runs, total = [], 0
    for page in (1, 2, 3):
        query = urlencode({"created": ">=" + since.date().isoformat(), "per_page": 100, "page": page})
        request = Request(
            f"https://api.github.com/repos/{repo}/actions/runs?{query}",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                     "User-Agent": "BlogLab-V3-Budget"},
        )
        with urlopen(request, timeout=25) as response:
            payload = json.load(response)
        total = int(payload.get("total_count") or 0)
        batch = payload.get("workflow_runs") or []
        runs.extend(batch)
        if len(batch) < 100 or len(runs) >= total:
            break
    recent = [r for r in runs if (_date(r.get("created_at") or "") or datetime.min.replace(tzinfo=timezone.utc)) >= since]
    return summarize_workflows(recent, total, len(runs) >= total)


def emit(report: dict, name: str) -> None:
    target = Path(os.getenv("RUNNER_TEMP") or "/tmp") / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    if summary := os.getenv("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as output:
            output.write("### BlogLab V3 metrics\n")
            output.write("Recorded data (publication outcome or workflow sample):\n")
            output.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["publisher", "usage"])
    args = parser.parse_args()
    if args.mode == "publisher":
        emit(publisher_report(), "publisher-v3-outcome.json")
    else:
        emit(usage_report(os.getenv("GITHUB_REPOSITORY", "DDAY2301/blog-lab")), "workflow-budget-v3.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
