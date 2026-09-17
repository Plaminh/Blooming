# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement the backend persistence, transactional ledger, and API endpoints for the Garden and Reward loop. Introduce Water and Leaves currencies. Award 1 Water for completed Pomodoros, 1 Leaf for completed Tasks/Milestones. Allow unlocking, selecting, and watering plants using real data, calculating vitality lazily on read.

## Technical Context

**Language/Version**: Python 3.10+, TypeScript 5.0+

**Primary Dependencies**: FastAPI, SQLAlchemy, SvelteKit, Tauri 2

**Storage**: PostgreSQL

**Testing**: pytest, Vitest

**Target Platform**: Windows and Linux Desktop

**Project Type**: Desktop application (Tauri + SvelteKit + FastAPI backend)

**Performance Goals**: Fast UI updates without background jobs for vitality

**Constraints**: Strict isolation of UI logic and backend authority. Deterministic vitality calculation. Atomic reward transactions.

**Scale/Scope**: Single user per desktop installation. No external APIs or heavy load.

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
specs/016-garden-rewards/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/routes/
│   ├── db/models/
│   ├── schemas/
│   └── services/
└── tests/

frontend/
├── src/
│   ├── lib/features/garden-selection/
│   └── routes/(app)/garden-selection/
```

**Structure Decision**: Web application layout (backend/frontend). Using existing modules where possible, adding/updating endpoints in backend and connecting viewmodels in frontend.

## Implementation Phases

### Phase 1: Repository and Schema Audit
- **Files**: `backend/app/db/models/garden.py`
- **Reuse**: The existing `HeartEvent` model concept as the basis for reward idempotency.
- **Changes**: Add new `Plant` and `PlantOwnership` models. Add `water_balance`, `leaves_balance`, `selected_plant_id`, `last_watered_at` to `GardenState`. Rename/refactor `HeartEvent` into `RewardEvent` with `resource_type`.
- **Risks**: Modifying existing active tables requires careful SQL schema updates to avoid data loss.

### Phase 2: Centralized Economy and Vitality Rules
- **Files**: `backend/app/core/economy.py` (New)
- **Changes**: Define constants: `WATER_PER_POMODORO = 1`, `LEAVES_PER_TASK = 1`, `VITALITY_MAX = 100`, `VITALITY_DECAY_PER_DAY = 10`, `WATERING_COST = 1`.
- **Dependencies**: None.
- **Verification**: Ensure constants are used across services instead of hardcoding.

### Phase 3: Ledger and Database Constraints
- **Files**: `backend/app/db/models/garden.py`
- **Changes**: Set unique constraints on `(user_id, plant_id)` in ownership, unique `idempotency_key` on rewards. Check constraints for `water_balance >= 0` and `leaves_balance >= 0`.
- **Verification**: `SQL manual update`, test migrations.

### Phase 4: Garden State and Catalog APIs
- **Files**: `backend/app/api/routes/garden.py`, `backend/app/schemas/garden.py`, `backend/app/services/garden_service.py`
- **Changes**: Endpoints for `GET /api/garden`, mapping `GardenState` and `Plant` ownerships.
- **Verification**: API returns correct shape including catalog availability.

### Phase 5: Unlock, Select, and Water Transactions
- **Files**: `backend/app/api/routes/garden.py`, `backend/app/services/garden_service.py`
- **Changes**: Endpoints for unlock, select, and water. Implement atomic deductions and `last_watered_at` updates.
- **Verification**: Test insufficient funds, duplicate unlocks, successful deductions.

### Phase 6: Pomodoro Reward Integration
- **Files**: `backend/app/services/focus_service.py`
- **Changes**: When transitioning `FocusRun` to `status='ENDED'` with `outcome` in (`DONE`, `NEED_MORE_TIME`, `FINISHED_EARLY`), create a `RewardEvent` for Water and update `water_balance`.
- **Verification**: Verify idempotency key (e.g., `focus_run_id_water`) prevents duplicate rewards.

### Phase 7: Task and Milestone Reward Integration
- **Files**: `backend/app/services/task_service.py`, `backend/app/services/goals_service.py`
- **Changes**: During task/milestone completion transition, award Leaves if not already rewarded.
- **Verification**: Tasks reopening and recompleting do not grant extra Leaves.

### Phase 8: Frontend Garden Integration
- **Files**: `frontend/src/lib/features/garden-selection/model/state.svelte.ts`, `.../GardenSelectionContent.svelte`
- **Changes**: Replace `INITIAL_GARDEN_STATE` mock with real API calls via a `GardenService`. Bind balances, plant lock status, and active selection.
- **Verification**: UI displays real data and actions trigger API calls successfully.

### Phase 9: Focused Tests and Demo Verification
- **Files**: `backend/tests/api/test_garden.py`, `frontend/src/.../GardenPanel.test.ts`
- **Changes**: Add unit tests for vitality formula and atomic balances.
- **Verification**: Run the full manual demo checklist in the spec.

### Phase 10: Final Cleanup and Validation
- **Changes**: Run linters, formatters, type checks. Ensure no console errors and no unhandled promise rejections.
