from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

def _bool(name: str, default: bool=False) -> bool:
    return os.getenv(name, "1" if default else "0").strip().lower() in {"1","true","yes","on"}

@dataclass(frozen=True)
class SettingsV3:
    host: str = os.getenv("AGENT_MANAGER_HOST", "127.0.0.1")
    port: int = int(os.getenv("AGENT_MANAGER_PORT", "8787"))
    db_path: Path = Path(os.getenv("AGENT_MANAGER_DB", "./data/agent_manager.db")).expanduser()
    monitor_interval: int = max(15, int(os.getenv("AGENT_MANAGER_MONITOR_INTERVAL", "60")))
    heartbeat_interval: int = max(10, int(os.getenv("AGENT_MANAGER_HEARTBEAT_INTERVAL", "30")))
    write_enabled: bool = _bool("AGENT_MANAGER_WRITE_ENABLED", False)
    roots_raw: str = os.getenv("AGENT_MANAGER_ROOTS", "")
    pv_root: str = os.getenv("PROJECT_VISIBILITY_ROOT", "")
    pv_health_url: str = os.getenv("PROJECT_VISIBILITY_HEALTH_URL", "http://127.0.0.1:8000/health")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    gmail_enabled: bool = _bool("GMAIL_REPORTING_ENABLED", False)
    gmail_token_file: Path = Path(os.getenv("GMAIL_OAUTH_TOKEN_FILE", "./data/gmail-token.json")).expanduser()
    report_to: str = os.getenv("REPORT_TO_EMAIL", "").strip()
    maintenance_interval: int = max(30, int(os.getenv("AGENT_MANAGER_MAINTENANCE_INTERVAL", "60")))
    ai_priority: str = os.getenv("AGENT_MANAGER_AI_PRIORITY", "colibri,ollama")
    colibri_base_url: str = os.getenv("COLIBRI_BASE_URL", "http://127.0.0.1:8790/v1")
    colibri_model: str = os.getenv("COLIBRI_MODEL", "").strip()
    def roots(self) -> list[Path]:
        vals=[x.strip() for x in self.roots_raw.split(os.pathsep) if x.strip()]
        if self.pv_root.strip() and self.pv_root.strip() not in vals: vals.insert(0,self.pv_root.strip())
        return [Path(v).expanduser() for v in vals]
