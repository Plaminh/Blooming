# Product Backlog

## Priority rule

The MVP blocks are committed scope. Work is ordered so that deterministic planning correctness and the daily planning loop are available before dependent conversational, goal, reminder, garden, and weather-presentation behavior. This backlog records intended scope, not implementation completion, estimates, owners, or sprint history. The frozen concept is `../02-product/Blooming-Concept-Updated.md`.

## MVP epics

| Epic | Outcome | Priority | Depends on |
|---|---|---|---|
| EPIC-01 User and Settings | A user can authenticate with JWT and set timezone, focus/break defaults, quiet hours, widget behavior, PlantType, and weather-context preferences | Must | Foundation |
| EPIC-02 Daily Planning | The user can create, review, edit, save, and understand a feasible Daily Plan | Must | EPIC-01 |
| EPIC-03 Mr. Bloom Assistant | Natural language in the full application creates reviewable Task/Roadmap Drafts and explains changes with validated structured output | Must | EPIC-02 |
| EPIC-04 Focus and Recovery | The user can execute and recover a plan without history loss, including widget countdown | Must | EPIC-02 |
| EPIC-05 Goals and Reminders | Goals, editable milestone roadmaps, and desktop reminder actions connect to a confirmed Daily Plan | Must | EPIC-01, EPIC-03 |
| EPIC-06 Garden and Widget Context | One GardenState reflects Heart Progress; PlantType is visual; widget composes time/weather layers | Must | EPIC-01, EPIC-04 |
| EPIC-07 Delivery and Quality | The integrated MVP is secure, tested on Windows/Linux, deployed, and documented | Must | EPIC-01–06 |

## Ordered backlog

| ID | Epic | Intended outcome | Key acceptance condition |
|---|---|---|---|
| PB-001 | EPIC-01 | Register/login/logout and JWT ownership enforcement | One user cannot read or mutate another user's data |
| PB-002 | EPIC-01 | Profile, timezone, defaults, quiet hours, widget, PlantType, and weather-location settings | Settings affect the correct user-local behavior without GPS history |
| PB-003 | EPIC-02 | Structured Task Draft and deterministic preview | One ordered PlanBlock timeline preserves fixed events, respects windows/deadlines/fixed Tasks, and follows the exact Break policy without overlap |
| PB-004 | EPIC-02 | Reality Check and overload resolution | `OVERLOADED` is explained with feasible alternatives, never hidden |
| PB-005 | EPIC-02 | Persisted Daily Plan and validated manual edits | Every time-affecting edit reuses deterministic validation |
| PB-006 | EPIC-03 | Mr. Bloom natural-language capture and limited plan editing | AI state changes use validated structured output; form fallback works; widget has no chat |
| PB-007 | EPIC-04 | FocusRun timer, pause/resume, outcomes, and actual-time storage | Planned time and actual execution are separate; Tauri calculates countdown from FastAPI timestamps |
| PB-008 | EPIC-04 | Re-plan remaining work | Completed history, fixed events, and active session are protected |
| PB-009 | EPIC-05 | Goal, Roadmap, Milestone, progress, and downstream-date warning | Roadmap does not create detailed future daily tasks automatically |
| PB-010 | EPIC-05 | FastAPI Reminder records, Tauri local due-time evaluation, tray red-dot, widget bubble | 20:00 local-time day-before reminder is idempotent; hiding the widget does not drop unread due reminders; no OS toast |
| PB-011 | EPIC-06 | HeartEvent ledger and one GardenState | Opening the app does not grant Heart Progress; stages use `DORMANT` → `SPROUTING` → `GROWING` → `BLOOMING` → `FLOURISHING` |
| PB-012 | EPIC-06 | PlantType switch and compositional widget visuals | Switching plants does not reset progress; time/weather are presentation layers; weather fallback is time-only |
| PB-013 | EPIC-07 | Security, privacy, observability, Docker deployment, and Windows/Linux regression evidence | Release gates and critical acceptance flows pass |

## Explicitly excluded ideas

Google Calendar integration/replacement, analytics, weekly AI reports, learned estimates, habits, voice, teams, social features, leaderboards, multiple gardens, inventory, shop/currency/gacha, plant death, robot customization, pet-care simulation, world/story/quests, OS toast/banner notifications, email/push reminders, continuous GPS, weather-driven planning, free-form widget chat, multiple agents, LangChain, and LangGraph are not backlog work for this MVP. A later Vitality system is post-MVP and must preserve earned progress.
