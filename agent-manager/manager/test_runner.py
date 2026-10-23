from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TestCommand:
    name: str
    argv: list[str]
    cwd: str = "."
    timeout: int = 600


@dataclass
class TestResult:
    name: str
    argv: list[str]
    cwd: str
    returncode: int
    stdout: str = ""
    stderr: str = ""
    passed: bool = False


def _package_scripts(path: Path) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    scripts = payload.get("scripts")
    return scripts if isinstance(scripts, dict) else {}


def detect_test_commands(root: Path, changed_files: list[str] | None = None) -> list[TestCommand]:
    changed = [x.replace("\\", "/") for x in (changed_files or [])]
    commands: list[TestCommand] = []

    # Agent Manager has its own isolated Python test suite.
    if (root / "agent-manager" / "requirements.txt").exists() and (
        not changed or any(p.startswith("agent-manager/") for p in changed)
    ):
        commands.extend(
            [
                TestCommand(
                    name="agent-manager compile",
                    argv=["python", "-m", "compileall", "-q", "manager", "run.py"],
                    cwd="agent-manager",
                    timeout=120,
                ),
                TestCommand(
                    name="agent-manager tests",
                    argv=["python", "-m", "pytest", "-q"],
                    cwd="agent-manager",
                    timeout=600,
                ),
                TestCommand(
                    name="agent-manager FastAPI smoke",
                    argv=[
                        "python",
                        "-c",
                        "from manager.service import app; assert app.title == 'Agent Manager'; print(app.version)",
                    ],
                    cwd="agent-manager",
                    timeout=120,
                ),
            ]
        )

    package = root / "package.json"
    if package.exists():
        scripts = _package_scripts(package)
        if "test" in scripts:
            commands.append(TestCommand(name="npm test", argv=["npm", "test"], timeout=900))
        if "build" in scripts:
            commands.append(TestCommand(name="npm build", argv=["npm", "run", "build"], timeout=900))

    # Generic Python repository fallback.
    if not commands:
        has_python = any(root.rglob("*.py"))
        if has_python:
            commands.append(
                TestCommand(
                    name="python compile",
                    argv=["python", "-m", "compileall", "-q", "."],
                    timeout=300,
                )
            )
            if (root / "pytest.ini").exists() or (root / "pyproject.toml").exists() or (root / "tests").exists():
                commands.append(TestCommand(name="pytest", argv=["python", "-m", "pytest", "-q"], timeout=900))

    # De-duplicate while keeping stable order.
    seen: set[tuple[str, tuple[str, ...], str]] = set()
    out: list[TestCommand] = []
    for command in commands:
        key = (command.name, tuple(command.argv), command.cwd)
        if key in seen:
            continue
        seen.add(key)
        out.append(command)
    return out


def run_tests(root: Path, commands: list[TestCommand]) -> list[TestResult]:
    results: list[TestResult] = []
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")

    for command in commands:
        cwd = (root / command.cwd).resolve()
        try:
            proc = subprocess.run(
                command.argv,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=command.timeout,
                check=False,
            )
            result = TestResult(
                name=command.name,
                argv=command.argv,
                cwd=command.cwd,
                returncode=proc.returncode,
                stdout=(proc.stdout or "")[-12000:],
                stderr=(proc.stderr or "")[-12000:],
                passed=proc.returncode == 0,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            result = TestResult(
                name=command.name,
                argv=command.argv,
                cwd=command.cwd,
                returncode=124,
                stderr=str(exc),
                passed=False,
            )
        results.append(result)
        if not result.passed:
            break
    return results
