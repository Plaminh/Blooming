# MVP Scope

The frozen product concept is `Blooming-Concept-Updated.md`. Scheduling correctness and the daily loop come first, but all six blocks below are required for the MVP.

## MVP objective

Blooming must turn daily intentions into a realistic, editable Daily Plan; support Pomodoro execution and recovery through the Mr. Bloom widget; connect milestones to a confirmed Daily Plan through reminders; and express lasting Heart Progress in one GardenState with a selectable PlantType.

## Included capabilities

| Block | Minimum behavior | Acceptance evidence |
|---|---|---|
| User and Settings | Register, login, logout, JWT; timezone; focus/break defaults; quiet hours; launch-on-startup; widget visibility and always-on-top; Mr. Bloom display name; active PlantType; weather-aware visuals on/off; city or optional coarse location | Authentication, timezone, widget, plant, and weather-preference tests pass |
| Desktop Widget | Lightweight always-on-top surface with WidgetState `DEFAULT`, `REMINDER`, `FOCUSING`, `SESSION_RESULT`, `HIDDEN`; composed time/weather visuals; no free-form chat | Widget state, tray, and fallback tests pass |
| Daily Planning | Natural-language Task Draft, Reality Check, deterministic PlanBlock timeline, edits validated by the scheduler | Scheduler, API, and Today invariants pass |
| Pomodoro, Focus, and Re-planning | Task selection in the app, presets `25/5` and `50/10` plus custom, FocusRun outcomes, protected-history re-planning | Focus/re-plan tests preserve history and fixed events |
| Goals and Reminders | Editable Goal, Roadmap, Milestone; FastAPI-stored Reminder/ReminderAction; Tauri local due-time evaluation; tray red-dot; widget bubble | Reminder sync, hidden-widget, and confirmation tests pass |
| Heart Progress and Garden | HeartEvent ledger; one GardenState; PlantType switch without reset; stages `DORMANT` → `SPROUTING` → `GROWING` → `BLOOMING` → `FLOURISHING` | Reward idempotency and plant-switch tests pass |

## Delivery order

1. Establish authentication/settings, timezone, and deterministic scheduling foundations.
2. Deliver the Daily Plan, overload, timeline, and persistence loop.
3. Add Mr. Bloom's validated Task Draft and explanation flows in the full application.
4. Add focus execution, widget countdown, and adaptive re-planning.
5. Add goals, milestones, and the desktop reminder architecture.
6. Add Heart Progress, PlantType, GardenState, time/weather widget layers, then harden and ship the complete MVP.

## Explicitly outside the MVP

- Google Calendar integration.
- OS toast or banner notifications, email, or push reminders.
- Team, social, or shared planning.
- Free-form widget chat, continuous LLM widget calls, RAG, LangGraph, or multi-agent workflows.
- Multiple simultaneous gardens or separate plant progression tracks, inventory, shop, currency, gacha, plant death, or a roaming desktop pet.
- Weather-driven scheduling, rewards, penalties, or gameplay effects.
- Continuous or historical GPS tracking; detailed forecasts; seasonal simulation.
- Mobile, web-only, and macOS releases.
- Full offline planning and AI.
- A later Vitality system is post-MVP and must preserve earned progress.

## Quality floor

- No generated or locked Task/Break PlanBlock overlaps another generated/locked block or fixed event; these blocks fit an available window and every Task block respects its deadline.
- `COMFORTABLE`, `TIGHT`, and `OVERLOADED` are explicit; overloaded work is never silently compressed.
- Manual or conversational time edits are revalidated by deterministic code.
- Planned time and actual execution time remain separate; re-planning preserves completed history, fixed events, and the active session unless changed by the user.
- FastAPI never receives one request per second. Tauri evaluates reminder due times locally. Hiding the widget does not drop unread due reminders.
- Time and weather change presentation only. Switching PlantType does not reset Heart Progress, GardenState, or history.
- AI output is structured, validated, and optional: a normal form remains usable when AI fails.

## Success measures

The eleven product success criteria in `Blooming-Concept-Updated.md` §10 are the MVP bar. Additional engineering floors:

| Type | Measure | Target |
|---|---|---:|
| Product | A five-task plan can be created in a usability walkthrough | At most 2 minutes |
| Correctness | Accepted plans with a scheduling invariant violation | 0% |
| Reliability | Duplicate reminder action persistence for one occurrence | 0 |
| Recovery | Re-plans that alter protected completed history or fixed events | 0 |
| AI safety | State-changing AI output validated or rejected before execution | 100% |
