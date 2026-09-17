# Implementation Plan: 013-manual-planning-today

**Branch**: `[013-manual-planning-today]` | **Date**: 2026-09-16 | **Spec**: [specs/013-manual-planning-today/spec.md](spec.md)

**Input**: Feature specification from `/specs/013-manual-planning-today/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement the complete manual planning workflow (Manual Task Drafts → Timeline generation → Reality Check → Save Daily Plan → GET /today → Edit status) using a deterministic, rule-based scheduler, explicitly bypassing all AI/LLM providers.

## Technical Context

**Language/Version**: Python 3.10

**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, Alembic

**Storage**: PostgreSQL

**Testing**: Pytest

**Target Platform**: Desktop app backend (consumed by Tauri 2 / SvelteKit)

**Project Type**: Backend Web Service

**Performance Goals**: Deterministic scheduling algorithm < 500ms for 50 tasks

**Constraints**: Strict timezone handling, idempotent saving, transactional consistency

**Scale/Scope**: Single user per request (authenticated), daily scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite, FastAPI/Python/Pydantic, and PostgreSQL/SQLAlchemy boundaries?
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully? (Handled at frontend contract level)
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

## Project Structure

### Documentation (this feature)

```text
specs/013-manual-planning-today/
├── plan.md              # This file
├── spec.md              # Feature specification
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── planning.py
│   ├── core/
│   │   ├── scheduler.py
│   │   └── errors.py
│   ├── crud/
│   │   └── crud_task.py
│   ├── db/
│   │   └── models/
│   │       └── tasks.py
│   ├── schemas/
│   │   └── planning.py
│   └── services/
│       └── planning_service.py

database/
└── migrations/
    └── 04_tasks_and_dependencies.sql (Direct SQL update)
```

**Structure Decision**: The backend is a FastAPI monolithic service. The new deterministic scheduler lives in `app/core/scheduler.py` to remain independent of the FastAPI request lifecycle. The database schema is updated directly in the initial migration file `04_tasks_and_dependencies.sql` without a new Alembic migration.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations.*
