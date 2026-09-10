# Blooming — Product Concept

> Status: Frozen MVP concept

## 1. Product Summary

Blooming is a lightweight desktop daily planner that turns natural-language intentions into realistic schedules, supports focused execution, and repairs the remaining plan when reality changes.

Blooming is desktop-only and supports Windows and Linux. It has two surfaces:

- **Full application:** the user creates or edits a Daily Plan, selects tasks, starts Pomodoro, manages milestones, and chooses the active plant type.
- **Mr. Bloom widget:** a small optional always-on-top window that shows Mr. Bloom, the current time, necessary reminder messages, the active Pomodoro countdown, and a compact garden whose ambience can adapt to local time and weather.

Mr. Bloom is the visual identity of Blooming, not a general-purpose AI companion. Planning is the product core; the character and garden make the plan feel present without keeping the full application open.

> **One-line description:** Blooming builds realistic daily schedules, follows them through a lightweight context-aware clock-and-focus widget, and helps the user recover when plans change.

### Problem and target users

Traditional task and calendar apps still require users to structure vague intentions, estimate duration, resolve conflicts, fit work into limited time, and repair the schedule after delays. This overhead often produces unrealistic plans or causes the user to abandon the day after one disruption.

Blooming initially serves students, self-directed learners, and individual knowledge workers who overload their days, underestimate task duration, use focus cycles, and want long-term direction without complex project-management software.

## 2. Product Identity and Principles

In the distant future, natural plant life has nearly disappeared. Mr. Bloom is a small robot cat connected to and protecting a living pixel garden.

- Mr. Bloom communicates the plan and reacts to focus sessions.
- The garden reflects accumulated meaningful progress.
- Completing work causes the selected plant and garden to visibly develop over time.
- The user may switch between a small preset set of plant types without resetting earned progress.
- The widget's ambient presentation may react to local time and current weather while keeping planning information primary.
- Mr. Bloom is warm, concise, occasionally enthusiastic, and honest about unrealistic plans.
- Desktop messages are useful and event-driven; free-form planning chat exists only inside the full application.

The user may rename Mr. Bloom. Preset skins, accessories, and selectable conversation styles are post-MVP features.

### Principles

1. **Planning first:** Blooming exists primarily to create, execute, and repair a realistic Daily Plan.
2. **AI interprets; code decides:** AI understands language and explains decisions; deterministic code owns time, conflicts, reminders, timers, and rewards.
3. **Recover over perfect:** completed history is preserved while only unfinished work is re-planned.
4. **Failure is not abandonment:** missing a task does not erase previous progress or punish the user.
5. **Present, not intrusive:** widget messages are infrequent, dismissible, and controlled by quiet hours.
6. **Context changes presentation, not planning:** time and weather may change the widget's ambience, but never task priority, schedule feasibility, reminders, or Heart Progress.

## 3. Core Product Loops

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

Long-term goals connect to daily action through:

```text
Goal -> Roadmap -> Milestone -> Reminder -> Confirm Daily Plan
```

## 4. MVP Feature Blocks

Blooming MVP contains six implementation blocks.

### Block 1 — User and Settings

- Register, login, logout, and JWT authentication.
- Basic profile and timezone.
- Default focus and break durations.
- Quiet hours and reminder preferences.
- Launch-on-startup, widget visibility, and always-on-top preferences.
- Mr. Bloom's display name.
- Active plant type.
- Weather-aware widget visuals on or off.
- Weather location preference using a manually selected city or optional coarse device location.

Social login, team accounts, and complex account recovery are outside the MVP.

### Block 2 — Desktop Widget

The widget is Blooming's lightweight desktop surface.

Functional `WidgetState` values:

```text
DEFAULT | REMINDER | FOCUSING | SESSION_RESULT | HIDDEN
```

`WidgetState` describes what the widget is doing. Visual presentation is `WidgetContext`, not an additional WidgetState.

#### Default state

- Mr. Bloom, the active plant, a miniature garden, and low-frame-rate idle animation.
- Current local time and date.
- Optional next-task or next-session summary.
- Short event-driven messages.
- Button to open the full application.

#### Context-aware presentation

The widget separates **functional state** from **visual context**. Functional state determines what the widget is doing; visual context changes how the same state looks.

Time-of-day context is calculated locally from the user's timezone:

```text
MORNING | AFTERNOON | EVENING | NIGHT
```

