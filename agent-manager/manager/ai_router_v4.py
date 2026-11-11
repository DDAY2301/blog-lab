from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import psutil

from .ollama_client import OllamaClient


@dataclass
class ProviderStatus:
    name: str
    ok: bool
    model: str | None = None
    latency_ms: float | None = None
    error: str | None = None
    detail: dict[str, Any] | None = None


class ColibriClient:
    """OpenAI-compatible client for colibri v2.x (coli serve / coli web)."""

    def __init__(self) -> None:
        self.base_url = os.getenv("COLIBRI_BASE_URL", "http://127.0.0.1:8790/v1").rstrip("/")
        self.health_url = os.getenv("COLIBRI_HEALTH_URL", self.base_url.removesuffix("/v1") + "/health")
        self.model = os.getenv("COLIBRI_MODEL", "").strip()
        self.api_key = os.getenv("COLIBRI_API_KEY", "").strip()
        self.profile = os.getenv("AGENT_MANAGER_COLIBRI_PROFILE", "").strip().lower()
        self.timeout = float(os.getenv("COLIBRI_TIMEOUT", "300"))

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def available_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{self.base_url}/models", headers=self._headers())
            r.raise_for_status()
            data = r.json()
        rows = data.get("data", data.get("models", []))
        out: list[str] = []
        for row in rows if isinstance(rows, list) else []:
            if isinstance(row, dict):
                value = row.get("id") or row.get("name")
                if value:
                    out.append(str(value))
            elif row:
                out.append(str(row))
        return out

    async def choose_model(self) -> str:
        models = await self.available_models()
        if self.model and self.model in models:
            return self.model
        if models:
            return models[0]
        raise RuntimeError("Colibri API is reachable but no model is loaded.")

    async def status(self) -> ProviderStatus:
        start = time.perf_counter()
        try:
            model = await self.choose_model()
            return ProviderStatus(
                name="colibri",
                ok=True,
                model=model,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
                detail={
                    "profile": self.profile or "generative",
                    "decision_only": self.decision_only,
                },
            )
        except Exception as exc:
            return ProviderStatus(
                name="colibri",
                ok=False,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
                error=str(exc),
            )

    @property
    def decision_only(self) -> bool:
        return (
            self.profile.startswith("decision")
            or self.model.lower() in {"laya", "gliner2.5-decide", "gliner-decide"}
        )

    async def system_one(self, state: str, questions: dict[str, Any]) -> dict[str, Any]:
        model = await self.choose_model()
        body = {"model": model, "state": state, "questions": questions}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/systemone",
                headers=self._headers(),
                json=body,
            )
            r.raise_for_status()
            return r.json()

    async def chat_json(self, system: str, user: str) -> tuple[str, dict]:
        model = await self.choose_model()
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "temperature": 0.05,
            "max_tokens": int(os.getenv("COLIBRI_MAX_TOKENS", "2048")),
        }
        effort = os.getenv("COLIBRI_REASONING_EFFORT", "high").strip().lower()
        if effort in {"low", "medium", "high", "xhigh"}:
            body["reasoning_effort"] = effort

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=body,
            )
            r.raise_for_status()
            data = r.json()

        content = str(
            ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "")
        ).strip()
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"summary": content}
        return f"colibri/{model}", parsed


