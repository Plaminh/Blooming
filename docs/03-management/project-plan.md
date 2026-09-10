# Project Plan

## Delivery approach

Blooming is a solo modular-monolith project delivered in small vertical slices. The project retains the required MVP blocks; delivery order is a risk-control decision, not a scope exclusion. `product-backlog.md` is the source of planned scope and priority. The frozen concept is `../02-product/Blooming-Concept-Updated.md`. No completion status is implied by this plan.

## Delivery sequence

| Phase | Outcome | Dependencies and exit evidence |
|---|---|---|
| 1. Foundation | Dockerized FastAPI/PostgreSQL, JWT/auth, user settings, timezone model, deterministic scheduler | Unified PlanBlock, deadline, fixed/flexible Task, Break, and ownership invariants are automated |
| 2. Daily planning | Structured planning, Reality Check, timeline, persistence, overload and edits | Valid DailyPlans are non-overlapping, honest, and editable |
| 3. Conversational planning | Full-application Mr. Bloom Task Draft, clarification, explanations, and form fallback | AI output is validated before state changes; widget has no chat |
| 4. Focus and recovery | Today task selection, FocusRun, widget countdown, outcomes, and re-planning | Protected history/fixed-event invariants pass; Tauri calculates remaining time locally |
| 5. Goals and reminders | Goal roadmap, milestones, FastAPI Reminder records, Tauri local due-time evaluation, tray red-dot, widget bubble | Local-time, hidden-widget, and duplicate-action tests pass |
| 6. Garden, plant, and ambience | HeartEvent, one GardenState, PlantType switch, compositional time/weather widget layers | Reward idempotency, plant-switch, and weather-fallback tests pass |
| 7. Release hardening | Security/privacy review, Windows/Linux smoke, regression, demo, and Docker deployment | Critical end-to-end flows pass |

## Control rules

- Implement scheduling correctness before adding experience polish.
- Keep one main feature in progress; split work that cannot be safely tested in one increment.
- A scope increase requires an explicit deferral of comparable work; explicit exclusions cannot enter an MVP sprint.
- Mr. Bloom can interpret and explain in the full application but cannot decide timestamps, feasibility, conflicts, reminders, Heart Progress, WeatherContext gameplay, or database transactions.
- Time and weather change presentation only.
- A feature is done only when its requirements, tests, privacy/security impact, and documentation agree; planned work is never reported as complete without evidence.

## Principal risks

| Risk | Response |
|---|---|
| Scheduling complexity | Keep domain rules pure, deterministic, and invariant-tested; reduce heuristics before weakening correctness. |
| AI malformed output or prompt injection | Require strict schemas, validate server-side, minimize prompts, and preserve form fallback. |
| Reminder timezone or duplicate actions | Store local timezone and action keys; FastAPI persists; Tauri evaluates due times locally; no per-second polling. |
| Re-planning rewrites history | Protect completed FocusRuns, fixed events, locked fixed-Task blocks, and active session in one recovery transaction. |
| Garden becomes punitive or game-like | One GardenState, Heart Progress as visual progress, PlantType visual-only, no death/inventory/shop in MVP. |
| Weather leaks into planning | Treat WeatherContext as cached presentation data; fallback to time-only visuals; never feed it to the scheduler. |
| Solo scope pressure | Preserve the MVP blocks and defer calendar, OS notifications, email/push, economy, social, and multi-agent features. |