When weather-aware visuals are enabled, Blooming also resolves a coarse current-weather category:

```text
CLEAR | CLOUDY | RAINY | STORMY | FOGGY | SNOWY | UNKNOWN
```

Time and weather may change:

- Sky, lighting, and background ambience.
- Small decorative pixel-art effects such as rain, clouds, stars, or sunlight.
- Mr. Bloom's idle presentation and short contextual greeting.
- The visual treatment of the miniature garden.

They do **not** change task priority, scheduling, Pomodoro duration, reminder timing, Heart Progress, or GardenState progression. If weather-aware visuals are disabled, the widget uses time-only WidgetContext and does not apply a weather overlay. If weather data is unavailable or invalid, WeatherContext may be `UNKNOWN` and the widget still uses time-only presentation.

The final widget presentation is composed from independent layers rather than requiring a unique asset for every possible combination:

```text
WidgetState
+ WidgetContext
+ PlantType and GardenState
```

`WidgetState` describes what the widget is doing. `WidgetContext` contains the time-of-day and optional weather presentation context. It remains independent from `WidgetState`.

For example, the same `REMINDER` state may appear as `MORNING + CLEAR` or `NIGHT + RAINY` without becoming a different reminder workflow.

#### Reminder state

When a reminder or focus event becomes due, Mr. Bloom displays a short message inside the widget's chat bubble. Relevant actions are rendered as compact buttons inside the widget.

```text
Mr. Bloom:
"It is time to start Database."

[START_FOCUS] [REMIND_LATER] [OPEN_BLOOMING]
```

When at least one reminder is due and unread, Tauri switches the system-tray icon to its red-dot variant. The reminder content remains inside Mr. Bloom's widget chat bubble. Blooming does not display OS toast or banner notifications in the MVP.

If the widget is hidden, the reminder remains due and unread. The red-dot tray icon stays visible, and the reminder bubble appears when the widget is reopened. A later setting may allow the widget to reveal itself automatically.

#### Focus state

Focus begins only after the user opens Blooming, selects a task, configures Pomodoro, and presses Start.

- The clock changes into a Pomodoro countdown.
- The widget shows the current task and focus controls.
- Mr. Bloom changes to a focus animation.
- When the session ends, the widget enters `SESSION_RESULT` and Mr. Bloom displays a completion bubble and outcome actions.
- After `DONE` or `FINISHED_EARLY`, the widget returns to `DEFAULT`. After `NEED_MORE_TIME` or `SKIP`, Blooming re-plans remaining work and the widget returns to `DEFAULT`.

```text
DEFAULT -> REMINDER -> DEFAULT
DEFAULT -> FOCUSING -> SESSION_RESULT -> DEFAULT
```

The widget also supports `HIDDEN`. Closing it destroys its window and animation but keeps Tauri core running in the system tray. `Quit Blooming` exits completely.

The widget has no free-form chat and does not call the language model continuously.

### Block 3 — Daily Planning and Scheduling

Planning chat exists inside the full application. The user describes available time and intended work; Mr. Bloom extracts an editable Task Draft containing:

- Title and estimated duration.
- Priority and deadline.
- Core or optional status.
- Fixed or flexible status.
- Direct dependency, when present.

Blooming asks only questions that materially affect the plan, normally no more than one or two.

#### Reality Check

```text
COMFORTABLE | TIGHT | OVERLOADED
```

Blooming never silently compresses impossible work. It offers to remove optional work, reduce scope, change priority, or move work to another day.

#### Deterministic Scheduler

The scheduler handles available windows, fixed events, duration, priority, deadlines, breaks, buffers, direct dependencies, long-task splitting, overlaps, conflicts, and remaining time.

The user may add, delete, reorder, split, or move tasks and sessions through the interface or limited natural-language commands. Every edit is validated by the scheduler.

### Block 4 — Pomodoro, Focus, and Re-planning

The user selects a task inside Blooming and chooses:

```text
25 minutes focus / 5 minutes break
50 minutes focus / 10 minutes break
Custom
```

A standalone Pomodoro may use a quick task without requiring a complete Daily Plan.

Focus Mode provides start, pause, resume, end, current-task, and next-task controls. It remains correct when the UI is hidden or the computer sleeps.

When Pomodoro ends, the widget enters `SESSION_RESULT`. Mr. Bloom shows a completion message and the user chooses the session outcome there:

