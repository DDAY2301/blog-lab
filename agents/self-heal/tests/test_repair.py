import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import repair


def test_safe_relpath_rejects_protected_path(tmp_path, monkeypatch):
    monkeypatch.setattr(repair, "BASE", tmp_path)
    with pytest.raises(repair.RepairError):
        repair._safe_relpath(".github/workflows/x.yml", allow_create=True)


def test_safe_relpath_allows_worker_source(tmp_path, monkeypatch):
    monkeypatch.setattr(repair, "BASE", tmp_path)
    path = tmp_path / "terminal/worker/src/index.js"
    path.parent.mkdir(parents=True)
    path.write_text("export default {}", encoding="utf-8")
    assert repair._safe_relpath("terminal/worker/src/index.js") == "terminal/worker/src/index.js"


def test_targeted_replace_requires_unique_match():
    with pytest.raises(repair.RepairError, match="ambiguous"):
        repair._replace_targeted("x=1\nx=1\n", "x=1", "x=2", {}, "src/x.js")


def test_targeted_replace_supports_occurrence():
    value = repair._replace_targeted(
        "x=1\nx=1\n",
        "x=1",
        "x=2",
        {"occurrence": 2},
        "src/x.js",
    )
    assert value == "x=1\nx=2\n"


def test_apply_plan_and_rollback(tmp_path, monkeypatch):
    monkeypatch.setattr(repair, "BASE", tmp_path)
    path = tmp_path / "src/App.jsx"
    path.parent.mkdir(parents=True)
    path.write_text("const value = 'old';\n", encoding="utf-8")
    context = [{"path": "src/App.jsx", "complete": True, "content": path.read_text()}]
    changed, original = repair.apply_plan({
        "edits": [{
            "path": "src/App.jsx",
            "action": "replace",
            "old": "'old'",
            "new": "'new'",
        }]
    }, context)
    assert changed == 1
    assert "'new'" in path.read_text(encoding="utf-8")
    repair.rollback(original)
    assert path.read_text(encoding="utf-8") == "const value = 'old';\n"


def test_apply_plan_rejects_secret_like_material(tmp_path, monkeypatch):
    monkeypatch.setattr(repair, "BASE", tmp_path)
    path = tmp_path / "src/App.jsx"
    path.parent.mkdir(parents=True)
    path.write_text("const x = 1;\n", encoding="utf-8")
    context = [{"path": "src/App.jsx", "complete": True, "content": path.read_text()}]
    with pytest.raises(repair.RepairError, match="credential-like"):
        repair.apply_plan({
            "edits": [{
                "path": "src/App.jsx",
                "action": "replace",
                "old": "1",
                "new": "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
            }]
        }, context)


def test_context_prefers_file_from_diagnostic(tmp_path, monkeypatch):
    monkeypatch.setattr(repair, "BASE", tmp_path)
    for rel, content in {
        "src/App.jsx": "APP\n",
        "src/styles.css": "CSS\n",
        "terminal/worker/src/index.js": "WORKER\n",
        "agents/blog-lab-publisher/agent.py": "AGENT\n",
        "package.json": "{}\n",
        "wrangler.jsonc": "{}\n",
    }.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    context = repair.build_context("Build failed in src/styles.css:12")
    assert context[0]["path"] == "src/styles.css"
