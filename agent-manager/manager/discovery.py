from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path

from .models import RepoSnapshot


IGNORED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".next",
    ".wrangler",
}

LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript-react",
    ".ts": "typescript",
    ".tsx": "typescript-react",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".md": "markdown",
    ".sh": "shell",
    ".ps1": "powershell",
}

PROMPT_NAMES = {
    "agents.md",
    "system.md",
    "system_prompt.md",
    "prompt.md",
    "prompts.md",
    "instructions.md",
}

SECRET_PATTERNS = (
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}", re.I),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}", re.I),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}", re.I),
)


class RepositoryScanner:
    def __init__(self) -> None:
        self.max_files = int(os.getenv("AGENT_MANAGER_MAX_FILES", "4000"))
        self.max_file_bytes = int(os.getenv("AGENT_MANAGER_MAX_FILE_BYTES", "300000"))

    def scan(self, root: str | Path) -> RepoSnapshot:
        root_path = Path(root).expanduser().resolve()
        if not root_path.exists():
            raise FileNotFoundError(str(root_path))
        if not root_path.is_dir():
            raise NotADirectoryError(str(root_path))

        language_counter: Counter[str] = Counter()
        agent_paths: set[str] = set()
        workflow_files: list[str] = []
        test_files: list[str] = []
        prompt_files: list[str] = []
        health_markers: set[str] = set()
        security_findings: list[str] = []
        notes: list[str] = []
        seen = 0

        for path in root_path.rglob("*"):
            if seen >= self.max_files:
                notes.append(f"scan truncated at {self.max_files} files")
                break
            if not path.is_file():
                continue
            rel = path.relative_to(root_path)
            if any(part in IGNORED_DIRS for part in rel.parts):
                continue

            seen += 1
            suffix = path.suffix.lower()
            language = LANGUAGE_BY_SUFFIX.get(suffix)
            if language:
                language_counter[language] += 1

            rel_posix = rel.as_posix()
            lower = rel_posix.lower()

            if any(part.lower() in {"agent", "agents"} for part in rel.parts[:-1]):
                if len(rel.parts) > 1:
                    idx = next(
                        (i for i, p in enumerate(rel.parts) if p.lower() in {"agent", "agents"}),
                        0,
                    )
                    if idx + 1 < len(rel.parts):
                        agent_paths.add("/".join(rel.parts[: idx + 2]))

            if lower.startswith(".github/workflows/") and suffix in {".yml", ".yaml"}:
                workflow_files.append(rel_posix)

            if (
                "/tests/" in f"/{lower}"
                or path.name.lower().startswith("test_")
                or path.name.lower().endswith(".test.js")
                or path.name.lower().endswith(".test.ts")
            ):
                test_files.append(rel_posix)

            if path.name.lower() in PROMPT_NAMES or "prompt" in path.name.lower():
                if suffix in {".md", ".txt", ".py", ".json", ".yaml", ".yml"}:
                    prompt_files.append(rel_posix)

            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size > self.max_file_bytes:
                continue

            if suffix not in {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yml", ".yaml", ".md", ".txt"}:
                continue

            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            low_text = text.lower()
            for marker in ("/health", "healthcheck", "self-heal", "self_heal", "guardian"):
                if marker in low_text:
                    health_markers.add(marker)

            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    security_findings.append(
                        f"credential-like value detected in {rel_posix}"
                    )
                    break

        if not (root_path / "README.md").exists() and not (root_path / "readme.md").exists():
            notes.append("README missing")

        return RepoSnapshot(
            name=root_path.name,
            root=str(root_path),
            files=seen,
            languages=dict(language_counter.most_common()),
            agent_paths=sorted(agent_paths),
            workflow_files=sorted(workflow_files),
            test_files=sorted(test_files),
            prompt_files=sorted(prompt_files),
            health_markers=sorted(health_markers),
            security_findings=sorted(set(security_findings)),
            notes=notes,
        )
