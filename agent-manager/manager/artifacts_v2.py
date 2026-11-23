from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import uuid
from pathlib import Path
from typing import Any

from .db_v3 import StoreV3, utcnow

MAX_ARTIFACT_BYTES = int(os.getenv("AGENT_MANAGER_MAX_ARTIFACT_BYTES", str(25 * 1024 * 1024)))
MAX_EMAIL_ARTIFACT_BYTES = int(os.getenv("AGENT_MANAGER_MAX_EMAIL_ARTIFACT_BYTES", str(60 * 1024 * 1024)))
TEXT_EXCERPT_BYTES = int(os.getenv("AGENT_MANAGER_ARTIFACT_TEXT_EXCERPT_BYTES", str(64 * 1024)))


def _safe_name(name: str) -> str:
    base = Path(str(name or "artifact.bin")).name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip(".-")
    return stem[:120] or "artifact.bin"


def _guess_mime(name: str, mime_type: str | None = None) -> str:
    value = str(mime_type or "").strip().lower()
    if value:
        return value
    guessed, _ = mimetypes.guess_type(name)
    return guessed or "application/octet-stream"


class ArtifactStoreV2:
    """Durable, bounded artifact store inside the existing Agent Manager data directory."""

    def __init__(self, store: StoreV3) -> None:
        self.store = store
        root = Path(__file__).resolve().parents[1]
        self.root = Path(os.getenv("AGENT_MANAGER_ARTIFACT_ROOT", str(root / "data" / "artifacts"))).expanduser()

    def save_bytes(
        self,
        *,
        source: str,
        source_id: str,
        filename: str,
        mime_type: str,
        data: bytes,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not data:
            raise ValueError("Artifact is empty.")
        if len(data) > MAX_ARTIFACT_BYTES:
            raise ValueError(f"Artifact exceeds {MAX_ARTIFACT_BYTES} bytes.")

        name = _safe_name(filename)
        mime = _guess_mime(name, mime_type)
        digest = hashlib.sha256(data).hexdigest()
        artifact_id = str(uuid.uuid4())
        bucket = utcnow()[:7]
        folder = self.root / bucket
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{digest[:16]}-{name}"
        if not path.exists():
            path.write_bytes(data)

        payload = metadata or {}
        self.store.execute(
            """
            INSERT INTO artifacts(
              id,source,source_id,filename,mime_type,size_bytes,sha256,local_path,created_at,metadata
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                artifact_id,
                source,
                source_id,
                name,
                mime,
                len(data),
                digest,
                str(path),
                utcnow(),
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        return self.get(artifact_id)

    def get(self, artifact_id: str) -> dict[str, Any]:
        rows = self.store.query("SELECT * FROM artifacts WHERE id=?", (artifact_id,))
        if not rows:
            raise KeyError(artifact_id)
        row = rows[0]
        try:
            row["metadata"] = json.loads(row.get("metadata") or "{}")
        except Exception:
            row["metadata"] = {}
        return row

    def list_for_source(self, source: str, source_id: str) -> list[dict[str, Any]]:
        rows = self.store.query(
            "SELECT * FROM artifacts WHERE source=? AND source_id=? ORDER BY created_at,id",
            (source, source_id),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            try:
                row["metadata"] = json.loads(row.get("metadata") or "{}")
            except Exception:
                row["metadata"] = {}
            out.append(row)
        return out

    def read_bytes(self, artifact: dict[str, Any]) -> bytes:
        path = Path(str(artifact.get("local_path") or ""))
        resolved = path.resolve()
        root = self.root.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise RuntimeError("Artifact path escaped the configured store.") from exc
        data = resolved.read_bytes()
        if len(data) > MAX_ARTIFACT_BYTES:
            raise RuntimeError("Stored artifact exceeds configured size limit.")
        return data

    def text_excerpt(self, artifact: dict[str, Any]) -> str:
        mime = str(artifact.get("mime_type") or "").lower()
        name = str(artifact.get("filename") or "").lower()
        textual = (
            mime.startswith("text/")
            or mime in {"application/json", "application/xml", "application/yaml", "application/x-yaml"}
            or name.endswith((".txt", ".md", ".markdown", ".json", ".csv", ".xml", ".yaml", ".yml"))
        )
        if not textual:
            return ""
        raw = self.read_bytes(artifact)[:TEXT_EXCERPT_BYTES]
        return raw.decode("utf-8-sig", errors="replace").strip()

    @staticmethod
    def public_view(artifact: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": artifact.get("id"),
            "filename": artifact.get("filename"),
            "mime_type": artifact.get("mime_type"),
            "size_bytes": artifact.get("size_bytes"),
            "sha256": artifact.get("sha256"),
            "metadata": artifact.get("metadata") or {},
        }
