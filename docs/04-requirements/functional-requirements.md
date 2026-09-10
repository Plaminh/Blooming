# Functional Requirements

Requirements use **must** for required behavior, **should** for intended non-critical behavior, and **may** for optional behavior.

Canonical names: DailyPlan, PlanBlock, FocusRun, PlanRevision, Goal, Milestone, Reminder, ReminderAction, Heart Progress, HeartEvent, GardenState, PlantType, WidgetState, WidgetContext, WeatherContext, WeatherSnapshot, PlanningSession, PlanningMessage.

## User, settings, and assistant

Mr. Bloom is a small robot cat and Blooming's visual identity: warm, concise, occasionally enthusiastic, and honest about unrealistic plans. Planning chat exists only in the full application. This identity does not create a companion, shop, inventory, or multi-agent system.

| ID | Requirement |
|---|---|
| FR-USER-001 | The system must register, authenticate, and log out users with JWT-based authentication. |
| FR-USER-002 | The system must enforce ownership for every user-owned read or state change. |
| FR-SET-001 | The system must store a basic profile, IANA timezone, default focus/break duration, quiet hours, reminder preferences, launch-on-startup, widget visibility, always-on-top, Mr. Bloom display name, active PlantType, weather-aware visuals on/off, and a city or optional coarse location. |
| FR-AI-001 | Mr. Bloom must provide extraction, limited editing, clarification, overload/conflict explanation, recovery, and milestone messages using the canonical intents, only inside the full application. |
| FR-AI-002 | The system must use validated structured output for an AI response that affects state; a normal structured form must remain available when AI interpretation fails. |
| FR-AI-003 | Mr. Bloom must ask clarification only when missing information materially affects feasibility or ordering, normally no more than one or two questions. |
| FR-AI-004 | The widget must not provide free-form chat and must not call the language model continuously. |

Where an intent is persisted, exchanged, or tested, it must be one of `CREATE_DAILY_PLAN`, `EDIT_DAILY_PLAN`, `CREATE_GOAL`, `EDIT_ROADMAP`, `REPLAN`, `EXPLAIN_PLAN`, or `GENERAL_RESPONSE`.

## Daily planning, focus, and recovery

| ID | Requirement |
|---|---|
| FR-PLAN-001 | The system must accept structured and natural-language Task input, available windows, non-Task fixed events, estimates, priority, deadline where applicable, core/optional, fixed/flexible, fixed start time for fixed Tasks, and direct dependencies. |
| FR-PLAN-002 | The system must present an editable Task Draft before scheduling natural-language input. |
| FR-PLAN-003 | The deterministic scheduler must return one ordered `PlanBlock[]` timeline containing generated `FOCUS` and `BREAK` blocks plus unchanged `FIXED_EVENT` blocks. Generated/locked blocks must fit available windows and Task deadlines and must not overlap each other or a fixed event; unchanged fixed events may overlap one another or extend partly outside a window. Each fixed Task must produce a validated locked sequence whose first `FOCUS` block begins at its fixed start time. |
| FR-PLAN-004 | The system must calculate and display `COMFORTABLE`, `TIGHT`, or `OVERLOADED`; overload must offer feasible alternatives and must not silently compress work. |
| FR-PLAN-005 | The system must persist reviewed DailyPlans and validate every manual or conversational time edit before it is accepted. |
| FR-FOCUS-001 | Today must show the timeline, current/next session, upcoming break, daily progress, garden visual, and Pomodoro setup. Focus begins only after the user selects a task and presses Start. |
| FR-FOCUS-002 | Focus Mode must support countdown, pause/resume, remaining time, progress, presets `25 / 5` and `50 / 10`, and a custom duration. FastAPI must store `started_at` and `expected_end_at`; Tauri must calculate the countdown locally. |
| FR-FOCUS-003 | The system must record `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, or `SKIP` and store actual execution independently of planned time. |
| FR-REPLAN-001 | The system must re-plan only unfinished flexible future work, retain completed FocusRuns, fixed events, locked fixed-Task PlanBlocks, and the active session as required by BR-008, and briefly explain changes. |

## Goals, reminders, widget, garden, and weather

| ID | Requirement |
|---|---|
| FR-GOAL-001 | The system must create editable Goals with high-level Roadmaps, Milestones, expected outcomes, deadlines, order, status, and overall progress. Roadmaps must not automatically create detailed tasks. |
| FR-GOAL-002 | The system must warn about downstream effects when a milestone moves and offer to shift downstream dates equally. |
| FR-REM-001 | FastAPI must store Reminder definitions, due times, and states. Tauri must synchronize upcoming reminders at startup, after sleep, and after reminder changes, and must evaluate due times locally. |
| FR-REM-002 | The system must support Milestone ReminderAction values `CREATE_PLAN`, `MARK_COMPLETED`, `MOVE_MILESTONE`, and `REMIND_LATER`, and require confirmation before adding tasks to a Daily Plan. Focus/task widget actions may include `START_FOCUS`, `REMIND_LATER`, and `OPEN_BLOOMING`; those two start/open actions are not Milestone ReminderAction values. |
| FR-REM-003 | When a reminder is due, the widget must show Mr. Bloom's bubble and the tray must show a red-dot while any due reminder is unread. Hiding the widget must not drop unread due reminders. The MVP must not use OS toast/banner notifications or per-second backend polling. |
| FR-WIDGET-001 | The widget must implement WidgetState `DEFAULT`, `REMINDER`, `FOCUSING`, `SESSION_RESULT`, and `HIDDEN` separately from visual WidgetContext. |
| FR-WIDGET-002 | WidgetContext must contain local time-of-day (`MORNING`, `AFTERNOON`, `EVENING`, `NIGHT`) and, when weather-aware visuals are enabled, optional WeatherContext (`CLEAR`, `CLOUDY`, `RAINY`, `STORMY`, `FOGGY`, `SNOWY`, or `UNKNOWN`). WidgetContext must remain independent from WidgetState. The rendered widget must compose WidgetState + WidgetContext + PlantType/GardenState from reusable layers, not a unique screen per combination. |
| FR-WIDGET-003 | Time and weather must not affect scheduler decisions, task priority, reminder timing, Heart Progress, or planning logic. Disabled weather-aware visuals must omit the weather overlay and use time-only WidgetContext without requiring WeatherContext `UNKNOWN`. Unavailable or invalid weather may normalize WeatherContext to `UNKNOWN` while the UI still uses time-only presentation. `UNKNOWN` must never affect scheduling, reminders, Heart Progress, or planning. |
| FR-WIDGET-004 | Session outcomes must be chosen in WidgetState `SESSION_RESULT`, not before it. The widget follows `DEFAULT → FOCUSING → SESSION_RESULT`, then `DONE → DEFAULT`, `FINISHED_EARLY → DEFAULT`, or `NEED_MORE_TIME` / `SKIP` → re-plan → `DEFAULT`. `FINISHED_EARLY` means the user ended the session early because the intended work was completed; it must not automatically trigger re-planning. |
| FR-PLANT-001 | The system must maintain one GardenState and persist the active PlantType. Frontend artwork must be selected from PlantType plus GardenState stage. |
| FR-PLANT-002 | HeartEvent recording must be idempotent. Opening the application must not grant Heart Progress. |
| FR-PLANT-003 | Switching PlantType must not reset Heart Progress, GardenState stage, or execution history. |
| FR-WX-001 | FastAPI must fetch and cache at most one current WeatherSnapshot per user for a selected city or optional coarse location. It must not require continuous GPS or store weather or location history in the MVP. |
