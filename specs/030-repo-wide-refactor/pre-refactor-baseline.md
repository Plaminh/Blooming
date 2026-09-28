# Pre-Refactor Baseline

This document captures the state of the repository before the Phase 1 refactoring begins.

## Backend Automated Tests
**Command**: `pytest tests/unit/ tests/integration/ tests/api/`
**Date**: 2026-09-28
**Environment**: Local Windows

**Result**: 
- Passed: 593
- Failed: 3
- Skipped: 6
- Warnings: 12

**Existing Failures** (Must not be fixed as part of the refactor, these will remain failures unless required for refactor to proceed):
1. `tests/api/test_assistant_routes.py::test_successful_today_save_completes_planning_session` (IntegrityError: daily_plans_confirmation_valid)
2. `tests/api/test_today_draft.py::test_today_draft_round_trip` (TypeError)
3. `tests/api/test_today_draft.py::test_today_draft_other_user_plan`

## Frontend Automated Tests
**Command**: `npm run test`
**Date**: 2026-09-28
**Environment**: Local Windows

**Result**:
- Test Files: 58 passed
- Tests: 411 passed
- Failed: 0

**Typescript Check**
**Command**: `npm run check`
**Result**: 0 errors and 0 warnings (Passed)

## Manual Baseline

These scenarios have NOT RUN yet. They will serve as the manual regression suite during the final verification.

### Authentication
- **ID**: MAN-001
- **Preconditions**: User is logged out.
- **Steps**: Navigate to `/`, enter valid credentials, click Login.
- **Expected Result**: User is authenticated and navigated to `/today`.
- **Status**: NOT RUN

### Onboarding and Settings
- **ID**: MAN-002
- **Preconditions**: User is authenticated, has not completed onboarding.
- **Steps**: Complete onboarding wizard, save timezone and widget preferences.
- **Expected Result**: Preferences persist and user lands on `/today`.
- **Status**: NOT RUN

### Today Plan
- **ID**: MAN-003
- **Preconditions**: User is on `/today`.
- **Steps**: Create a new task draft, view timeline preview, save plan, reload.
- **Expected Result**: Plan saves successfully, timeline matches draft.
- **Status**: NOT RUN

### Mr. Bloom
- **ID**: MAN-004
- **Preconditions**: User is on `/mr-bloom`.
- **Steps**: Send "I want to work on my feature", follow deterministic planning flow, apply patches to Today draft.
- **Expected Result**: Chat routes to coach/drafting, patches apply correctly, draft is updated.
- **Status**: NOT RUN

### Goals
- **ID**: MAN-005
- **Preconditions**: User is on `/goals`.
- **Steps**: Create a new goal with Mr. Bloom, save roadmap, add milestone.
- **Expected Result**: Goal is saved, roadmap displays correctly, milestone is added.
- **Status**: NOT RUN

### Pomodoro
- **ID**: MAN-006
- **Preconditions**: User has an active task.
- **Steps**: Start pomodoro timer, pause, resume, finish.
- **Expected Result**: Timer behaves correctly, result is persisted as a FocusRun.
- **Status**: NOT RUN

### Re-plan
- **ID**: MAN-007
- **Preconditions**: User has completed a pomodoro on a task.
- **Steps**: Trigger re-plan.
- **Expected Result**: Unfinished work is adjusted, completed work is preserved.
- **Status**: NOT RUN

### Garden
- **ID**: MAN-008
- **Preconditions**: User has completed a pomodoro.
- **Steps**: Visit `/garden`, check water/leaves balance, unlock plant.
- **Expected Result**: Rewards are accrued correctly, plant unlocks successfully.
- **Status**: NOT RUN

### Widget
- **ID**: MAN-009
- **Preconditions**: Tauri widget is enabled.
- **Steps**: Show widget, observe time/pomodoro state.
- **Expected Result**: Widget accurately reflects main application state.
- **Status**: NOT RUN
