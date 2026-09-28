# Implementation Plan: Repository-Wide Architectural Refactor

**Branch**: `[030-repo-wide-refactor]` | **Date**: 2026-09-28 | **Spec**: [specs/030-repo-wide-refactor/spec.md](spec.md)

**Input**: Feature specification from `specs/030-repo-wide-refactor/spec.md`

## Summary

Perform a comprehensive, repository-wide architectural refactor of the Blooming project (Svelte 5, FastAPI, PostgreSQL). The primary goal is structural consistency without intentionally changing observable business behavior. This includes aligning database schema with ORM, moving domain logic out of API routes into services, centralizing frontend state and components, and establishing clear dependency rules.

## Technical Context

**Language/Version**: Python 3.12, TypeScript 5, Rust (Tauri)

**Primary Dependencies**: FastAPI, Svelte 5, Tauri 2, SQLAlchemy, Vite

**Storage**: PostgreSQL (per-table SQL schema)

**Testing**: Pytest (backend), Vitest (frontend)

**Target Platform**: Desktop (Windows/macOS/Linux) via Tauri

**Project Type**: Desktop-app (Svelte + Rust) with an external Python/FastAPI backend

**Performance Goals**: N/A (Keep existing performance profile)

**Constraints**: `Observable business behavior before refactor == Observable business behavior after refactor`

**Scale/Scope**: Entire repository

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
specs/030-repo-wide-refactor/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/      # Thin HTTP handlers
│   ├── services/        # Application/Domain logic
│   ├── repositories/    # Database interactions
│   ├── core/            # Config, errors, security
│   ├── db/
│   │   └── models/      # SQLAlchemy ORM
│   └── ai/              # AI package (llm, nlu, drafting, coach, handlers)
└── tests/
    ├── api/             # HTTP contract tests
    ├── integration/     # Service/DB integration
    └── unit/            # Pure logic

frontend/
├── src/
│   ├── routes/          # Page composition
│   ├── lib/
│   │   ├── features/    # Cohesive domain features (auth, today, goals, etc)
│   │   ├── shared/      # ui, styles, api, types, utils (NO feature dependencies)
│   │   └── platform/    # desktop integration
└── tests/

database/
├── install.sql
├── init/
├── tables/
├── functions/
├── triggers/
└── reference_data/
```

**Structure Decision**: Selected the split backend/frontend/database structure based on user specification and existing repository setup. Refactoring targets clear separation of domain logic from routing (backend), feature modularization without circular dependencies (frontend), and robust schema initialization (database).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations.
