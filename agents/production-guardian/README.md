# Production Guardian Agent

This folder contains the Blog Lab production guardian runtime.

Use from repository root:

```bash
python agents/production-guardian/guardian.py check --skip-remote
python agents/production-guardian/guardian.py check --strict-remote
python agents/production-guardian/guardian.py repair
```

The directory name intentionally matches the product wording used in workflows. Tests import the module through `agents/production_guardian_import.py` because Python package imports cannot use hyphens directly.
