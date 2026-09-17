# Implementation Plan: API Integration

**Branch**: `[018-api-integration]` | **Date**: 2026-09-17 | **Spec**: [specs/018-api-integration/spec.md](./spec.md)

**Input**: Feature specification from `/specs/018-api-integration/spec.md`

## Summary

Integrate all existing Blooming frontend screens with the local FastAPI backend and PostgreSQL database. This involves standardizing the shared API client to automatically prefix requests and handle endpoints consistently, updating all feature modules to consume real API endpoints while discarding mock implementations, mapping backend response payloads correctly to frontend state stores, and ensuring proper UI states (loading, errors, success, empty data) without compromising existing UI/UX and Tauri runtime behavior.

## Technical Context

**Language/Version**: TypeScript 5+ (Frontend), Python 3.11+ (Backend)

**Primary Dependencies**: SvelteKit, FastAPI, Pydantic, Tauri 2

**Storage**: PostgreSQL via SQLAlchemy (Backend)

**Testing**: Vitest (Frontend unit), Pytest (Backend)

**Target Platform**: Tauri 2 Desktop App

**Project Type**: Desktop Application (SvelteKit + FastAPI)

**Performance Goals**: Fast UI updates with real-time feedback; frontend-handled Pomodoro counting.

**Constraints**: Backend API endpoints must exactly match existing definitions. No new tables or schema changes unless required to fix mismatches.

**Scale/Scope**: Frontend state reconciliation across 8 key areas: Auth, Onboarding, Today, Focus, Goals, Garden, Settings, Statistics.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

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
specs/018-api-integration/
├── plan.md              # This file
├── data-model.md        # Frontend state and API endpoint mappings
├── quickstart.md        # Validation guide
└── tasks.md             # To be generated
```

### Source Code

The implementation spans both the SvelteKit frontend and FastAPI backend without restructuring existing directories:

```text
backend/app/
├── api/routes/
└── schemas/

frontend/src/
├── lib/api.ts
├── lib/features/
│   ├── authentication/
│   ├── companion-widget/
│   ├── garden-selection/
│   ├── goals/
│   ├── onboarding-setup/
│   ├── settings/
│   ├── statistics/
│   └── today/
└── routes/
```

**Structure Decision**: The project maintains its existing SvelteKit frontend (Tauri desktop) and FastAPI backend boundaries. Changes are constrained to modifying API requests in frontend stores/components to map strictly to existing backend routers. No broad refactoring is introduced.
