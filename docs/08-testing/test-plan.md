# Test Plan: Blooming MVP

## Objective

Testing establishes that the required MVP blocks work together without compromising deterministic scheduling, user ownership, recovery, desktop reminder presentation, Heart Progress integrity, or presentation-only time/weather behavior. This plan defines intended evidence and does not claim unimplemented tests have passed.

The frozen concept is `../02-product/Blooming-Concept-Updated.md`.

## Coverage

| Area | Critical verification |
|---|---|
| User and Settings | JWT authentication, object ownership, profile/timezone/defaults, quiet hours, widget preferences, PlantType, and weather-location settings. |
| Mr. Bloom | Canonical intent classification in the full application, schema validation, one/two-question clarification discipline, prompt-injection/malformed-output rejection, form fallback, and no widget chat. |
| Daily Planning | Unified ordered PlanBlock output with unchanged fixed events, available-window/deadline containment, dependency/core/deadline ordering, fixed/flexible Tasks, precise breaks/buffers, overload reasons, persistence, and edit validation. |
| Focus and recovery | Timer/pause/resume, canonical outcomes, separate planned/actual time, protected history, fixed events, locked fixed-Task blocks, active-session preservation, explanation, and local countdown after widget hide/sleep. |
| Goals and reminders | Editable roadmaps, downstream-date warning, 20:00 day-before timezone timing, ReminderAction, confirmation before tasks, Tauri local due-time evaluation, tray red-dot, hidden-widget retention. |
| Garden and widget context | One GardenState, HeartEvent idempotency, PlantType switch without reset, WidgetState independent from WidgetContext, composed time/weather layers, fetch-`UNKNOWN` vs disabled-overlay fallback. |

## Test layers

| Layer | Purpose |
|---|---|
| Domain/property | Scheduling, time, Heart Progress, GardenState, and WidgetState invariants. |
| Integration | Transactions, SQLAlchemy mappings, JWT ownership, reminder sync payloads, weather cache, and idempotency. |
| API | Schemas, validation/errors, authorization, structured AI boundary, PlantType switch, and side effects. |
| Desktop/E2E | Today, Goals, Settings, widget states, tray red-dot, recovery, and reminder-action flows on Windows and Linux. |
| AI/security/privacy | Evaluation dataset, schema/injection failures, prompt minimization, secrets/logs, coarse location, and authorization abuse. |

## Release gates

- All critical scheduling/re-planning invariants pass: no overlap, out-of-window/late Task block, altered fixed event or locked fixed-Task block, incorrect Break emission, altered protected history, or merged planned/actual time.
- AI output is validated or rejected in every state-changing path; the manual form works on failure; the widget does not call the LLM continuously.
- Reminder occurrence and ReminderAction persistence are timezone-correct and idempotent. FastAPI is not polled once per second. Hiding the widget does not drop unread due reminders. No OS toast is required to pass.
- Opening the application does not grant Heart Progress. Switching PlantType does not reset Heart Progress or GardenState. Missed work does not erase progress.
- Time and weather do not change scheduler output, reminder due times, or Heart Progress. Unavailable or invalid weather may use `UNKNOWN` with time-only visuals. Disabled weather-aware visuals omit the overlay without requiring `UNKNOWN`.
- No critical authentication, authorization, privacy, data-loss, reminder, or timer defect remains.
- Docker smoke test and the critical end-to-end daily/goal/reminder/garden/widget flows pass on Windows and Linux before release.

## Out of scope for this test release

Google Calendar, calendar replacement, advanced analytics, learned estimates, habits, voice, teams/social features, multiple gardens/inventory/economy, plant death, pet/world/quest systems, OS notifications, email/push, continuous GPS, weather-driven planning, complex animation, multiple agents, LangChain, and LangGraph are excluded features and have no MVP acceptance suite.
