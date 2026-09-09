# Test Plan: Blooming MVP

## Objective

Testing establishes that the six required MVP blocks work together without compromising deterministic scheduling, user ownership, recovery, reminder delivery, or non-punitive plant behavior. This plan defines intended evidence and does not claim unimplemented tests have passed.

## Coverage

| Area | Critical verification |
|---|---|
| User and Settings | JWT authentication, object ownership, profile/timezone/defaults, email setting, and Rest Mode configuration. |
| Mr. Bloom | Canonical intent classification, schema validation, one/two-question clarification discipline, prompt-injection/malformed-output rejection, and form fallback. |
| Daily Planning | Unified ordered PlanBlock output with unchanged fixed events, available-window/deadline containment, dependency/core/deadline ordering, fixed/flexible Tasks, precise breaks/buffers, overload reasons, persistence, and edit validation. |
| Focus and recovery | Timer/pause/resume, canonical outcomes, separate planned/actual time, protected history, fixed events, locked fixed-Task blocks, active-session preservation, and explanation. |
| Goals and reminders | Editable roadmaps, downstream-date warning, 20:00 day-before timezone timing, actions, confirmation before tasks, email/in-app idempotency. |
| Plant and rest | One active plant, Water Reserve decay after abandonment, meaningful activity, no direct missed-work damage, Rest Mode pause, death preservation/new seed, and asset mapping. |

## Test layers

| Layer | Purpose |
|---|---|
| Domain/property | Scheduling, time, plant, and state-transition invariants. |
| Integration | Transactions, SQLAlchemy mappings, JWT ownership, jobs, email adapter, and idempotency. |
| API | Schemas, validation/errors, authorization, structured AI boundary, and side effects. |
| UI/E2E | Home/Mr. Bloom, Today, Goals, authentication/settings, recovery, and reminder-action flows. |
| AI/security/privacy | Evaluation dataset, schema/injection failures, prompt minimization, secrets/logs, and authorization abuse. |

## Release gates

- All critical scheduling/re-planning invariants pass: no overlap, out-of-window/late Task block, altered fixed event or locked fixed-Task block, incorrect Break emission, altered protected history, or merged planned/actual time.
- AI output is validated or rejected in every state-changing path; the manual form works on failure.
- Reminder occurrence and delivery are timezone-correct and idempotent.
- A missed task, longer task, actively re-planned skip, or delayed recovering milestone does not directly damage plant health; abandonment and Rest Mode rules pass.
- No critical authentication, authorization, privacy, data-loss, reminder, or timer defect remains.
- Docker smoke test and the critical end-to-end daily/goal/reminder/plant flows pass before release.

## Out of scope for this test release

Google Calendar, calendar replacement, advanced analytics, learned estimates, habits, voice, teams/social features, multiple plants/inventory/economy, pet/world/quest systems, complex animation/web push, multiple agents, LangChain, and LangGraph are excluded features and have no MVP acceptance suite.
