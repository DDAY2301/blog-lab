"""Consistent and verified SQLite hot-backup for the Agent Manager V8 pilot.

Called as a script from Windows PowerShell to avoid multiline Python -c quoting.
Never writes to or modifies the original database.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import uuid
from pathlib import Path


def backup_sqlite(source: Path, destination: Path) -> dict:
    source = Path(source).expanduser().resolve()
    destination = Path(destination).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"SQLite source does not exist: {source}")
    if source == destination:
        raise ValueError("Source and destination must be different.")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite an existing backup: {destination}")
    if not destination.parent.is_dir():
        raise FileNotFoundError(f"Backup directory does not exist: {destination.parent}")

    temporary = destination.with_name(
        destination.name + "." + uuid.uuid4().hex + ".tmp"
    )
    src = None
    dst = None
    try:
        # SQLite backup API produces a consistent snapshot, including WAL data,
        # while the original service remains online.
        src = sqlite3.connect(str(source), timeout=15)
        dst = sqlite3.connect(str(temporary), timeout=15)
        src.backup(dst, pages=128, sleep=0.15)
        dst.close()
        dst = None
        src.close()
        src = None

        check = sqlite3.connect(str(temporary), timeout=15)
        try:
            integrity = check.execute("PRAGMA quick_check").fetchone()[0]
            if integrity != "ok":
                raise RuntimeError(f"SQLite quick_check failed: {integrity}")
            tables = check.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()[0]
            if tables < 1:
                raise RuntimeError("Backup is unexpectedly empty (no tables).")
        finally:
            check.close()

        if destination.exists():
            raise FileExistsError(f"Backup appeared concurrently: {destination}")
        os.replace(temporary, destination)
        return {
            "ok": True,
            "backup_path": str(destination),
            "size_bytes": destination.stat().st_size,
            "integrity_check": integrity,
            "tables": tables,
        }
    finally:
        if src is not None:
            src.close()
        if dst is not None:
            dst.close()
        if temporary.exists():
            temporary.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a hot SQLite backup.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = backup_sqlite(args.source, args.destination)
    except Exception as exc:
        print(f"SQLite backup failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
