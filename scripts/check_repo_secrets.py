#!/usr/bin/env python3
"""Detect plausible committed/API secrets without false positives inside words.

A historical guardian check matched `sk-` *inside* the word "sandisk-" in an
ordinary forum URL. Boundaries prevent that false alarm. Never print matched
secret values, including into GitHub Actions logs.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

# The prefix must start a token, not be embedded in an ordinary word.
# Keep the previous minimum-length thresholds to preserve detection coverage.
PATTERNS = (
    ("GitHub classic token", re.compile(rb"(?<![A-Za-z0-9_])ghp_[A-Za-z0-9]{20,}")),
    ("GitHub fine-grained token", re.compile(rb"(?<![A-Za-z0-9_])github_pat_[A-Za-z0-9_]{20,}")),
    ("API key", re.compile(rb"(?<![A-Za-z0-9_])sk-[A-Za-z0-9_-]{20,}")),
)

BINARY_SUFFIXES = frozenset({
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".svgz",
    ".zip", ".gz", ".bz2", ".xz", ".pdf", ".woff", ".woff2", ".ttf",
    ".mp3", ".mp4", ".mov", ".webm", ".wav", ".sqlite", ".db",
})
# Existing workflow excluded this generated dependency lockfile.
EXCLUDED_FILES = frozenset({"package-lock.json"})


def find_secrets(content: bytes) -> list[tuple[str, int]]:
    """Return only secret types and line numbers, never raw values."""
    result = []
    for name, pattern in PATTERNS:
        for match in pattern.finditer(content):
            line = content.count(b"\n", 0, match.start()) + 1
            result.append((name, line))
    return result


def tracked_and_new_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        check=True,
        stdout=subprocess.PIPE,
    )
    return sorted({os.fsdecode(part) for part in result.stdout.split(b"\0") if part})


def scan(repository: Path) -> int:
    findings: list[tuple[str, int, str]] = []
    for relative_path in tracked_and_new_files():
        path = repository / relative_path
        if path.name in EXCLUDED_FILES or path.suffix.lower() in BINARY_SUFFIXES:
            continue
        if path.is_symlink() or not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            print(f"SECRET_SCAN_IO_ERROR {relative_path}: {type(exc).__name__}", file=sys.stderr)
            return 2
        if b"\0" in data[:8192]:
            continue
        for kind, line in find_secrets(data):
            findings.append((relative_path, line, kind))

    if findings:
        for filename, line, kind in findings:
            print(f"::error file={filename},line={line}::Potential {kind} found; value redacted")
        print(f"SECRET_SCAN_FAILED count={len(findings)}", file=sys.stderr)
        return 1
    print("SECRET_SCAN_OK no matching tokens")
    return 0


if __name__ == "__main__":
    sys.exit(scan(Path.cwd()))
