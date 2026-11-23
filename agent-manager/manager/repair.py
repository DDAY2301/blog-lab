from __future__ import annotations

import json
import re
from pathlib import Path

from .discovery import IGNORED_DIRS, RepositoryScanner
from .evaluator import deterministic_health
from .coder_prompt_v1 import (
    CODER_FIX_PROMPT,
    CODER_FIX_VERSION,
    PROGRAMMER_WORKFLOW_PROMPT,
    PROGRAMMER_WORKFLOW_VERSION,
    coder_fix_prompt_digest,
    programmer_prompt_digest,
)
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

    def _context(
        self,
        root: Path,
        objective: str,
        preferred: list[str] | None = None,
    ) -> str:
        blocks: list[str] = []
        total = 0
        ordered: list[Path] = []
        seen: set[str] = set()

        for rel_text in preferred or []:
            rel = Path(str(rel_text).replace("\\", "/"))
            candidate = (root / rel).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                continue
            if not candidate.is_file() or candidate.suffix.lower() not in SAFE_SUFFIXES:
                continue
            key = candidate.as_posix().lower()
            if key not in seen:
                ordered.append(candidate)
                seen.add(key)

        for path in self._candidate_files(root, objective):
            key = path.resolve().as_posix().lower()
            if key in seen:
                continue
            ordered.append(path)
            seen.add(key)

        for path in ordered:
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

        system = PROGRAMMER_WORKFLOW_PROMPT

        user = json.dumps(
            {
                "prompt_version": PROGRAMMER_WORKFLOW_VERSION,
                "prompt_digest": programmer_prompt_digest(),
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


    async def fix_failed_candidate(
        self,
        *,
        root: Path,
        objective: str,
        failures: list[dict],
        changed_files: list[str],
        attempt: int,
    ) -> RepairPlanResult:
        root = Path(root).expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"Repository not found: {root}")

        snapshot = self.scanner.scan(root)
        health = deterministic_health(snapshot)
        failure_text = json.dumps(failures, ensure_ascii=False)[:36_000]
        context_objective = (
            objective
            + "\n"
            + " ".join(changed_files[:40])
            + "\n"
            + failure_text[:12_000]
        )
        context = self._context(root, context_objective, preferred=changed_files)

        user = json.dumps(
            {
                "prompt_version": CODER_FIX_VERSION,
                "prompt_digest": coder_fix_prompt_digest(),
                "attempt": attempt,
                "objective": objective,
                "repository": snapshot.model_dump(),
                "health": health.model_dump(),
                "changed_files": changed_files[:80],
                "validation_failures": failures[:12],
                "selected_current_candidate_context": context,
            },
            ensure_ascii=False,
        )

        model, payload = await self.ollama.chat_json(CODER_FIX_PROMPT, user)
        patch = str(payload.get("patch", "") or "")
        errors = validate_patch_paths(patch)
        valid = bool(patch.strip()) and not errors

        return RepairPlanResult(
            model=model,
            objective=objective,
            summary=str(payload.get("summary", "")),
            plan=[str(x) for x in payload.get("plan", [])][:20],
            patch=patch,
            tests=[str(x) for x in payload.get("tests", [])][:20],
            risk=str(payload.get("risk", "high")),
            valid=valid,
            validation_errors=errors,
        )