class AIRouterV4:
    """Colibri-first AI router with Ollama fallback and deterministic availability."""

    def __init__(self) -> None:
        self.colibri = ColibriClient()
        self.ollama = OllamaClient()
        self.priority = [
            x.strip().lower()
            for x in os.getenv("AGENT_MANAGER_AI_PRIORITY", "colibri,ollama").split(",")
            if x.strip()
        ]
        self._fail_until: dict[str, float] = {}
        self.cooldown = max(15, int(os.getenv("AGENT_MANAGER_PROVIDER_COOLDOWN", "60")))
        self.root = Path(__file__).resolve().parents[1]
        self._resource_lock = asyncio.Lock()
        total_gb = psutil.virtual_memory().total / (1024 ** 3)
        low_mem = os.getenv("AGENT_MANAGER_LOW_MEMORY_AI_SWAP", "auto").strip().lower()
        self.low_memory_swap = low_mem in {"1", "true", "yes", "on"} or (
            low_mem == "auto" and total_gb < 12.0
        )
        self.colibri_min_free_gb = float(os.getenv("AGENT_MANAGER_COLIBRI_MIN_FREE_GB", "2.2"))

    async def status(self) -> dict[str, dict[str, Any]]:
        c = await self.colibri.status()
        start = time.perf_counter()
        try:
            model = await self.ollama.choose_model()
            o = ProviderStatus(
                name="ollama",
                ok=True,
                model=model,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
            )
        except Exception as exc:
            o = ProviderStatus(
                name="ollama",
                ok=False,
                latency_ms=round((time.perf_counter() - start) * 1000, 1),
                error=str(exc),
            )
        memory = psutil.virtual_memory()
        return {
            "colibri": c.__dict__,
            "ollama": o.__dict__,
            "priority": self.priority,
            "resource_mode": {
                "low_memory_swap": self.low_memory_swap,
                "total_ram_gb": round(memory.total / (1024 ** 3), 2),
                "available_ram_gb": round(memory.available / (1024 ** 3), 2),
                "colibri_min_free_gb": self.colibri_min_free_gb,
            },
        }

    async def _unload_ollama_running_models(self) -> None:
        """Free RAM without stopping the Ollama service itself."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(f"{self.ollama.base_url.rstrip('/')}/api/ps")
                r.raise_for_status()
                models = r.json().get("models", [])
                for row in models:
                    name = str(row.get("name") or row.get("model") or "").strip()
                    if not name:
                        continue
                    try:
                        await client.post(
                            f"{self.ollama.base_url.rstrip('/')}/api/generate",
                            json={"model": name, "prompt": "", "stream": False, "keep_alive": 0},
                        )
                    except Exception:
                        pass
        except Exception:
            return
        await asyncio.sleep(2.0)

    async def _start_colibri_for_triage(self) -> bool:
        try:
            current = await self.colibri.status()
            if current.ok:
                return True
        except Exception:
            pass

        if os.name != "nt":
            return False

        script = self.root / "scripts" / "start-colibri.ps1"
        if not script.exists():
            return False

        def run_start() -> int:
            completed = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                ],
                cwd=str(self.root),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=210,
                check=False,
            )
            return int(completed.returncode)

        await asyncio.to_thread(run_start)
        deadline = time.time() + 45.0
        while time.time() < deadline:
            try:
                status = await self.colibri.status()
                if status.ok:
                    return True
            except Exception:
                pass
            await asyncio.sleep(2.0)
        return False

    async def _stop_colibri_after_triage(self) -> None:
        if os.name != "nt":
            return
        colibri_home = Path(os.getenv("COLIBRI_HOME", "")).expanduser() if os.getenv("COLIBRI_HOME") else None
        if not colibri_home or not colibri_home.exists():
            colibri_home = self.root / "data" / "colibri-src"
        cli = colibri_home / "c" / "coli"
        if not cli.exists():
            return

        def run_stop() -> None:
            try:
                subprocess.run(
                    ["py", "-3", str(cli), "stop"],
                    cwd=str(colibri_home),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=45,
                    check=False,
                )
            except Exception:
                pass

        await asyncio.to_thread(run_stop)

    async def _prepare_low_memory_colibri(self) -> bool:
        await self._unload_ollama_running_models()
        deadline = time.time() + 15.0
        while time.time() < deadline:
            free_gb = psutil.virtual_memory().available / (1024 ** 3)
            if free_gb >= self.colibri_min_free_gb:
                break
            await asyncio.sleep(1.0)
        return await self._start_colibri_for_triage()

    async def triage(self, state: str) -> dict[str, Any] | None:
        # Agent Focus on 8 GB hardware: reuse resident Ollama instead of
        # spawning Colibri and evicting the currently loaded coding model.
        # This remains advisory triage only; no repair action is executed here.
        if os.getenv("AGENT_MANAGER_LOW_MEMORY_MODE", "0") == "1":
            system = (
                "You classify operational incidents for a local multi-agent service. "
                "Return JSON only with severity (P0, P1, P2 or P3), action "
                "(observe, restart, self_heal or human) and reason. "
                "Use only supplied evidence. Do not invent outages or recommend "
                "credential bypass or destructive recovery."
            )
            try:
                async with self._resource_lock:
                    model, result = await self.ollama.chat_json(system, state[:8000])
                if not isinstance(result, dict):
                    return None
                severity = str(result.get("severity") or "").upper()
                action = str(result.get("action") or "").lower()
                if severity not in {"P0", "P1", "P2", "P3"}:
                    return None
                if action not in {"observe", "restart", "self_heal", "human"}:
                    return None
                return {
                    "severity": severity,
                    "action": action,
                    "reason": str(result.get("reason") or "")[:1200],
                    "provider": f"ollama/{model}",
                }
            except Exception:
                return None

        if self._fail_until.get("colibri", 0) > time.time():
            return None
        questions = {
            "severity": {
                "type": "choice",
                "instructions": "How severe is this operational incident?",
                "criteria": {
                    "P0": "system-wide outage, data corruption, or security emergency",
                    "P1": "critical service unavailable or repeated unrecovered failure",
                    "P2": "degraded service with a workaround or noncritical component failure",
                    "P3": "minor issue or maintenance concern"
                }
            },
            "action": {
                "type": "choice",
                "instructions": "Which safe response family fits best?",
                "criteria": {
                    "observe": "collect more evidence without changing the system",
                    "restart": "restart a reversible local service or worker",
                    "self_heal": "invoke an existing tested self-heal workflow",
                    "human": "human approval or credentials are required"
                }
            }
        }

        async with self._resource_lock:
            started_for_call = False
            try:
                if self.low_memory_swap:
                    status = await self.colibri.status()
                    if not status.ok:
                        started_for_call = await self._prepare_low_memory_colibri()
                        if not started_for_call:
                            return None
                return await self.colibri.system_one(state, questions)
            except Exception:
                return None
            finally:
                if self.low_memory_swap and started_for_call:
                    await self._stop_colibri_after_triage()

    async def chat_json(self, system: str, user: str) -> tuple[str, dict]:
        async with self._resource_lock:
            if self.low_memory_swap and self.colibri.decision_only:
                await self._stop_colibri_after_triage()

            now = time.time()
            errors: list[str] = []
            for provider in self.priority:
                if self._fail_until.get(provider, 0) > now:
                    continue
                try:
                    if provider == "colibri":
                        if self.colibri.decision_only:
                            # Laya is reserved for System One triage; generation goes to Ollama.
                            continue
                        return await self.colibri.chat_json(system, user)
                    if provider == "ollama":
                        model, result = await self.ollama.chat_json(system, user)
                        return f"ollama/{model}", result
                except Exception as exc:
                    self._fail_until[provider] = now + self.cooldown
                    errors.append(f"{provider}: {exc}")
            raise RuntimeError("No local AI provider is available. " + " | ".join(errors))
