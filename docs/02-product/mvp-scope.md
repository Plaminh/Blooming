# MVP Scope

## MVP objective

Blooming must turn daily intentions and long-term goals into realistic, editable plans; support focused execution and recovery; connect milestones to tomorrow's plan through reminders; and express sustained progress through one non-punitive living plant. Scheduling correctness and the daily loop are implemented first, but all six blocks below are required for the MVP.

## Included capabilities

| Block | Minimum behavior | Acceptance evidence |
|---|---|---|
| User and Settings | Register, login, logout, JWT authentication, basic profile, timezone, focus/break defaults, email-reminder setting, and Rest Mode configuration | Authentication, authorization, timezone, and settings tests pass |
| Mr. Bloom Assistant | Calm, concise conversational onboarding, extraction, limited plan/roadmap editing, clarification, explanation, and recovery using canonical intents | Structured-output and fallback tests pass |
| Daily Planning | Form and natural-language Task Draft, deadlines, core/optional and fixed/flexible Tasks, Reality Check, deterministic unified PlanBlock timeline, precise breaks/buffers, dependencies, unchanged fixed events, edits, persistence, and overload alternatives | Scheduler, API, and UI invariants pass |
| Focus and Adaptive Re-planning | Today timeline, current/next session, timer, pause/resume, `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, `SKIP`, and protected-history re-planning | Focus/re-plan tests preserve history and fixed events |
| Long-term Goals and Reminders | Editable goals, high-level roadmaps, milestones, progress, local-time reminder, in-app and basic email delivery | Reminder, action, downstream-date, and idempotency tests pass |
| Plant System | One active backend-owned plant, growth/health state, Water Reserve, meaningful activity, history-preserving death, and Rest Mode | Plant-decay, activity, Rest Mode, and asset-state tests pass |

## Delivery order

1. Establish authentication/settings and deterministic scheduling foundations.
2. Deliver the daily plan, overload, timeline, and persistence loop.
3. Add Mr. Bloom's validated Task Draft and explanation flows.
4. Add focus execution and adaptive re-planning.
5. Add goals, milestones, and timezone-correct reminder actions.
6. Add the minimal plant, Water Reserve, Rest Mode, then harden and deploy the complete MVP.

## Explicitly outside the MVP

- Google Calendar integration or calendar replacement.
- Advanced analytics, weekly AI reports, automatic learning from estimate history, habit tracking, or voice assistant.
- Team accounts, collaborative planning, social features, and leaderboards.
- Multiple active plants, plant inventory, shop, currency, gacha, robot customization, pet-care simulation, world map, territory restoration, story campaign, or quest system.
- Complex animation, complex web push, multiple AI agents, LangChain, and LangGraph.

## Quality floor

- No generated or locked Task/Break PlanBlock overlaps another generated/locked block or fixed event; these blocks fit an available window and every Task block respects its deadline. Each fixed event appears unchanged as a `FIXED_EVENT`, even when input events overlap one another or extend partly outside the window used for capacity.
- `COMFORTABLE`, `TIGHT`, and `OVERLOADED` are explicit; overloaded work is never silently compressed.
- Manual or conversational time edits are revalidated by deterministic code.
- Planned time and actual execution time remain separate; re-planning preserves completed history, fixed events, locked fixed-Task blocks, and the active session unless changed by the user.
- Reminder timing uses the user timezone; one reminder action cannot send duplicate notifications.
- Missed work and delayed milestones do not directly reduce plant health; Rest Mode pauses Water Reserve decay and growth.
- AI output is structured, validated, and optional: a normal form remains usable when AI fails.

## Success measures

| Type | Measure | Target |
|---|---|---:|
| Product | A five-task plan can be created in a usability walkthrough | At most 2 minutes |
| Correctness | Accepted plans with a scheduling invariant violation | 0% |
| Reliability | Duplicate milestone reminders | 0 |
| Recovery | Re-plans that alter protected completed history or fixed events | 0 |
| AI safety | State-changing AI output validated or rejected before execution | 100% |
