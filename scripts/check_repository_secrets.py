"""Read-only credential scanner: precise token boundaries, no value logging.
Avoids matching the tail of unrelated words such as 'sandisk-...' in URLs.
Do not disable scanning merely because the candidate is inside a URL.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

PATTERNS = {
    "github_classic": re.compile(r"(?<![A-Za-z0-9_])ghp_[A-Za-z0-9]{20,}(?![A-Za-z0-9_])"),
    "github_fine_grained": re.compile(r"(?<![A-Za-z0-9_])github_pat_[A-Za-z0-9_]{20,}(?![A-Za-z0-9_])"),
    "api_secret": re.compile(r"(?<![A-Za-z0-9_])sk-[A-Za-z0-9_-]{20,}(?![A-Za-z0-9_-])"),
}
IGNORE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf", ".zip", ".ico", ".woff", ".woff2", ".mp4"}

def find_possible_secrets(content: str) -> set[str]:
    return {name for name, pattern in PATTERNS.items() if pattern.search(content)}

def main() -> int:
    root = Path(__file__).resolve().parent.parent
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).split(b"\0")
    findings = []
    for item in tracked:
        if not item:
            continue
        relative = item.decode("utf-8", errors="replace")
        path = root / relative
        if not path.is_file() or path.suffix.lower() in IGNORE_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        matches = find_possible_secrets(content)
        if matches:
            # Never print a candidate key; only report the file and type.
            findings.append((relative, sorted(matches)))
    for relative, kinds in findings:
        print(f"Potential credential in {relative} ({', '.join(kinds)})")
    if findings:
        print(f"Credential scan failed: {len(findings)} files need review")
        return 1
    print("Credential scan passed: no matching tokens in tracked text")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
