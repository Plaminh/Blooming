# Implementation Plan: Pomodoro and Re-planning

**Branch**: `014-pomodoro-replanning` | **Date**: 2026-09-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/014-pomodoro-replanning/spec.md`

## Summary

Implement Pomodoro session management (start, pause, resume, finish) and subsequent schedule re-planning using the existing FastAPI/SQLAlchemy backend and SvelteKit/Tauri frontend architecture. The frontend computes live countdowns, while the backend maintains the authoritative timestamps and executes deterministic rule-based re-planning on flexible incomplete tasks.

## Technical Context

**Language/Version**: Python 3.10+ (Backend), TypeScript 5+ (Frontend)
**Primary Dependencies**: FastAPI, SvelteKit, Tauri 2
**Storage**: PostgreSQL via SQLAlchemy and Alembic
**Testing**: pytest (Backend), svelte-check / vitest (Frontend)
**Target Platform**: Desktop app
**Project Type**: Web/Desktop Application (Frontend + Backend)
**Performance Goals**: Sub-200ms API response for re-planning and state changes
**Constraints**: Demo-ready initial version; no background sync or AI required
**Scale/Scope**: Local desktop usage

## Constitution Check

*GATE: Passed*

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite, FastAPI/Python/Pydantic, and PostgreSQL/SQLAlchemy boundaries?
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully?
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

## Implementation Plan details

### 1. Existing-code assessment

The actual repository already contains a significant portion of the architecture designed for this feature:
- **Backend Models**: `FocusRun` and `FocusRunEvent` exist in `app.db.models.focus`. `Task` and `PlanBlock` exist with necessary properties.
- **Backend Services & CRUD**: `FocusService` (`app/services/focus_service.py`) and `TodayService` (`app/services/today_service.py`) contain the logic for session management and re-planning respectively.
- **Backend API**: `app/api/routes/focus.py` provides the exact endpoints needed (`/start`, `/pause`, `/resume`, `/finish`, `/active`).
- **Frontend Components**: `today/+page.svelte` initiates the session via API and invokes the Tauri `companion-widget`.
- **Frontend Widget**: `widget/+page.svelte` correctly computes the countdown independently and supports transitions (`focusing`, `paused`, `ending`).

*Conflicts/Missing items*:
Backend tests for the focus routes and replanning do not fully cover the current implementation requirements.

### 2. Session state machine

- **Start**: Creates a new session in `FOCUSING` state. Validates no existing active session.
- **Pause**: Transitions from `FOCUSING` to `PAUSED`. Sets `paused_at`.
- **Resume**: Transitions from `PAUSED` to `FOCUSING`. Adds `now - paused_at` to `total_paused_seconds` and extends `expected_end_at`.
- **Finish**: Transitions to `ENDED`. Logs actual duration and assigns an outcome. Rejects duplicate calls if state is already `ENDED`.
- **Restore**: On refresh, frontend queries `GET /focus/active`. If `FOCUSING` or `PAUSED`, it instantly restores the timer logic without losing state.

### 3. Time calculation

- Backend uses timezone-aware UTC `datetime.now(timezone.utc)`.
- The frontend computes elapsed time dynamically:
  - If `FOCUSING`: `elapsedSeconds = (now - startedAt) - total_paused_seconds`.
  - If `PAUSED`: `elapsedSeconds = (pausedAt - startedAt) - total_paused_seconds`.
- Remaining time is `planned_focus_seconds - elapsedSeconds`, floored at 0.
- Actual duration excludes pause time automatically through this math.

### 4. Outcome behavior

- **DONE**: `FocusRun` outcome set to `DONE`, `Task` status set to `COMPLETED`.
- **FINISHED_EARLY**: `FocusRun` outcome set to `FINISHED_EARLY`, records shorter `actual_duration_seconds`, `Task` status set to `COMPLETED`.
- **NEED_MORE_TIME**: `FocusRun` outcome set to `NEED_MORE_TIME`, `Task` status remains `PENDING`.
- **SKIP**: `FocusRun` outcome set to `SKIP`, `Task` status set to `SKIPPED`.

### 5. Re-planning algorithm

Algorithm located in `TodayService.replan_today`:
1. Identifies "preserved" plan blocks: any past entries, completed/skipped/cancelled tasks, and `FIXED` schedule types.
2. Identifies flexible tasks (incomplete, flexible scheduling, not past).
3. Uses the `DeterministicScheduler` to place the flexible tasks in remaining `availability_windows` from `now` onwards, avoiding preserved blocks (which act as obstacles).
4. Creates new `PlanBlock` records for the newly scheduled times.
5. Unscheduled tasks gracefully do not receive plan blocks, inherently serving as "overflow" tasks (visible via main task list but missing from the timeline).

### 6. Backend design

- **Routes**: `/focus/start`, `/focus/pause`, `/focus/resume`, `/focus/finish`, `/focus/active`.
- **Transaction boundary**: The `finish_session` method performs state transition, updates the task, and triggers `replan_today` (which cascades to schedule changes) within consecutive DB commits/flushes.
- **Failures**: Concurrent session starts throw `ValidationError` (HTTP 400).

### 7. Frontend design

- **API Client**: `api.get`, `api.post` are used to communicate with the backend.
- **State Management**: Handled via local Svelte `$state` and `$derived` inside the standalone Tauri widget.
- **UI**: The standalone widget window presents the sprite atlas and interactive buttons mapped exactly to the presentation states (`FocusingPresentation`, `PausedPresentation`, `EndingPresentation`).

### 8. Testing and verification

- Pytest suite covering the state transition lifecycle (`start` -> `pause` -> `resume` -> `finish`).
- Pytest verification for the four outcomes (`DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, `SKIP`).
- Verify replanning protection (ensuring fixed blocks are untouched).
- Svelte-check for frontend type strictness on the Presentation types.

## Project Structure

### Documentation (this feature)

```text
specs/014-pomodoro-replanning/
├── plan.md              # This file
├── data-model.md        
├── contracts/
│   └── focus-api.md     
├── quickstart.md        
└── tasks.md             # Phase 2 output
```

### Source Code

```text
backend/
├── app/
│   ├── api/routes/focus.py
│   ├── crud/crud_focus.py
│   ├── db/models/focus.py
│   ├── schemas/focus.py
│   └── services/focus_service.py
└── tests/
    └── api/routes/test_focus.py

frontend/
├── src/
│   ├── lib/features/companion-widget/
│   └── routes/(app)/today/+page.svelte
```
