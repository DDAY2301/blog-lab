from __future__ import annotations

import base64
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import httpx


class GitOpsError(RuntimeError):
    pass


def _run(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = 180,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or proc.stdout or "")[-5000:]
        raise GitOpsError(f"{' '.join(argv[:4])} failed ({proc.returncode}): {stderr}")
    return proc


def repo_full_name(root: Path) -> str:
    url = _run(["git", "remote", "get-url", "origin"], cwd=root).stdout.strip()
    patterns = [
        r"github\.com[:/](?P<name>[^/\s]+/[^/\s]+?)(?:\.git)?$",
        r"api\.github\.com/repos/(?P<name>[^/\s]+/[^/\s]+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group("name").removesuffix(".git")
    raise GitOpsError(f"Could not determine GitHub owner/repo from origin: {url}")


def _auth_env() -> dict[str, str]:
    env = os.environ.copy()
    token = (
        os.getenv("AGENT_MANAGER_GITHUB_TOKEN", "").strip()
        or os.getenv("GH_TOKEN", "").strip()
        or os.getenv("GITHUB_TOKEN", "").strip()
    )
    if token:
        basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env["GIT_CONFIG_COUNT"] = "1"
        env["GIT_CONFIG_KEY_0"] = "http.extraHeader"
        env["GIT_CONFIG_VALUE_0"] = f"Authorization: Basic {basic}"
    return env


@dataclass
class Worktree:
    root: Path
    path: Path
    branch: str

    def cleanup(self) -> None:
        try:
            _run(["git", "worktree", "remove", "--force", str(self.path)], cwd=self.root)
        except Exception:
            shutil.rmtree(self.path, ignore_errors=True)


def create_worktree(root: Path, *, base_ref: str, branch: str) -> Worktree:
    if not (root / ".git").exists():
        raise GitOpsError(f"Not a git repository: {root}")

    _run(["git", "fetch", "origin", base_ref], cwd=root, timeout=180)
    tmp = Path(tempfile.mkdtemp(prefix="agent-manager-worktree-"))
    # git worktree add requires the destination not to pre-exist.
    shutil.rmtree(tmp)
    _run(
        ["git", "worktree", "add", "-b", branch, str(tmp), f"origin/{base_ref}"],
        cwd=root,
        timeout=180,
    )
    return Worktree(root=root, path=tmp, branch=branch)


def apply_patch(worktree: Path, patch: str) -> list[str]:
    patch_file = worktree / ".agent-manager.patch"
    patch_file.write_text(patch, encoding="utf-8")
    try:
        _run(["git", "apply", "--check", str(patch_file)], cwd=worktree)
        _run(["git", "apply", str(patch_file)], cwd=worktree)
    finally:
        patch_file.unlink(missing_ok=True)

    changed = _run(["git", "status", "--porcelain"], cwd=worktree).stdout.splitlines()
    paths: list[str] = []
    for line in changed:
        value = line[3:].strip()
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        if value:
            paths.append(value.replace("\\", "/"))
    return paths


def commit_and_push(worktree: Path, branch: str, message: str) -> str:
    _run(["git", "add", "-A"], cwd=worktree)
    status = _run(["git", "status", "--porcelain"], cwd=worktree).stdout.strip()
    if not status:
        raise GitOpsError("No changes remain to commit.")

    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "agent-manager[bot]")
    env.setdefault("GIT_AUTHOR_EMAIL", "agent-manager[bot]@users.noreply.github.com")
    env.setdefault("GIT_COMMITTER_NAME", env["GIT_AUTHOR_NAME"])
    env.setdefault("GIT_COMMITTER_EMAIL", env["GIT_AUTHOR_EMAIL"])
    _run(["git", "commit", "-m", message], cwd=worktree, env=env)

    sha = _run(["git", "rev-parse", "HEAD"], cwd=worktree).stdout.strip()
    _run(
        ["git", "push", "--set-upstream", "origin", branch],
        cwd=worktree,
        env=_auth_env(),
        timeout=240,
    )
    return sha


async def create_pull_request(
    *,
    repository: str,
    branch: str,
    base: str,
    title: str,
    body: str,
) -> str:
    token = (
        os.getenv("AGENT_MANAGER_GITHUB_TOKEN", "").strip()
        or os.getenv("GH_TOKEN", "").strip()
        or os.getenv("GITHUB_TOKEN", "").strip()
    )
    if token:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://api.github.com/repos/{repository}/pulls",
                headers=headers,
                json={
                    "title": title,
                    "head": branch,
                    "base": base,
                    "body": body,
                    "draft": False,
                },
            )
            if response.status_code >= 300:
                raise GitOpsError(
                    f"GitHub PR creation failed ({response.status_code}): {response.text[:1200]}"
                )
            return str(response.json().get("html_url") or "")

    if shutil.which("gh"):
        proc = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                repository,
                "--head",
                branch,
                "--base",
                base,
                "--title",
                title,
                "--body",
                body,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if proc.returncode != 0:
            raise GitOpsError(f"gh pr create failed: {(proc.stderr or proc.stdout)[-2000:]}")
        return proc.stdout.strip()

    raise GitOpsError(
        "No GitHub write credential available. Set AGENT_MANAGER_GITHUB_TOKEN "
        "or authenticate GitHub CLI with 'gh auth login'."
    )


def unique_branch(prefix: str = "agent-manager/repair") -> str:
    return f"{prefix}-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