```text
DEFAULT
    -> FOCUSING
    -> SESSION_RESULT
    -> DONE -> DEFAULT
    -> FINISHED_EARLY -> DEFAULT
    -> NEED_MORE_TIME -> re-plan -> DEFAULT
    -> SKIP -> re-plan -> DEFAULT
```

`FINISHED_EARLY` enters `SESSION_RESULT` when the user ends a session before its expected end time because the intended work was completed. It returns to `DEFAULT` and does not automatically trigger re-planning. Planned and actual duration are stored separately. Outcome selection does not happen before `SESSION_RESULT`.

Re-planning preserves completed sessions, actual history, fixed events, and the active session; it may adjust only future flexible work, breaks, remaining duration, and optional tasks.

### Block 5 — Goals and Reminders

A goal contains a title, description, target date, status, and high-level roadmap. Roadmaps contain ordered milestones with expected outcomes, deadlines, statuses, and reminders.

Roadmaps provide direction but do not automatically create detailed tasks. Before a milestone deadline, Blooming asks whether the user wants to create a Daily Plan. Tasks are added only after confirmation. By default, milestone reminders are scheduled at 20:00 in the user's timezone on the day before the milestone deadline.

```text
CREATE_PLAN | MARK_COMPLETED | MOVE_MILESTONE | REMIND_LATER
```

For the desktop MVP:

- FastAPI stores reminder definitions, due times, and states.
- Tauri core synchronizes upcoming reminders at startup, after sleep, and after reminder changes.
- Tauri core evaluates synchronized reminder due times locally.
- When a reminder becomes due, Mr. Bloom displays a short templated message inside the widget's chat bubble.
- Reminder actions are rendered inside the widget and sent to FastAPI for validation and persistence.
- Coarse periodic synchronization is allowed; per-second backend polling is prohibited.
- If the widget is hidden, the reminder remains due and unread and is displayed when the widget is reopened.
- Reminders require Blooming to remain running in the foreground or system tray.
- The red-dot tray indicator remains visible while at least one due reminder is unread. It disappears after all due reminders have been viewed, completed, dismissed, or rescheduled.

Server scheduling is added later only for email, push, or jobs that must run while Blooming is fully closed.

### Block 6 — Heart Progress, Plant Selection, and Living Garden

Heart Progress is permanent visual progress, not spendable currency. It increases when the user completes a valid focus session, task, core objective, milestone, or recovery plan.

Opening Blooming grants no progress, and the same completion cannot grant repeated rewards.

```text
DORMANT -> SPROUTING -> GROWING -> BLOOMING -> FLOURISHING
```

Growth appears through new leaves, flowers, fuller foliage, and species-appropriate details in the application and small widget changes. Numerical Heart values do not need emphasis; the visual garden is the primary reward.

#### Plant types and switching

The MVP includes five preset plant types:

```text
POTHOS | CACTUS | BONSAI | SUNFLOWER | LOTUS
```

Only one plant type is active at a time. Switching the active plant changes the visual plant asset but does not create a new progression track.

When the user switches plant type:

- Heart Progress is preserved.
- The current GardenState stage is preserved.
- Focus, task, milestone, and recovery history are preserved.
- No currency, purchase, unlock, or inventory action is required.

The frontend selects the plant artwork from the combination of `PlantType` and the shared `GardenState`. Time and weather are rendered as separate ambient layers so the number of plant assets does not multiply across every weather and time combination.

The MVP excludes currency, inventory, shops, multiple simultaneous gardens or plant progress tracks, free-form decoration, and permanent character death. A later Vitality system must preserve earned progress and allow gentle recovery.

## 5. Main Interfaces

| Surface | Purpose |
| --- | --- |
| Desktop Widget | Mr. Bloom, active plant, miniature garden, context-aware clock ambience, reminder bubbles, compact actions, and active Pomodoro |
| Today | Planning chat, Task Draft, timeline, task selection, Pomodoro setup, and re-planning |
| Goals | Goals, roadmaps, milestones, and reminder actions |
| Settings | Account, timezone, focus defaults, widget behavior, quiet hours, Mr. Bloom's name, active plant, and weather-context preferences |

The full application opens directly to Today. The MVP does not require separate chat or garden screens.

## 6. Framework and Architecture

### Platforms

