"""Regression tests for V8 SQLite backup on Linux and Windows PowerShell hosts.

Uses Python stdlib only so Windows CI can run it without installing Manager.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.backup_sqlite_v8 import backup_sqlite


class SqliteBackupV8Tests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="manager v8 backup ")
        self.addCleanup(self.folder.cleanup)
        self.home = Path(self.folder.name)
        self.source = self.home / "source with spaces.sqlite"
        self.destination = self.home / "backup with spaces.sqlite"

    def _populate(self):
        connection = sqlite3.connect(str(self.source))
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(
            "CREATE TABLE job_events (id INTEGER PRIMARY KEY, message TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO job_events(message) VALUES (?)", ("Live manager intact",)
        )
        connection.commit()
        return connection

    def test_backup_contains_committed_wal_rows_while_source_open(self):
        live = self._populate()
        try:
            result = backup_sqlite(self.source, self.destination)
            self.assertTrue(result["ok"])
            self.assertEqual(result["integrity_check"], "ok")
            self.assertGreater(result["size_bytes"], 0)
            copied = sqlite3.connect(str(self.destination))
            try:
                self.assertEqual(
                    copied.execute("SELECT message FROM job_events").fetchone()[0],
                    "Live manager intact",
                )
            finally:
                copied.close()
            original = sqlite3.connect(str(self.source))
            try:
                self.assertEqual(
                    original.execute("SELECT COUNT(*) FROM job_events").fetchone()[0], 1
                )
            finally:
                original.close()
        finally:
            live.close()

    def test_cli_subprocess_works_with_spaces_in_windows_paths(self):
        live = self._populate()
        script = Path(__file__).resolve().parents[1] / "scripts" / "backup_sqlite_v8.py"
        try:
            proc = subprocess.run(
                [sys.executable, str(script), "--source", str(self.source),
                 "--destination", str(self.destination)],
                text=True, capture_output=True, timeout=25,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            response = json.loads(proc.stdout.strip())
            self.assertTrue(response["ok"])
            self.assertTrue(self.destination.is_file())
        finally:
            live.close()

    def test_missing_database_does_not_create_backup_or_source(self):
        with self.assertRaises(FileNotFoundError):
            backup_sqlite(self.source, self.destination)
        self.assertFalse(self.source.exists())
        self.assertFalse(self.destination.exists())

    def test_refuses_overwriting_previous_verified_backup(self):
        live = self._populate()
        try:
            backup_sqlite(self.source, self.destination)
            before = self.destination.read_bytes()
            with self.assertRaises(FileExistsError):
                backup_sqlite(self.source, self.destination)
            self.assertEqual(self.destination.read_bytes(), before)
        finally:
            live.close()

    def test_broken_sqlite_does_not_leave_backup_or_temporary_file(self):
        self.source.write_bytes(b"not a sqlite database")
        with self.assertRaises(sqlite3.DatabaseError):
            backup_sqlite(self.source, self.destination)
        self.assertFalse(self.destination.exists())
        self.assertFalse(list(self.home.glob("*.tmp")))

    def test_empty_database_does_not_produce_a_claimed_backup(self):
        empty = sqlite3.connect(str(self.source))
        try:
            empty.execute("PRAGMA user_version=42")
            empty.commit()
        finally:
            empty.close()
        with self.assertRaises(RuntimeError):
            backup_sqlite(self.source, self.destination)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
