# Product Backlog

## Priority rule

All six product blocks are MVP scope. Work is ordered so that deterministic planning correctness and the daily planning loop are available before dependent conversational, goal, reminder, and plant behavior. This backlog records intended scope, not implementation completion, estimates, owners, or sprint history.

## MVP epics

| Epic | Outcome | Priority | Depends on |
|---|---|---|---|
| EPIC-01 User and Settings | A user can authenticate with JWT and set timezone, focus/break defaults, reminder preferences, and Rest Mode | Must | Foundation |
| EPIC-02 Daily Planning | The user can create, review, edit, save, and understand a feasible daily plan | Must | EPIC-01 |
| EPIC-03 Mr. Bloom Assistant | Natural language creates reviewable Task/Roadmap Drafts and explains changes with validated structured output | Must | EPIC-02 |
| EPIC-04 Focus and Recovery | The user can execute and recover a plan without history loss | Must | EPIC-02 |
| EPIC-05 Goals and Reminders | Goals, editable milestone roadmaps, and local-time reminder actions connect to tomorrow's plan | Must | EPIC-01, EPIC-03 |
| EPIC-06 Plant System | One active plant reflects meaningful activity, Water Reserve, abandonment, and Rest Mode | Must | EPIC-01, EPIC-04 |
| EPIC-07 Delivery and Quality | The integrated MVP is secure, tested, deployed, and documented | Must | EPIC-01–06 |

## Ordered backlog

| ID | Epic | Intended outcome | Key acceptance condition |
|---|---|---|---|
| PB-001 | EPIC-01 | Register/login/logout and JWT ownership enforcement | One user cannot read or mutate another user's data |
| PB-002 | EPIC-01 | Profile, timezone, defaults, email setting, and Rest Mode configuration | Settings affect the correct user-local behavior |
| PB-003 | EPIC-02 | Structured Task Draft and deterministic preview | One ordered PlanBlock timeline preserves fixed events, respects windows/deadlines/fixed Tasks, and follows the exact Break policy without overlap |
| PB-004 | EPIC-02 | Reality Check and overload resolution | `OVERLOADED` is explained with feasible alternatives, never hidden |
| PB-005 | EPIC-02 | Persisted Daily Plan and validated manual edits | Every time-affecting edit reuses deterministic validation |
| PB-006 | EPIC-03 | Mr. Bloom natural-language capture and limited plan editing | AI state changes use validated structured output; form fallback works |
| PB-007 | EPIC-04 | FocusRun timer, pause/resume, outcomes, and actual-time storage | Planned time and actual execution are separate |
| PB-008 | EPIC-04 | Re-plan remaining work | Completed history, fixed events, and active session are protected |
| PB-009 | EPIC-05 | Goal, Roadmap, Milestone, progress, and downstream-date warning | Roadmap does not create detailed future daily tasks automatically |
| PB-010 | EPIC-05 | In-app/basic email reminder and four reminder actions | 20:00 local-time day-before reminder is idempotent; plan tasks need confirmation |
| PB-011 | EPIC-06 | PlantState, meaningful-activity ledger, and Water Reserve | Opening the app does not create water or growth |
| PB-012 | EPIC-06 | Health/death/rest rules and frontend asset selection | Missed work does not directly damage the plant; death preserves data and yields a seed |
| PB-013 | EPIC-07 | Security, privacy, observability, Docker deployment, and regression evidence | Release gates and critical acceptance flows pass |

## Explicitly excluded ideas

Google Calendar integration/replacement, analytics, weekly AI reports, learned estimates, habits, voice, teams, social features, leaderboards, multiple plants, inventory, shop/currency/gacha, robot customization, pet-care simulation, world/story/quests, complex animation/web push, multiple agents, LangChain, and LangGraph are not backlog work for this MVP.
