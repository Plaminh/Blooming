# Test Cases: Connected MVP

These cases supplement the deterministic Quick Planning suite. They are expected test design, not execution evidence.

## Authentication and AI boundary

| ID | Scenario | Expected result |
|---|---|---|
| TC-USER-001 | A registered user calls a user-owned endpoint with a valid JWT; another user requests the same object. | Owner succeeds; non-owner is denied without exposing the object. |
| TC-AI-001 | Mr. Bloom returns malformed, injected, or schema-invalid state-changing output. | Backend rejects it; no plan/goal/reminder/plant state changes; structured form remains available. |

## Focus and recovery

| ID | Scenario | Expected result |
|---|---|---|
| TC-FOCUS-001 | A FocusRun ends with each canonical outcome. | Only `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, and `SKIP` are accepted; planned and actual time remain separate. |
| TC-REPLAN-001 | A re-plan follows a session overrun with completed work, a fixed event, a locked fixed-Task block, and an active session. | Completed FocusRuns/actual history/fixed event/locked fixed-Task block remain unchanged; only unfinished flexible future blocks move; explanation is returned. |
| TC-REPLAN-002 | A manual or conversational time edit would overlap a block or fixed event. | Deterministic validation rejects the edit and preserves the saved plan. |

## Goals and reminders

| ID | Scenario | Expected result |
|---|---|---|
| TC-GOAL-001 | A user moves a milestone with later milestones. | The system warns about downstream dates and offers equal-day shifting; it does not silently move them. |
| TC-REM-001 | A milestone deadline is tomorrow in the user's IANA timezone. | The reminder is due at 20:00 local time and supports `CREATE_TOMORROWS_PLAN`, `MARK_COMPLETED`, `MOVE_MILESTONE`, and `REMIND_LATER`. |
| TC-REM-002 | The reminder job retries an occurrence after a partial delivery failure. | At most one in-app/email delivery is recorded per idempotency key; a Daily Plan receives tasks only after confirmation. |

## Plant and Rest Mode

| ID | Scenario | Expected result |
|---|---|---|
| TC-PLANT-001 | User opens the app without meaningful activity. | No water, growth, or RewardEvent is created. |
| TC-PLANT-002 | A deadline passes, a plan is incomplete, work overruns, a skip is actively re-planned, or a milestone is delayed during recovery. | Plant health does not directly deteriorate. |
| TC-PLANT-003 | No meaningful activity occurs for the configured prolonged period. | Water Reserve decreases deterministically and may progress health through `DRY`, `WILTING`, `CRITICAL`, then `DEAD`. |
| TC-PLANT-004 | Rest Mode is active while the decay job runs. | Water Reserve decay, growth, and wilting are paused; expected return date is retained when provided. |
| TC-PLANT-005 | Water Reserve is depleted through all health stages. | Dead plant and user progress history remain; no account/task/goal deletion occurs and a new seed is available. |
