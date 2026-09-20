from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPERATOR = (ROOT / ".github/workflows/operator-terminal.yml").read_text(encoding="utf-8")
PUBLISHER = (ROOT / ".github/workflows/agent-blog-lab-publisher.yml").read_text(encoding="utf-8")
LIVE = (ROOT / ".github/workflows/live-feed.yml").read_text(encoding="utf-8")


def test_operator_workflow_does_not_expose_terminal_payload_env():
    assert "      TERMINAL_PAYLOAD:" not in OPERATOR


def test_operator_staging_handles_optional_paths_safely():
    assert "git add -A -- src public data" in OPERATOR
    assert "for optional_path in content/drafts logs" in OPERATOR
    assert "Repository changed, but no permitted changes were staged." in OPERATOR
    assert "content/drafts logs 2>/dev/null || true" not in OPERATOR


def test_publisher_staging_handles_optional_paths_safely():
    assert "git add -A -- src/App.jsx data public/data" in PUBLISHER
    assert "for optional_path in content/drafts logs" in PUBLISHER
    assert "Agent produced repository changes, but no allowed changes were staged." in PUBLISHER
    assert "content/drafts logs 2>/dev/null || true" not in PUBLISHER


def test_permanent_operator_errors_do_not_retry():
    assert 'if [[ "$COMMAND_RC" -eq 64 ]]' in OPERATOR
    assert 'if [[ "$COMMAND_RC" -eq 78 ]]' not in OPERATOR
    assert "@github/copilot" not in OPERATOR


def test_operator_and_publisher_sync_with_latest_main():
    for workflow in (OPERATOR, PUBLISHER):
        assert "name: Sync latest main" in workflow
        assert "git fetch origin main" in workflow
        assert "git checkout -B main origin/main" in workflow
        assert "git pull --rebase origin main" in workflow
        assert "git push origin HEAD:main" in workflow


def test_deploying_workflows_build_after_final_sync():
    assert "name: Final synchronized public build" in OPERATOR
    assert "name: Final synchronized article build" in PUBLISHER
    assert "name: Sync latest main" in LIVE
    assert "name: Build final synchronized site" in LIVE
    assert "git pull --rebase origin main" in LIVE


def test_publisher_has_heartbeat_catchup_scheduler():
    assert 'cron: "7,22,37,52 * * * *"' in PUBLISHER
    assert "agents/blog-lab-publisher/schedule.py --github-output" in PUBLISHER
    assert "scheduled-slot" in PUBLISHER
    assert "needs.plan.outputs.slot" in PUBLISHER


def test_publisher_no_longer_relies_on_runtime_dst_filter():
    assert 'OFFSET="$(TZ=Europe/Ljubljana date +%z)"' not in PUBLISHER
    assert 'schedule=$EVENT_SCHEDULE run=$RUN' not in PUBLISHER
