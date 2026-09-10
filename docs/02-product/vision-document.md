# Vision Document: Blooming

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Current |
| Last updated | 10 September 2026 |

## Revision history

| Date | Version | Change |
|---|---|---|
| 8 September 2026 | 1.0 | Established the personal-project vision and MVP boundary. |
| 10 September 2026 | 1.1 | Aligned with `Blooming-Concept-Updated.md`: desktop-only, widget, PlantType, Heart Progress, and presentation-only weather. |

## 1. Introduction and references

This document defines Blooming's product direction, users, system boundary, core features, and high-level quality goals. The frozen concept in `Blooming-Concept-Updated.md` is the source of truth. Release commitments live in `mvp-scope.md`.

References:

- `Blooming-Concept-Updated.md`
- `../01-discovery/product-proposal.md`
- `../01-discovery/app-survey.md`
- `mvp-scope.md`
- `../04-requirements/domain-rules.md`

## 2. Positioning

### Problem statement

| Element | Statement |
|---|---|
| The problem of | Creating task lists and schedules that ignore real capacity and become obsolete after disruption |
| Affects | Students, self-directed learners, and individual knowledge workers managing changing personal days |
| The impact is | Stress, repeated manual re-planning, abandoned plans, and reduced trust in planning tools |
| A successful solution would | Produce an understandable feasible Daily Plan, expose overload, support execution through a lightweight desktop widget, and adapt without rewriting completed history |

### Product position statement

For individuals who need to organize busy days and long-term goals, Blooming is a desktop daily planner that turns intentions into realistic, editable Daily Plans. Unlike a task list, calendar replacement, timer, chatbot wrapper, or pet game, it separates language interpretation from deterministic scheduling, shows when work cannot fit, follows the plan through Mr. Bloom's widget, and supports recovery.

## 3. Stakeholders and users

| Stakeholder/user | Description | Goals and needs |
|---|---|---|
| Primary user | Student, self-directed learner, or individual knowledge worker | Plan quickly, avoid overload, retain control, focus, and recover from disruption |
| Developer and maintainer | Solo project owner | Keep scope manageable, architecture testable, and documentation consistent with the frozen concept |
| LLM provider | External semantic-processing service | Receive valid requests within provider limits; must not become the scheduling authority |
| Weather provider | External presentation-data service | Supply coarse current conditions; must not affect planning |
| Hosting provider | Runs the deployed API/database services | Receive secure configuration and health-checkable artifacts |

### User environment

- The user plans and focuses on Windows or Linux desktop. There is no MVP web-only, mobile, or macOS product.
- Two surfaces: the full application (Today, Goals, Settings) and the optional Mr. Bloom widget.
- Planning commonly occurs before a study/work block; the widget follows the plan while the main window is closed.
- The user may have incomplete estimates and fixed commitments.
- The experience must remain usable when the AI feature fails, times out, or is disabled.
- Time and weather may change ambience; they must never change planning, reminders, or Heart Progress.

## 4. Product overview

### Product perspective

Blooming is a standalone Windows/Linux desktop application. Tauri hosts two windows (main application and widget). FastAPI owns validation, scheduling, persistence, reminder records, Heart Progress, PlantType, GardenState, and weather-context caching. An external LLM may interpret natural language inside the full application only; its output is untrusted input. Weather is presentation-only. Google Calendar, OS notifications, email/push reminders, and team systems remain outside the MVP.

### Product principles

1. Planning first.
2. AI interprets; code decides.
3. Recover over perfect.
4. Failure is not abandonment.
5. Present, not intrusive.
6. Context changes presentation, not planning.

### Core loop

```text
Open Blooming
    -> Describe today's work
    -> Confirm the Task Draft
    -> Generate a realistic Daily Plan
    -> Select a task and start Pomodoro
    -> Follow the plan through the widget
    -> Complete or re-plan
    -> The garden grows
```

Long-term direction:

```text
Goal -> Roadmap -> Milestone -> Reminder -> Confirm Daily Plan
```

### Assumptions and dependencies

