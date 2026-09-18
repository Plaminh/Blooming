# Implementation Plan: goals-milestones-reminders

**Branch**: `[015-goals-milestones-reminders]` | **Date**: 2026-09-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/015-goals-milestones-reminders/spec.md`

## Summary

Make the existing Goals/Roadmap experience functional with real persisted data. Users will manage goals via Mr. Bloom drafts and manually edit milestones, and due reminders can be loaded and actioned using the existing backend architecture and SvelteKit frontend without requiring AI.

## Technical Context

**Language/Version**: Python 3.10 (Backend), TypeScript (Frontend)

**Primary Dependencies**: FastAPI, SvelteKit, Tauri 2

**Storage**: PostgreSQL via SQLAlchemy

**Testing**: pytest (Backend), vitest/playwright (Frontend)

**Target Platform**: Desktop (Windows/Linux)

**Project Type**: Desktop-app (Tauri + SvelteKit + FastAPI)

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
specs/015-goals-milestones-reminders/
├── plan.md              # This file
├── research.md          
├── data-model.md        
└── quickstart.md        
```

### Source Code

```text
backend/
├── app/
│   ├── api/routes/
│   │   ├── goals.py
│   │   └── reminders.py
│   ├── schemas/
│   │   ├── goals.py
│   │   └── reminders.py
│   └── services/
│       ├── goals_service.py
│       └── reminders_service.py
└── tests/
    └── api/routes/
        ├── test_goals.py
        └── test_reminders.py

frontend/
├── src/
│   ├── lib/features/goals/
│   │   ├── stores/
│   │   │   └── goalsStore.ts
│   │   └── components/
│   │       └── organisms/
│   │           └── DueRemindersPanel.svelte
│   └── routes/(app)/goals/
│       └── +page.svelte
```

## Phases

### Phase 1: Repository Audit & Contracts

- **Identify reusable files**: 
  - `models/goals.py`, `models/reminders.py`, `models/daily_plans.py`, `models/tasks.py` (No database migrations required).
  - Existing SvelteKit components (`MyGoalsPanel.svelte`, `GoalDetailsPanel.svelte`, `GoalsRightRail.svelte`).
  - `api.ts` fetch wrapper.
- **Identify gaps**:
  - Empty `routes/goals.py`.
  - Missing `schemas/goals.py`, `schemas/reminders.py`.
  - Missing `services/goals_service.py`, `services/reminders_service.py`.
  - Missing `DueRemindersPanel.svelte` for the goals screen.
  - Frontend mock data (`FIXTURE_GOALS`) needs to be replaced with real API calls via a store.
- **Contracts**: 
  - Define Request/Response schemas for Goals CRUD, Milestones CRUD, and Reminder Actions in Pydantic models.

### Phase 2: Backend API (Goals & Milestones)

- **Create Schemas**: `GoalCreate`, `GoalUpdate`, `GoalResponse`, `MilestoneCreate`, `MilestoneUpdate`, `MilestoneResponse` in `schemas/goals.py`.
- **Create Service**: `goals_service.py` to handle DB operations (CRUD).
  - Include strict ownership checks (`user_id` matching).
  - Validate milestone positions to prevent conflicts.
- **Create Routes**: Implement endpoints in `routes/goals.py`:
  - `GET /goals/`
  - `POST /goals/`
  - `GET /goals/{goal_id}`
  - `PUT /goals/{goal_id}`
  - `DELETE /goals/{goal_id}`
  - `POST /goals/{goal_id}/milestones/`
  - `PUT /goals/{goal_id}/milestones/{milestone_id}`
  - `DELETE /goals/{goal_id}/milestones/{milestone_id}`
- **Verification**: Write tests in `test_goals.py` covering CRUD, validation, and ownership isolation.

### Phase 3: Backend API (Due Reminders & Actions)

- **Create Schemas**: `ReminderResponse`, `ReminderActionRequest` in `schemas/reminders.py`.
- **Create Service**: `reminders_service.py`.
  - Fetch due reminders: `status IN ('SCHEDULED', 'DUE')` and `due_at <= now()`.
  - Execute actions:
    - `CREATE_PLAN`: Create a `Task` for the milestone, create a Draft `DailyPlan`, and mark `Reminder` as `COMPLETED`.
    - `MARK_COMPLETED`: Set `Reminder` to `COMPLETED`, set `Milestone` status to `COMPLETED`.
    - `MOVE_MILESTONE`: Update `Milestone.due_at`, adjust `Reminder.due_at` and `Reminder.original_due_at`, record a `ReminderAction`.
    - `REMIND_LATER`: Update `Reminder.due_at` to future time, record `ReminderAction` with `REMIND_LATER`.
- **Idempotency**: Prevent duplicate action execution if reminder is already completed/dismissed.
- **Create Routes**: Implement in `routes/reminders.py` (and register in `main.py`):
  - `GET /reminders/due`
  - `POST /reminders/{reminder_id}/actions`
- **Verification**: Write tests in `test_reminders.py` testing due filtering logic and each action's idempotency and state changes.

### Phase 4: Frontend Integration (Goals & Milestones)

- **Create Store**: `lib/features/goals/stores/goalsStore.ts` using Svelte runes/stores to wrap `api.ts`.
  - Methods: `loadGoals()`, `createGoal()`, `updateGoal()`, `deleteGoal()`.
  - Milestone methods: `addMilestone()`, `updateMilestone()`, `deleteMilestone()`.
- **Update UI**: 
  - Refactor `routes/(app)/goals/+page.svelte` to call `loadGoals()` on mount instead of using `FIXTURE_GOALS`.
  - Wire up edit/delete handlers in `MyGoalsPanel`, `GoalDetailsPanel`, and `GoalsRightRail`.
  - Update local state immediately after a successful mutation without page reload.
  - Implement form submission states (loading, success, error) and prevent duplicate submissions.

### Phase 5: Frontend Integration (Reminders)

- **Create Component**: `DueRemindersPanel.svelte` in `organisms`.
  - Visually style it similarly to `NextMilestonePanel`.
  - Render a list of due reminders with buttons for "Create Plan", "Mark Completed", "Move", "Remind Later".
- **Store Updates**: Add `loadDueReminders()` and `executeReminderAction()` to `goalsStore.ts`.
- **Update GoalsRightRail**: Embed `DueRemindersPanel` at the top of the rail, showing it only if there are due reminders.
- **Verification**: Run frontend with backend locally. Perform the demo script: load goals, manage goals/milestones, see due reminders, execute actions, and verify persistence across reloads.
