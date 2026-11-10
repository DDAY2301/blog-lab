---
name: bloglab-publisher-reliability
description: Ensures automated BlogLab publishing is evidence-backed, scheduled and idempotent.
metadata:
  version: '1.0.0-bloglab-adapted'
  project: 'DDAY2301/blog-lab'
---
# bloglab-publisher-reliability

Read executable schedule in config.yaml and schedule.py rather than obsolete README assumptions. Separate heartbeat/skip/publish/failure; never report a slot as published without content commit and public article verification. Preserve limits and content quality gates. Do not force AI publishing when sources are weak. For photos: verified Wikimedia Commons or other licensed primary media with attribution, source URL, rights and caption; otherwise HOLD photo, never synthesize or insert a random city scene as a factual event photo. Publisher may modify content/state/diagnostics only, per AGENTS.md. Dry-run and tests before proposed changes.

## Operating procedure
1. Read `AGENTS.md`, current code and latest evidence before diagnosing.
2. Record objective, evidence and severity (S0–S3); prefer smallest change.
3. Use a feature branch and PR; never edit secrets or bypass review gates.
4. Verify the affected area with tests; mark unrun checks as NOT RUN.
5. Summarize results, risks and release decision without inventing successful deployment.

Derived and adapted from the user-provided BlogLab Skill Pack v1.0 (2026-11-10).
