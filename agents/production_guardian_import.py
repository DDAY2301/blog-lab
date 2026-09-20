from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load_guardian() -> ModuleType:
    root = Path(__file__).resolve().parents[1]
    path = root / "agents" / "production-guardian" / "guardian.py"
    name = "blog_lab_production_guardian"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load production guardian from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
