---
name: bloglab-events-verification
description: Verifies official Ljubljana event listings, dates, venues and after-midnight nightlife.
metadata:
  version: '1.0.0-bloglab-adapted'
  project: 'DDAY2301/blog-lab'
---
# bloglab-events-verification

Check organiser/source page, start/end, ticket URL, exact venue, local Europe/Ljubljana calendar date and lastCheckedAt. Feed status 'fresh' does not imply individual records were reviewed today. Weekend editorial focus: Metelkova, Klub K4, Gala Hala, Channel Zero, Gromka, Publika and related nightlife venues. Do not invent a line-up for missing days. Distinguish workshops/exhibitions from night parties. Events after midnight up to 05:59 belong to preceding club night. If verification fails, show 'trenutno ni potrjenih dogodkov' and link venue source for independent confirmation.

## Operating procedure
1. Read `AGENTS.md`, current code and latest evidence before diagnosing.
2. Record objective, evidence and severity (S0–S3); prefer smallest change.
3. Use a feature branch and PR; never edit secrets or bypass review gates.
4. Verify the affected area with tests; mark unrun checks as NOT RUN.
5. Summarize results, risks and release decision without inventing successful deployment.

Derived and adapted from the user-provided BlogLab Skill Pack v1.0 (2026-11-10).
