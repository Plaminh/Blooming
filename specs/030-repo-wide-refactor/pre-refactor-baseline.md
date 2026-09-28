# Pre-Refactor Baseline

This document captures the state of the repository before the Phase 1 refactoring begins.

## Backend Automated Tests
**Command**: `pytest tests/unit/`
**Date**: 2026-09-28
**Environment**: Local Windows

**Result**: 
- Passed: 488
- Failed: 0
- Skipped: 0
- Errors: 0
- Duration: 20.45s

**Command**: `pytest -m "not live_llm and not external" tests/` (Integration and DB tests)
**Date**: 2026-09-28
**Environment**: Local Windows

**Result**:
- Passed: N/A
- Failed: N/A
- Status: BLOCKED (Docker daemon not running, unable to start testcontainers)

## Frontend Baseline
**Command**: `npm run test`
**Date**: 2026-09-28
**Result**: 
- Test Files: 58 passed
- Tests: 411 passed
- Errors: 0
- Duration: 84.07s

**Command**: `npm run check`
**Date**: 2026-09-28
**Result**: 
- Passed: svelte-check found 0 errors and 0 warnings

## Database / Bootstrap Baseline
**Result**: BLOCKED
- Docker/PostgreSQL bootstrap: BLOCKED (Docker not running)
- Backend DB connection: BLOCKED (Docker not running)
- Existing schema tests: BLOCKED

## Existing Failures 
- **KNOWN_BASELINE_FAILURE**: 
  - `tests/api/test_assistant_routes.py::test_successful_today_save_completes_planning_session` (IntegrityError: daily_plans_confirmation_valid)
  - `tests/api/test_today_draft.py::test_today_draft_round_trip` (TypeError)
  - `tests/api/test_today_draft.py::test_today_draft_other_user_plan`
  *(Note: these integration tests are currently BLOCKED from running, but are known to be failing in the baseline based on historical data. They will remain failures unless required for refactor to proceed.)*
