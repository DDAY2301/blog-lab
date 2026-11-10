---
name: bloglab-ux-e2e-qa
description: Tests actual BlogLab user journeys, event archive, photo credits and responsive layouts.
metadata:
  version: '1.0.0-bloglab-adapted'
  project: 'DDAY2301/blog-lab'
---
# bloglab-ux-e2e-qa

Objective: test homepage → rubric → story → back; homepage → calendar → event → official source; Weekend Friday/Saturday/Sunday and archives, search with and without matches. Verify /?rubrika=, /?clanek=, /?dogodek=, /?dogodki= and query deep links across reloads. Test 360/768/1440px; missing photo, slow network, invalid date, keyboard navigation and mobile menu. Assert attribution for each photo, no false event photo labels and no empty section gaps. Report severity, evidence, reproduction, fix and PASS/FAIL/BLOCKED. GitHub Actions green is not proof that production works.

## Operating procedure
1. Read `AGENTS.md`, current code and latest evidence before diagnosing.
2. Record objective, evidence and severity (S0–S3); prefer smallest change.
3. Use a feature branch and PR; never edit secrets or bypass review gates.
4. Verify the affected area with tests; mark unrun checks as NOT RUN.
5. Summarize results, risks and release decision without inventing successful deployment.

Derived and adapted from the user-provided BlogLab Skill Pack v1.0 (2026-11-10).