Blooming targets Windows and Linux desktop environments. Windows is the primary development platform, but Linux compatibility must be validated before the MVP is considered complete.

### Technology stack

| Layer | Technology |
| --- | --- |
| Desktop shell | Tauri 2 / Rust |
| Desktop UI | Svelte + TypeScript + Vite |
| Backend API | Python + FastAPI + Pydantic |
| Persistence | PostgreSQL + SQLAlchemy |
| AI | Remote LLM API with validated structured outputs |
| Authentication | JWT |
| Reminder presentation | Tauri tray red-dot indicator + event-driven Svelte chat bubbles |
| Weather context | Remote weather API accessed through FastAPI with coarse caching |
| Deployment | Dockerized backend |

The Tauri notification plugin is not required in the MVP. A server scheduler or queue is introduced only for server-originated email, push, or offline jobs.

### Runtime architecture

```text
Blooming Desktop
├── Tauri Core
│   ├── System tray and window lifecycle
│   ├── Local timer calculation
│   ├── Local reminder timing
│   └── Local time-of-day context
├── Widget Window
│   ├── Mr. Bloom, active plant, and clock
│   ├── Time-of-day theme and optional weather overlay
│   ├── Reminder and focus-event chat bubbles
│   ├── Compact reminder actions
│   └── Active Pomodoro display
└── Main Window
    └── Lazy-loaded planning interface
            │
            ▼ HTTPS
FastAPI Backend
├── Auth and User
├── Daily Plan and Scheduler
├── Focus and Re-planning
├── Goals and Reminders
├── Heart, Plant, and Garden
├── Weather Context
├── Connects to PostgreSQL
└── Calls the LLM API
```

### Timer and reminder ownership

```text
Start focus
    -> FastAPI stores started_at and expected_end_at
    -> Tauri core calculates the countdown locally
    -> Svelte widget displays the countdown
    -> Pause, Resume, End, or Outcome synchronizes with FastAPI

Reminder becomes due
    -> Tauri core marks it as due and unread
    -> Tauri switches the tray icon to its red-dot variant
    -> Svelte widget displays Mr. Bloom's reminder bubble
    -> Tauri marks the reminder as read and synchronizes its state with FastAPI
    -> Tauri clears the red dot when no unread reminder remains
    -> Any user action is validated and stored by FastAPI
```

| Responsibility | Owner |
| --- | --- |
| Store timer timestamps and status | FastAPI |
| Calculate countdown | Tauri core |
| Display countdown | Svelte widget |
| Store reminder records and state | FastAPI |
| Evaluate reminder due times locally | Tauri core |
| Display and clear the tray unread indicator | Tauri core |
| Display Mr. Bloom's reminder bubble | Svelte widget |
| Process reminder actions | FastAPI |

FastAPI never receives one request per second. After sleep or a temporary disconnection, Tauri recalculates the timer from timestamps and synchronizes the latest state.

### Widget context ownership

```text
Time context
    -> Tauri resolves local time from the configured timezone
    -> Widget selects MORNING / AFTERNOON / EVENING / NIGHT

Weather context
    -> User enables weather-aware visuals and provides a city or optional coarse location
    -> FastAPI requests and caches current conditions from a weather provider
    -> FastAPI maps provider data to a coarse WeatherContext
    -> Tauri synchronizes the latest WeatherContext periodically
    -> Widget applies the corresponding ambient overlay
```

Weather is presentation data only. It is refreshed coarsely, for example at startup, after wake, after location changes, and at a low-frequency interval rather than continuously. Precise GPS history is not stored or required. If weather-aware visuals are disabled, no weather overlay is applied and WidgetContext is time-only; WeatherContext is not required to be `UNKNOWN`. If synchronization fails, WeatherContext may be `UNKNOWN` and time-based visuals continue normally. `UNKNOWN` never affects scheduling, reminders, Heart Progress, or planning.

| Responsibility | Owner |
| --- | --- |
| Resolve time-of-day context | Tauri core |
| Store plant and weather preferences | FastAPI |
| Fetch and normalize weather conditions | FastAPI |
| Cache weather context | FastAPI |
| Display time/weather ambience | Svelte widget |
| Persist active plant type | FastAPI |
| Select plant asset from PlantType and GardenState stage | Svelte UI |

### Resource-efficiency rules