| Type | Statement | Validation or review trigger |
|---|---|---|
| Assumption | Users can provide or accept rough duration estimates. | Observe repeated correction or abandonment during usability testing. |
| Assumption | A visible overload explanation is more useful than silently dropping work. | Test overload scenarios with users. |
| Dependency | Conversational input requires an external LLM API. | Select and privacy-review a provider before implementing conversational integration. |
| Dependency | Weather-aware visuals require a remote weather API and a city or optional coarse location. | Disable visuals and fall back to time-only presentation when data is unavailable. |
| Dependency | Persistence and deployment require PostgreSQL and a hosting environment. | Confirm before persistence and release work respectively. |
| Constraint | The MVP is implemented by one developer in small evidence-producing increments. | Split an increment when its acceptance evidence cannot be completed coherently. |
| Constraint | AI cost must remain bounded and the planner must work without AI. | Review after AI evaluation. |

## 5. Product features

### Reality-aware Daily Planning

The user describes available time and intended work, or enters a structured Task Draft. Blooming validates inputs, locks fixed Tasks, places flexible work, calculates usable capacity, and classifies the request as `COMFORTABLE`, `TIGHT`, or `OVERLOADED`. It returns one ordered PlanBlock timeline. The frontend does not reconstruct events separately.

### Plan review and editing

The user sees the generated timeline, warnings, and unscheduled tasks before committing. Every edit is validated by the scheduler. The system does not silently shorten work or create overlaps.

### Conversational task capture

Planning chat exists only in the full application. Mr. Bloom extracts an editable Task Draft and asks at most one or two material questions. A form remains available as fallback. The widget has no free-form chat and does not call the LLM continuously.

### Focus execution

Focus begins after the user opens Blooming, selects a task, configures Pomodoro, and presses Start. FastAPI stores timestamps; Tauri calculates the countdown; the widget displays it. Outcomes are `DONE`, `NEED_MORE_TIME`, `SKIP`, and `FINISHED_EARLY`. Planned and actual duration stay separate.

### Adaptive re-planning

When work takes longer, is skipped, or availability changes, Blooming freezes completed history, fixed events, and the active session, then schedules unfinished flexible work into the remaining time.

### Goals and desktop reminders

A Goal has a high-level Roadmap of Milestones. Roadmaps do not auto-create detailed tasks. FastAPI stores Reminder and ReminderAction records. Tauri synchronizes upcoming reminders and evaluates due times locally. The tray red-dot and widget bubble present due reminders. Milestone actions are `CREATE_PLAN`, `MARK_COMPLETED`, `MOVE_MILESTONE`, and `REMIND_LATER`.

### Heart Progress, PlantType, and GardenState

Heart Progress increases for valid completed focus, task, core objective, milestone, or recovery work. Opening the app grants nothing. One GardenState uses `DORMANT` → `SPROUTING` → `GROWING` → `BLOOMING` → `FLOURISHING`. PlantType is a visual variant of that shared progression.

### Widget context

WidgetState is functional: `DEFAULT`, `REMINDER`, `FOCUSING`, `SESSION_RESULT`, `HIDDEN`. WidgetContext contains local time (`MORNING`, `AFTERNOON`, `EVENING`, `NIGHT`) and optional WeatherContext (`CLEAR`, `CLOUDY`, `RAINY`, `STORMY`, `FOGGY`, `SNOWY`, `UNKNOWN`). It remains independent from WidgetState. The rendered widget composes WidgetState + WidgetContext + PlantType/GardenState.

## 6. High-level quality requirements

| Quality | Target |
|---|---|
| Performance | Scheduler preview completes within 500 ms at the backend for up to 50 tasks, excluding network latency. |
| Reliability | No accepted plan contains an overlap or a session outside its available window. |
| Persistence | Saved plans and FocusRun timestamps survive restart; Tauri recovers countdown from stored instants. |
| Security/privacy | Secrets and personal planning content are excluded from source control and application logs; weather uses city/coarse location, not GPS history. |
| Accessibility | Critical planning and focus flows are keyboard-operable and do not rely on color alone. |
| AI quality/cost | Invalid AI output never reaches the scheduler unvalidated; requests are capped and have a manual fallback. |

## 7. Future direction

Possible later releases include calendar integration, a Vitality system that preserves earned progress, email/push while Blooming is fully closed, and native mobile or macOS. These directions do not expand the first MVP.
