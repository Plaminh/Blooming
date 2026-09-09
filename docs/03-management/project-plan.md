# Project Plan

## Delivery approach

Blooming is a solo modular-monolith project delivered in small vertical slices. The project retains six required MVP blocks; delivery order is a risk-control decision, not a scope exclusion. `product-backlog.md` is the source of planned scope and priority. No completion status is implied by this plan.

## Delivery sequence

| Phase | Outcome | Dependencies and exit evidence |
|---|---|---|
| 1. Foundation | Docker environment, JWT/auth, user settings, timezone model, deterministic scheduler | Unified PlanBlock, deadline, fixed/flexible Task, Break, and ownership invariants are automated |
| 2. Daily planning | Structured planning, Reality Check, timeline, persistence, overload and edits | Valid Plans are non-overlapping, honest, and editable |
| 3. Conversational planning | Mr. Bloom Task Draft, clarification, explanations, and form fallback | AI output is validated before state changes |
| 4. Focus and recovery | Today, FocusRun, outcomes, and re-planning | Protected history/fixed-event invariants pass |
| 5. Goals and reminders | Goal roadmap, milestones, reminder delivery/actions | Local-time and duplicate-delivery tests pass |
| 6. Plant and rest | One plant, Water Reserve, activity, death, asset mapping, Rest Mode | Decay and non-punitive behavior tests pass |
| 7. Release hardening | Security/privacy review, regression, demo, and Docker deployment | Critical end-to-end flows and smoke test pass |

## Control rules

- Implement scheduling correctness before adding experience polish.
- Keep one main feature in progress; split work that cannot be safely tested in one increment.
- A scope increase requires an explicit deferral of comparable work; explicit exclusions cannot enter an MVP sprint.
- Mr. Bloom can interpret and explain but cannot decide timestamps, feasibility, conflicts, reminders, plant state, or database transactions.
- A feature is done only when its requirements, tests, privacy/security impact, and documentation agree; planned work is never reported as complete without evidence.

## Principal risks

| Risk | Response |
|---|---|
| Scheduling complexity | Keep domain rules pure, deterministic, and invariant-tested; reduce heuristics before weakening correctness. |
| AI malformed output or prompt injection | Require strict schemas, validate server-side, minimize prompts, and preserve form fallback. |
| Reminder timezone/duplicate delivery | Store local timezone and delivery keys; use transactional, idempotent scheduled jobs. |
| Re-planning rewrites history | Protect completed FocusRuns, fixed events, locked fixed-Task blocks, and active session in one recovery transaction. |
| Plant becomes punitive or game-like | Limit it to one plant, meaningful activity, Water Reserve, Rest Mode, and history-preserving death. |
| Solo scope pressure | Preserve six minimal blocks and defer all integrations, economy, social, and multi-agent features. |