- Widget and main application use separate frontend entry points.
- The planning bundle loads only when the main window opens.
- Closing the widget destroys its WebView; Tauri core remains.
- Pixel art uses small sprite sheets; hidden animation pauses.
- Time themes, weather overlays, and plant sprites are composited from reusable layers instead of pre-rendering every combination.
- Weather context is refreshed at a coarse interval and cached; it is never polled per second.
- FastAPI, PostgreSQL, and LLM inference run remotely.
- The client does not poll continuously.
- No local LLM, bundled Python backend, or native-notification plugin is required.

## 7. AI and Application Boundary

The AI layer handles natural-language extraction, essential clarification, priority and dependency suggestions, roadmap drafting, editing-intent parsing, and explanations.

Deterministic code handles scheduling, conflicts, time calculations, fixed events, breaks, timer state, reminder timing, Heart Progress, GardenState stages, active plant selection, time-of-day context, weather-context fallback, and database transactions. External weather data is normalized into a small presentation-only context before reaching the widget.

Any AI output that changes system state must be validated as structured data before execution.

## 8. Core Domain Model

```text
User, UserSettings
PlanningSession, PlanningMessage
Task, DailyPlan, PlanBlock, PlanRevision, FocusRun
Goal, Milestone, Reminder, ReminderAction
HeartEvent, GardenState, PlantType
WidgetState, WidgetContext, WeatherContext, WeatherSnapshot
```

- `Task` is intended work.
- `PlanBlock` is a scheduled portion of a task.
- `FocusRun` records actual execution.
- `PlanRevision` records a meaningful re-plan.
- `HeartEvent` is an auditable Heart Progress reward, not currency.
- `PlantType` is the user's currently selected visual plant; it does not own separate progress.
- `WidgetState` describes what the widget is doing: `DEFAULT`, `REMINDER`, `FOCUSING`, `SESSION_RESULT`, or `HIDDEN`.
- `WidgetContext` contains the time-of-day and optional weather presentation context. It remains independent from `WidgetState`.
- `WeatherContext` is a normalized coarse category used only for visuals.
- `WeatherSnapshot` stores the latest cached weather context and freshness metadata, not a location-history trail.
- `PlanningSession` and `PlanningMessage` are runtime/domain concepts for full-application planning chat. They do not require storing raw conversational text.

## 9. Explicitly Outside the MVP

- General-purpose or emotional companion chat.
- Free-form chat inside the widget.
- Semantic memory, vector search, RAG, LangGraph, or multi-agent workflows.
- Random proactive AI messages and voice chat.
- Google Calendar integration.
- OS toast or banner notifications, email, or push reminders.
- Team, social, or shared planning.
- A roaming transparent desktop pet.
- Shops, inventory, currency, multiple simultaneous gardens or separate plant progression tracks, or free-form garden building.
- Plant unlock economies, rarity systems, or collectible plant inventories.
- Weather-driven scheduling, productivity scoring, rewards, penalties, or gameplay effects.
- Detailed weather forecasts, seasonal simulation, and continuous or historical GPS tracking.
- User-uploaded skins and complex accessories.
- Full offline planning and AI.
- Mobile, web-only, and macOS releases.

## 10. MVP Success Criteria

Blooming succeeds when a user can:

1. Create a feasible, editable Daily Plan from a natural-language description.
2. Keep a lightweight Mr. Bloom clock widget visible on Windows or Linux.
3. Select a task in the app, start Pomodoro, and see the widget switch to an accurate countdown.
4. Receive due reminders through a red-dot tray indicator and Mr. Bloom's widget bubble without OS notifications or per-second backend polling.
5. Hide the widget, reopen it, and receive reminders that became due while it was hidden.
6. Complete, extend, or skip a session and repair future work without changing completed history.
7. Connect a long-term milestone to a confirmed Daily Plan.
8. See meaningful progress reflected in the garden without punishment for imperfection.
9. Switch among the preset plant types without resetting Heart Progress, GardenState stage, or execution history.
10. See the widget automatically use the correct morning, afternoon, evening, or night presentation for the configured timezone.
11. Enable weather-aware visuals and see the widget apply a coarse weather ambience when data is available, while falling back cleanly to time-only presentation when it is not.

> Open Blooming to plan. Keep Mr. Bloom on the desktop to follow the plan. Let the widget reflect the time, weather, and plant you chose. Focus when it is time to act. Re-plan when reality changes.
