from manager.repair import patch_paths, validate_patch_paths


def test_valid_patch_path() -> None:
    patch = """diff --git a/src/app.py b/src/app.py
--- a/src/app.py
+++ b/src/app.py
@@ -1 +1 @@
-old
+new
"""
    assert patch_paths(patch) == ["src/app.py"]
    assert validate_patch_paths(patch) == []


def test_reject_env_patch() -> None:
    patch = """diff --git a/.env b/.env
--- a/.env
+++ b/.env
@@ -1 +1 @@
-A=1
+A=2
"""
    errors = validate_patch_paths(patch)
    assert errors
    assert "protected path" in errors[0]


def test_reject_parent_traversal() -> None:
    patch = """diff --git a/../outside.py b/../outside.py
--- a/../outside.py
+++ b/../outside.py
@@ -1 +1 @@
-old
+new
"""
    errors = validate_patch_paths(patch)
    assert errors
    assert "parent traversal" in errors[0]
