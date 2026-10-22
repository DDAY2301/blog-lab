"""Prevent false outage loops caused by stale workflow Worker version constants."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "terminal/worker/src/index.js"
WORKFLOWS = (
    ".github/workflows/deploy-worker.yml",
    ".github/workflows/terminal-agent-command-suite.yml",
    ".github/workflows/terminal-self-heal.yml",
)
pattern = r"auth-v\d+\.\d+-production"
versions = set(re.findall(pattern, SOURCE.read_text(encoding="utf-8")))
if len(versions) != 1:
    raise SystemExit(f"Worker has inconsistent production versions: {sorted(versions)}")
expected = versions.pop()
for path in WORKFLOWS:
    data = (ROOT / path).read_text(encoding="utf-8")
    actual = re.findall(r"EXPECTED_WORKER_VERSION:\s*(" + pattern + r")", data)
    if actual != [expected]:
        raise SystemExit(f"VERSION_CONTRACT_MISMATCH {path} expected={expected} configured={actual}")
    print(f"VERSION_CONTRACT_OK {path} {expected}")
