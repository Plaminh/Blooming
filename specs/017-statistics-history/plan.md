# Implementation Plan: Statistics and Plan History

**Branch**: `[017-statistics-history]` | **Date**: 2026-09-17 | **Spec**: [specs/017-statistics-history/spec.md](./spec.md)

**Input**: Feature specification from `/specs/017-statistics-history/spec.md`

## Summary

Implement backend aggregation routes for focus time, plan completion, and plan history, replacing the mock data on the Statistics screen with live, user-scoped data. The frontend `PlanHistoryPanel` will be updated to fetch paginated/filtered data from the new API.

## Technical Context

**Language/Version**: Python 3.12, TypeScript 5
**Primary Dependencies**: FastAPI, SQLAlchemy, Svelte 5
**Storage**: PostgreSQL
**Testing**: pytest
**Target Platform**: Desktop (Windows/Linux) via Tauri
**Project Type**: Desktop app
**Performance Goals**: Fast aggregations without N+1 queries.
**Constraints**: Scoped to authenticated user, accurate timezone handling.
**Scale/Scope**: Real-time aggregation for a single user's history.

## Constitution Check

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite, FastAPI/Python/Pydantic, and PostgreSQL/SQLAlchemy boundaries?
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully?
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

## Project Structure

### Documentation (this feature)

```text
specs/017-statistics-history/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/routes/statistics.py
│   ├── schemas/statistics.py
│   └── services/statistics_service.py
└── tests/
    └── api/routes/test_statistics.py

frontend/
├── src/
│   ├── lib/features/statistics/
│   │   ├── api/statistics.api.ts
│   │   ├── types.ts
│   │   └── components/organisms/PlanHistoryPanel.svelte
│   └── routes/(app)/statistics/+page.svelte
```

**Structure Decision**: Add statistics domain module in backend (`routes`, `schemas`, `services`) and hook up existing frontend components via a new API client in `frontend/src/lib/features/statistics/api/statistics.api.ts`.
