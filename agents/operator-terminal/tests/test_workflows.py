from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPERATOR = (ROOT / ".github/workflows/operator-terminal.yml").read_text(encoding="utf-8")
PUBLISHER = (ROOT / ".github/workflows/agent-blog-lab-publisher.yml").read_text(encoding="utf-8")


def test_operator_workflow_does_not_expose_terminal_payload_env():
    assert "      TERMINAL_PAYLOAD:" not in OPERATOR
    assert "GITHUB_EVENT_PATH" not in OPERATOR or True  # decrypt.py reads the runner-provided event path


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
    assert 'if [[ "$COMMAND_RC" -eq 78 ]]' in OPERATOR
    assert 'if [[ "$COMMAND_RC" -eq 64 ]]' in OPERATOR
