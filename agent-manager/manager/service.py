from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException

from .discovery import RepositoryScanner
from .evaluator import AgentEvaluator, deterministic_health
from .models import ReviewRequest, ReviewResult, ScanRequest
from .ollama_client import OllamaClient

app = FastAPI(
    title="Agent Manager",
    version="0.1.0",
    description="Local-first supervisor for discovering, evaluating and improving AI agents.",
)

scanner = RepositoryScanner()
ollama = OllamaClient()
evaluator = AgentEvaluator(ollama)


def configured_roots() -> list[str]:
    raw = os.getenv("AGENT_MANAGER_ROOTS", "").strip()
    if raw:
        return [p for p in raw.split(os.pathsep) if p]
    # Running from agent-manager/, default to the parent repository.
    return [str(Path(__file__).resolve().parents[2])]


@app.get("/health")
async def health() -> dict:
    model_status: dict = {"reachable": False, "models": []}
    try:
        models = await ollama.available_models()
        model_status = {"reachable": True, "models": models}
    except Exception as exc:
        model_status = {"reachable": False, "error": str(exc), "models": []}

    return {
        "ok": True,
        "version": "0.1.0",
        "mode": "local-free",
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
    ai_review = None

    if request.use_ai:
        try:
            ai_review = await evaluator.ai_review(snapshot, health_report)
        except Exception as exc:
            # Deterministic review remains available even when Ollama/model is offline.
            health_report.findings.append(f"AI review unavailable: {exc}")

    return ReviewResult(
        snapshot=snapshot,
        health=health_report,
        ai_review=ai_review,
    )
