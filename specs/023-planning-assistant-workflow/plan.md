# Implementation Plan: 023-planning-assistant-workflow

**Branch**: `023-planning-assistant-workflow` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/023-planning-assistant-workflow/spec.md`

## Summary

Build a production-ready "Mr. Bloom Planning Assistant" workflow by replacing the fake frontend-driven local timeline generation with a backend-driven deterministic preview (`POST /today/preview`). Enhance the `/assistant/chat` endpoint to be context-aware, accept a `session_id` and `current_draft`, and strictly validate the output from the Groq LLM before returning it. Persist the conversations and sessions securely in `planning_sessions` and `planning_messages`, and implement an atomic `POST /today/save` endpoint to persist the finalized day plan.

## Technical Context

**Language/Version**: Python 3.10+, TypeScript 5+

**Primary Dependencies**: FastAPI, SvelteKit, Pydantic, SQLAlchemy, httpx

**Storage**: PostgreSQL (existing `planning_sessions`, `planning_messages`, `daily_plans`, `tasks`, `goals`, `milestones`)

**Testing**: pytest (backend unit/integration tests), vitest/svelte-testing-library (frontend component/store tests)

**Target Platform**: Desktop (Tauri/Rust) and Web

**Project Type**: Full-stack application

**Performance Goals**: LLM calls should gracefully timeout or retry on 429/5xx, remaining within a 30s envelope.

**Constraints**: Strict backward compatibility for API updates (optional fields). The LLM cannot invent constraints, and no raw errors/stacktraces go to the client.

**Scale/Scope**: ~5 new/modified endpoints, ~3 updated frontend components/stores.

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
specs/023-planning-assistant-workflow/
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
│   ├── api/routes/
│   │   ├── assistant.py
│   │   └── today.py
│   ├── core/
│   │   └── scheduler.py
│   ├── schemas/
│   │   ├── assistant.py
│   │   └── today.py
│   └── services/
│       ├── assistant_service.py
│       └── today_service.py
└── tests/
    └── api/

frontend/
├── src/
│   ├── lib/
│   │   ├── features/mr-bloom/
│   │   │   ├── components/
│   │   │   │   └── molecules/ChatComposer.svelte
│   │   │   └── stores/mrBloomStore.ts
│   │   └── features/today/
│   │       ├── components/organisms/TodayTimeline.svelte
│   │       └── timeline.ts
│   └── api.ts
└── tests/
```

**Structure Decision**: The project uses the existing FastAPI + SvelteKit split. No new structural modules are required, as existing modules will be augmented.

## Complexity Tracking

No violations.
