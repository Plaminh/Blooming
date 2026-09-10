# Test Cases: Connected MVP

These cases supplement the deterministic Quick Planning suite. They are expected test design, not execution evidence.

## Authentication and AI boundary

| ID | Scenario | Expected result |
|---|---|---|
| TC-USER-001 | A registered user calls a user-owned endpoint with a valid JWT; another user requests the same object. | Owner succeeds; non-owner is denied without exposing the object. |
| TC-AI-001 | Mr. Bloom returns malformed, injected, or schema-invalid state-changing output. | Backend rejects it; no DailyPlan/Goal/Reminder/GardenState changes; structured form remains available. |
| TC-AI-002 | The widget is visible during planning. | The widget does not expose free-form chat and does not call the language model continuously. |

## Focus and recovery

| ID | Scenario | Expected result |
|---|---|---|
| TC-FOCUS-001 | A FocusRun ends with each canonical outcome. | Only `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, and `SKIP` are accepted; planned and actual time remain separate. `FINISHED_EARLY` does not automatically trigger re-planning. |
| TC-FOCUS-002 | The user selects a task on Today and starts Pomodoro. | FastAPI stores `started_at` and `expected_end_at`; the widget enters WidgetState `FOCUSING`; Tauri calculates remaining time locally. |
| TC-REPLAN-001 | A re-plan follows a session overrun with completed work, a fixed event, a locked fixed-Task block, and an active session. | Completed FocusRuns/actual history/fixed event/locked fixed-Task block remain unchanged; only unfinished flexible future blocks move; explanation is returned. |
| TC-REPLAN-002 | A manual or conversational time edit would overlap a block or fixed event. | Deterministic validation rejects the edit and preserves the saved Daily Plan. |

## Goals and reminders

| ID | Scenario | Expected result |
|---|---|---|
| TC-GOAL-001 | A user moves a milestone with later milestones. | The system warns about downstream dates and offers equal-day shifting; it does not silently move them. |
| TC-REM-001 | A milestone deadline is tomorrow in the user's IANA timezone. | The reminder is due at 20:00 local time and supports `CREATE_PLAN`, `MARK_COMPLETED`, `MOVE_MILESTONE`, and `REMIND_LATER`. |
| TC-REM-002 | Tauri retries synchronization after a temporary disconnection. | At most one ReminderAction is persisted per occurrence; a Daily Plan receives tasks only after confirmation; FastAPI is not polled once per second. |
| TC-REM-003 | A reminder becomes due while the widget is `HIDDEN`. | The reminder stays due and unread; the tray red-dot remains; the bubble appears when the widget is reopened. No OS toast is shown. |

## Garden, plant, and widget context

| ID | Scenario | Expected result |
|---|---|---|
| TC-PLANT-001 | User opens the app without completing eligible work. | No HeartEvent is created. |
| TC-PLANT-002 | A deadline passes, a plan is incomplete, work overruns, a skip is actively re-planned, or a milestone is delayed during recovery. | Heart Progress and GardenState are not erased or punished. |
| TC-PLANT-003 | The user switches PlantType from `POTHOS` to `CACTUS`. | Artwork changes; Heart Progress, GardenState stage, and history are unchanged. |
| TC-WIDGET-001 | Local time corresponds to night and weather is `RAINY`. | WidgetState remains the functional state; visuals compose `NIGHT` + `RAINY` layers. Scheduler output, reminder due times, and Heart Progress are unchanged. |
| TC-WIDGET-002 | Weather fetch fails or returns invalid data while weather-aware visuals are on. | WeatherContext may be `UNKNOWN`; UI uses time-only presentation. Scheduling, reminders, and Heart Progress are unchanged. |
| TC-WIDGET-002b | Weather-aware visuals are turned off. | No weather overlay is applied. WidgetContext is time-only. WeatherContext is not required to be `UNKNOWN`. |
| TC-WIDGET-003 | WidgetState follows reminder then focus. | `DEFAULT → REMINDER → DEFAULT` holds. Focus follows `DEFAULT → FOCUSING → SESSION_RESULT`, then `DONE → DEFAULT`, `FINISHED_EARLY → DEFAULT`, or `NEED_MORE_TIME` / `SKIP` → re-plan → `DEFAULT`. Outcomes are chosen in `SESSION_RESULT`. `FINISHED_EARLY` does not automatically trigger re-planning. `HIDDEN` destroys the widget window while Tauri core remains. |
