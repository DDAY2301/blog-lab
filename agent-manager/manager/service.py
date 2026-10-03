from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException

from .autopilot import AutopilotDisabled, AutonomousRepairExecutor
from .discovery import RepositoryScanner
from .evaluator import AgentEvaluator, deterministic_health
from .models import (
    AutopilotRequest,
    AutopilotResult,
    DiscoverResult,
    RepairPlanRequest,
    RepairPlanResult,
    ReviewRequest,
    ReviewResult,
    ScanRequest,
)
from .ollama_client import OllamaClient
from .registry import AgentRegistry
from .repair import RepairPlanner

app = FastAPI(
    title="Agent Manager",
    version="0.4.0",
    description="Local-first supervisor for discovering, evaluating and safely improving AI agents.",
)

scanner = RepositoryScanner()
ollama = OllamaClient()
evaluator = AgentEvaluator(ollama)
registry = AgentRegistry()
repair_planner = RepairPlanner(ollama)
autopilot = AutonomousRepairExecutor(repair_planner)


def configured_roots() -> list[str]:
    raw = os.getenv("AGENT_MANAGER_ROOTS", "").strip()
    if raw:
        return [p for p in raw.split(os.pathsep) if p]
    return [str(Path(__file__).resolve().parents[2])]


@app.get("/health")
async def health() -> dict:
    model_status: dict = {"reachable": False, "models": []}
    try:
        models = await ollama.available_models()
        model_status = {"reachable": True, "models": models}
    except Exception as exc:
        model_status = {"reachable": False, "error": str(exc), "models": []}

    write_enabled = os.getenv("AGENT_MANAGER_WRITE_ENABLED", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    return {
        "ok": True,
        "version": "0.4.0",
        "mode": "local-free",
        "write_enabled": write_enabled,
        "write_policy": "isolated-worktree-tests-branch-pr-no-direct-main",
        "registered_agents": len(registry.list()),
        "ollama": model_status,
    }


@app.get("/models")
async def models() -> dict:
    try:
        available = await ollama.available_models()
        chosen = await ollama.choose_model()
        return {"available": available, "selected": chosen}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/registry")
async def get_registry() -> dict:
    return {"agents": [item.model_dump() for item in registry.list()]}


@app.post("/registry/discover", response_model=DiscoverResult)
async def discover(request: ScanRequest) -> DiscoverResult:
    roots = request.roots or configured_roots()
    agents = []
    errors = []

    for root in roots:
        try:
            snapshot = scanner.scan(root)
            report = deterministic_health(snapshot)
            agents.append(registry.upsert(snapshot, report))
        except Exception as exc:
            errors.append({"root": root, "error": str(exc)})

    return DiscoverResult(agents=agents, errors=errors)


@app.post("/scan")
async def scan(request: ScanRequest) -> dict:
    roots = request.roots or configured_roots()
    results = []
    for root in roots:
        try:
            snapshot = scanner.scan(root)
            report = deterministic_health(snapshot)
            results.append(
                {
                    "snapshot": snapshot.model_dump(),
                    "health": report.model_dump(),
                }
            )
        except Exception as exc:
            results.append({"root": root, "error": str(exc)})
    return {"results": results}


@app.post("/review", response_model=ReviewResult)
async def review(request: ReviewRequest) -> ReviewResult:
    try:
        snapshot = scanner.scan(request.root)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    health_report = deterministic_health(snapshot)
    registry.upsert(snapshot, health_report)
    ai_review = None

    if request.use_ai:
        try:
            ai_review = await evaluator.ai_review(snapshot, health_report)
        except Exception as exc:
            health_report.findings.append(f"AI review unavailable: {exc}")

    return ReviewResult(
        snapshot=snapshot,
        health=health_report,
        ai_review=ai_review,
    )


@app.post("/repair/plan", response_model=RepairPlanResult)
async def plan_repair(request: RepairPlanRequest) -> RepairPlanResult:
    try:
        return await repair_planner.plan(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/autopilot/execute", response_model=AutopilotResult)
async def execute_autopilot(request: AutopilotRequest) -> AutopilotResult:
    try:
        return await autopilot.execute(request)
    except AutopilotDisabled as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
