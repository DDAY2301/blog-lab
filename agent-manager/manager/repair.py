from __future__ import annotations

import json
import re
from pathlib import Path

from .discovery import IGNORED_DIRS, RepositoryScanner
from .evaluator import deterministic_health
from .models import RepairPlanRequest, RepairPlanResult
from .ollama_client import OllamaClient


PROTECTED_PREFIXES = (
    ".git/",
    ".env",
    "secrets/",
    "credentials/",
)

SAFE_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yml", ".yaml",
    ".md", ".txt", ".html", ".css", ".sh", ".ps1",
}


def patch_paths(patch: str) -> list[str]:
    paths: list[str] = []
    for line in patch.splitlines():
        if not line.startswith("+++ "):
            continue
        value = line[4:].strip()
        if value == "/dev/null":
            continue
        if value.startswith("b/"):
            value = value[2:]
        paths.append(value)
    return paths


def validate_patch_paths(patch: str) -> list[str]:
    errors: list[str] = []
    for value in patch_paths(patch):
        normalized = value.replace("\\", "/").lstrip("/")
        parts = Path(normalized).parts
        if ".." in parts:
            errors.append(f"parent traversal rejected: {value}")
            continue
        lower = normalized.lower()
        if any(lower == p.rstrip("/") or lower.startswith(p) for p in PROTECTED_PREFIXES):
            errors.append(f"protected path rejected: {value}")
    return errors


class RepairPlanner:
    def __init__(self, ollama: OllamaClient | None = None) -> None:
        self.ollama = ollama or OllamaClient()
        self.scanner = RepositoryScanner()

    def _candidate_files(self, root: Path, objective: str, limit: int = 24) -> list[Path]:
        words = {
            w.lower()
            for w in re.findall(r"[A-Za-z0-9_.-]{3,}", objective)
        }
        ranked: list[tuple[int, Path]] = []

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(root)
            if any(part in IGNORED_DIRS for part in rel.parts):
                continue
            if path.suffix.lower() not in SAFE_SUFFIXES:
                continue
            try:
                if path.stat().st_size > 80_000:
                    continue
            except OSError:
                continue

            rel_text = rel.as_posix().lower()
            score = 0
            if any(token in rel_text for token in ("agent", "prompt", "test", "workflow", "guardian", "heal")):
                score += 5
            if path.name.lower() in {"readme.md", "package.json", "requirements.txt", "pyproject.toml"}:
                score += 4
            score += sum(2 for word in words if word in rel_text)
            ranked.append((score, path))

        ranked.sort(key=lambda item: (-item[0], item[1].as_posix()))
        return [p for _, p in ranked[:limit]]

    def _context(self, root: Path, objective: str) -> str:
        blocks: list[str] = []
        total = 0
        for path in self._candidate_files(root, objective):
            rel = path.relative_to(root).as_posix()
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            text = text[:16_000]
            block = f"\n--- FILE: {rel} ---\n{text}\n"
            if total + len(block) > 120_000:
                break
            blocks.append(block)
            total += len(block)
        return "".join(blocks)

    async def plan(self, request: RepairPlanRequest) -> RepairPlanResult:
        root = Path(request.root).expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"Repository not found: {root}")

        snapshot = self.scanner.scan(root)
        health = deterministic_health(snapshot)
        context = self._context(root, request.objective)

        system = """You are a senior autonomous code-repair engineer.
Prepare the smallest safe patch for the requested objective.

Rules:
- Use ONLY the provided repository evidence.
- Do not touch secrets, .env files, credentials or .git.
- Prefer minimal changes over rewrites.
- Preserve existing behavior unless the objective requires a change.
- Add/update tests when appropriate.
- Return JSON only.
- The patch field must be a standard unified git diff suitable for git apply.
- If evidence is insufficient, return an empty patch and explain why.

Schema:
{
  "summary": "what should change",
  "plan": ["step 1", "step 2"],
  "patch": "diff --git ...",
  "tests": ["command"],
  "risk": "low|medium|high"
}
"""

        user = json.dumps(
            {
                "objective": request.objective,
                "repository": snapshot.model_dump(),
                "health": health.model_dump(),
                "selected_file_context": context,
            },
            ensure_ascii=False,
        )

        model, payload = await self.ollama.chat_json(system, user)
        patch = str(payload.get("patch", "") or "")
        errors = validate_patch_paths(patch)
        valid = bool(patch.strip()) and not errors

        return RepairPlanResult(
            model=model,
            objective=request.objective,
            summary=str(payload.get("summary", "")),
            plan=[str(x) for x in payload.get("plan", [])][:20],
            patch=patch,
            tests=[str(x) for x in payload.get("tests", [])][:20],
            risk=str(payload.get("risk", "high")),
            valid=valid,
            validation_errors=errors,
        )
