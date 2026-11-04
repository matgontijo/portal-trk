# portal-trk — technical portfolio notes

Source reviewed: `066cae251058759306cdb9bd9b2ce7a4e113c14a` · 2026-11-04. These notes distinguish implemented behavior from next steps; they do not certify a production deployment.

## Purpose

Business operations portal with backend-enforced module permissions and recurring workflows.

**Stack:** Python, FastAPI, SQLite, React, TypeScript.

**AI scope:** Business workflow automation; no ML or LLM implementation found.

## Evidence in this repository

- [backend/app/permissions.py](../backend/app/permissions.py): Module/action permissions with default-deny behavior.
- [backend/tests/test_permissions.py](../backend/tests/test_permissions.py): Five permission regression cases.
- [backend/app/recorrencia.py](../backend/app/recorrencia.py): Recurring-task logic.
- [backend/app/routers/skills.py](../backend/app/routers/skills.py): Application skills endpoint; its name alone is not evidence of an LLM agent.

## Validation

```text
cd backend && python -m pytest tests/test_permissions.py -q
```

Use an isolated environment and synthetic data. Never run operational ingestion, scheduled jobs or live provider calls merely to demonstrate the project. Test presence is not the same as a successful test run.

## Known limits and next steps

- Default development signing secret and demo accounts need explicit production configuration.
- The bank provider defaults to fake; do not describe a live banking integration without validation.
- Tests cover the permission helper, not full end-to-end authorization of every route.
- No CI workflow or model evaluation was found.

## Portfolio positioning

Supporting access-control and workflow project.

A reproducible AI evaluation should document a synthetic or anonymized dataset, baseline, expected outputs, failure cases, quality metrics, latency and cost. Training and evaluating a predictive model would be separate work; it is not claimed here.
