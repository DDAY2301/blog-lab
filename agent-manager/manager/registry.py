from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .models import AgentRecord, HealthReport, RepoSnapshot


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AgentRegistry:
    def __init__(self, state_path: str | None = None) -> None:
        default_path = Path(__file__).resolve().parents[1] / "data" / "registry.json"
        self.path = Path(
            state_path
            or os.getenv("AGENT_MANAGER_STATE", str(default_path))
        ).expanduser()

    def _read(self) -> dict[str, AgentRecord]:
        if not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        out: dict[str, AgentRecord] = {}
        for item in raw.get("agents", []):
            try:
                record = AgentRecord.model_validate(item)
                out[record.id] = record
            except Exception:
                continue
        return out

    def _write(self, records: dict[str, AgentRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "updated_at": utc_now(),
            "agents": [
                record.model_dump()
                for record in sorted(records.values(), key=lambda x: x.name.lower())
            ],
        }
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp.replace(self.path)

    @staticmethod
    def make_id(root: str) -> str:
        normalized = str(Path(root).expanduser().resolve()).lower()
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
        return f"agent-{digest}"

    def list(self) -> list[AgentRecord]:
        return sorted(self._read().values(), key=lambda x: x.name.lower())

    def upsert(self, snapshot: RepoSnapshot, health: HealthReport) -> AgentRecord:
        records = self._read()
        record_id = self.make_id(snapshot.root)
        now = utc_now()
        previous = records.get(record_id)

        record = AgentRecord(
            id=record_id,
            name=snapshot.name,
            root=snapshot.root,
            first_seen_at=previous.first_seen_at if previous else now,
            last_seen_at=now,
            health_score=health.score,
            status=health.status,
            languages=snapshot.languages,
            agent_paths=snapshot.agent_paths,
            workflow_files=snapshot.workflow_files,
            prompt_files=snapshot.prompt_files,
            security_findings=snapshot.security_findings,
            previous_score=previous.health_score if previous else None,
        )
        records[record_id] = record
        self._write(records)
        return record
