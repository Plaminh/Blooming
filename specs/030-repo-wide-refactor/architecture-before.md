# Pre-Refactor Architecture Snapshot

This document captures the physical state and structure of the repository before the Phase 1 refactoring begins.

## Frontend

**Structure and Organization:**
- **Top-Level Routes**: SvelteKit routes live in `src/routes/`. Authenticated application routes are grouped under `(app)/` (e.g., `today`, `goals`, `mr-bloom`, `settings`, `statistics`, `garden-selection`).
- **Feature Modules**: Business domains are separated into `src/lib/features/` (e.g., `authentication`, `companion-widget`, `today`, `goals`, `mr-bloom`). However, atoms/molecules/organisms hierarchies create deep nesting.
- **Shared Modules**: Shared UI primitives and core utils are in `src/lib/shared/`. Currently, there are mixing concerns and potential bleeding of feature logic.
- **Platform Integration**: Tauri desktop bindings exist in `src/lib/platform/desktopWindow.ts`.
- **State Management**: Mixed approach. Uses legacy Svelte stores (e.g., `authStore`, `clockStore`), Svelte 5 rune classes (`.svelte.ts`) predominantly for feature models (e.g., `TodayState.svelte.ts`), and some route-local state.
- **API Types**: Kept close to the features (e.g., `src/lib/features/today/types.ts`).

## Backend

**Structure and Organization:**
- **API Routes**: Located in `app/api/routes/`. The Assistant route (`assistant.py`) contains significant session and database orchestration directly in the handler.
- **Services**: Located in `app/services/` (e.g., `assistant_service.py`, `today_service.py`). The Today domain's high complexity is primarily concentrated in `today_service.py` rather than directly in the route.
- **CRUD / Persistence**: Very light directory `app/crud/` (only `crud_daily_plan.py`, `crud_focus.py`, `crud_task.py`). Most DB access uses SQLAlchemy sessions directly in services/routes.
- **DB Models**: SQLAlchemy declarative models are in `app/db/models/`.
- **AI Modules**: Contained in `app/ai/`. Heavily structured orchestrator (`router.py`, `coach.py`, `parser.py`, `handlers/`).
- **Core**: Cross-cutting concerns in `app/core/` (config, security, rate limit, scheduler, runtime).
- **High-Risk Modules**: `TodayService`, `AssistantService`, and `planning.py` have high complexity and significant cross-dependencies.

## Database

**Structure and Organization:**
- **Installer**: `database/install.sql` is the authoritative fresh schema installer.
- **Tables**: Managed manually via individual SQL files inside `database/tables/` (currently 24 SQL files).
- **Initialization / Seed**: Handled via `00_init.sql` and `99_seed.sql`. Required reference data is currently loaded through the existing seed/bootstrap SQL.
- **SQLAlchemy Location**: Mapped models in `backend/app/db/models/`. No Alembic migration generation is in place; the database is considered SQL-first.
- **Existing Schema Smoke Tests**: A transactional `00_schema_smoke_test.sql` lives in `database/tests/` to verify baseline constraints.

## Tests

**Structure and Organization:**
- **Frontend**: Tests are co-located next to the implementation files using Vitest (`*.test.ts`).
- **Backend**: Segmented heavily in `backend/tests/`:
  - `unit/`: AI logic, parsing, and isolated pure functions.
  - `services/`: Business logic integration.
  - `api/`: Endpoint and contract integration tests.
  - `infrastructure/`: Fixture isolation and database safety rules.
  - `integration/`: Live / external integrations (e.g., LLM network calls in `test_today_llm_live.py`).
