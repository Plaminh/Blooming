# Phase 1: Data Model & State

This feature is a **structural refactor**, meaning no *new* entities are introduced to the core business logic. Instead, the focus is on reorganizing existing data models, reducing duplicate definitions, and aligning schemas.

## Core Entities Reorganized

### Backend Organization
The SQLAlchemy models must precisely match the PostgreSQL schema.
- **Location**: `backend/app/db/models/`
- **Goal**: Full parity verification between `tables/*.sql` and Python models.

### Frontend Type Contracts
- **Location**: `frontend/src/lib/shared/types/` (and potentially `lib/shared/api/types/`)
- **Goal**: Centralize type definitions that are currently scattered across API files, feature files, and test fixtures. Eliminate duplicate DTOs between frontend and backend.

## Key Target Domains
The following domains will have their contracts audited and normalized:

1. **User / Auth / Settings**: User profile and application settings.
2. **Planning**: `TodayDraft`, `DailyPlan`, `Task`, `PlanBlock`.
3. **Goals**: `Goal`, `Milestone`.
4. **Focus / Timers**: `FocusRun`.
5. **Reminders**: `Reminder` (and due-time lookup).
6. **Garden**: `GardenState`, `Water`, `Leaves`.
7. **AI / Chat**: `PlanningSession`, `PlanningMessage`, `AIUsage`.

## Validation Rules
- **Server-Owned**: Fields owned by the server (e.g., timestamps, IDs generated post-insert) remain server-owned. The frontend must not invent persistence fields.
- **API Schemas**: Pydantic models must not expose ORM-specific details (like lazy-loading markers) to the frontend.
