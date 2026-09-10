# Domain Glossary and Business Rules

## Core model

| Concept | Definition |
|---|---|
| `Task` | Work the user intends to accomplish: title, estimate, priority, deadline when applicable, core/optional and fixed/flexible classification, and direct dependencies. |
| `DailyPlan` | A user-local daily plan with windows, fixed events, tasks, PlanBlocks, and revisions. |
| `PlanBlock` | A scheduled `FOCUS`, `BREAK`, or `FIXED_EVENT` portion of a plan; one Task can have many focus blocks. |
| `FocusRun` | Actual execution record linked to a focus block; planned and actual time are separate. |
| `PlanRevision` | A meaningful re-plan, retaining the protected before-state and reason. |
| `Goal` / `Milestone` | A long-term desired outcome and its editable high-level roadmap step; a roadmap is not a complete future task list. |
| `Reminder` / `ReminderAction` | FastAPI-stored reminder definition/state. Milestone ReminderAction values are `CREATE_PLAN`, `MARK_COMPLETED`, `MOVE_MILESTONE`, and `REMIND_LATER`. Focus/task widget actions `START_FOCUS` and `OPEN_BLOOMING` are not Milestone ReminderAction values. |
| `HeartEvent` | An auditable Heart Progress reward. Heart Progress is permanent visual progress, not spendable currency. |
| `GardenState` | The one shared garden progression: `DORMANT` → `SPROUTING` → `GROWING` → `BLOOMING` → `FLOURISHING`. |
| `PlantType` | The currently selected visual plant: `POTHOS`, `CACTUS`, `BONSAI`, `SUNFLOWER`, or `LOTUS`. It does not own separate progress. |
| `WidgetState` | Functional widget state: `DEFAULT`, `REMINDER`, `FOCUSING`, `SESSION_RESULT`, or `HIDDEN`. |
| `WidgetContext` | Time-of-day and optional WeatherContext used only for visual presentation. It remains independent from `WidgetState`. |
| `WeatherContext` | Coarse presentation category: `CLEAR`, `CLOUDY`, `RAINY`, `STORMY`, `FOGGY`, `SNOWY`, or `UNKNOWN`. |
| `WeatherSnapshot` | Cached current WeatherContext and freshness metadata, not a location-history trail. |
| `PlanningSession` / `PlanningMessage` | Runtime/domain concepts for full-application planning chat. They do not require storing raw message text in PostgreSQL. The widget does not own a chat session. |

## Scheduling and recovery rules

| ID | Rule |
|---|---|
| BR-001 | Every generated `FOCUS`/`BREAK` PlanBlock and locked fixed-Task sequence must lie within the available window and must not overlap another generated/locked block or any fixed event. Unchanged `FIXED_EVENT` blocks may overlap one another or extend partly outside the window because BR-022 normalizes clipped copies only for capacity. |
| BR-002 | `FOCUS`, `BREAK`, and `FIXED_EVENT` are the only PlanBlock types. Fixed events remain unchanged. |
| BR-003 | Scheduled plus unscheduled focus duration must equal a Task estimate; impossible work must not be silently compressed. |
| BR-004 | The scheduler must use windows, fixed events, duration, priority, deadline, core/optional, fixed/flexible, dependencies, breaks, buffers, and splitting rules. |
| BR-005 | Reality Check returns `COMFORTABLE`, `TIGHT`, or `OVERLOADED`. An overload explains the conflict and offers removing optional work, reducing scope/duration, keeping the core outcome, moving work, or choosing priority. |
| BR-006 | Every manual or conversational time-affecting edit must be validated by deterministic scheduling code. |
| BR-007 | The AI layer may extract/suggest/explain, but cannot authoritatively set timestamps, feasibility, conflicts, fixed events, reminder execution, Heart Progress, GardenState, PlantType, WeatherContext, or database state. |
| BR-008 | A re-plan may adjust only unfinished flexible future work and upcoming breaks. It preserves completed FocusRuns, actual history, fixed events, locked fixed-Task PlanBlocks, and the active session unless the user requests a change. |
| BR-009 | Focus outcomes are exactly `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, and `SKIP`. |
| BR-010 | `NEED_MORE_TIME` and `SKIP` create a recoverable remaining-work decision; they do not rewrite past execution. |

## Goals and reminders

| ID | Rule |
|---|---|
| BR-011 | A Milestone has expected outcome, deadline, order, status, and reminder configuration. Moving one warns about downstream milestones and offers an equal-day shift. |
| BR-012 | The default reminder is 20:00 in the user's timezone, one day before the milestone deadline. |
| BR-013 | Milestone ReminderAction values are `CREATE_PLAN`, `MARK_COMPLETED`, `MOVE_MILESTONE`, and `REMIND_LATER`; tasks enter a Daily Plan only after user confirmation. Focus/task widget actions may include `START_FOCUS`, `REMIND_LATER`, and `OPEN_BLOOMING`; `START_FOCUS` and `OPEN_BLOOMING` are not Milestone ReminderAction values. |
| BR-014 | Reminder persistence is idempotent per reminder occurrence and action. FastAPI stores definitions and state. Tauri evaluates synchronized due times locally. The MVP presents due reminders through the tray red-dot and the widget bubble. There is no OS toast, email, or push in the MVP. |

## Heart Progress, garden, widget, and weather

| ID | Rule |
|---|---|
| BR-015 | There is one GardenState at a time. Growth stages are `DORMANT`, `SPROUTING`, `GROWING`, `BLOOMING`, and `FLOURISHING`. |
| BR-016 | Heart Progress increases only for a valid completed focus session, task, core objective, milestone, or recovery plan. Opening Blooming grants no progress. The same completion cannot grant repeated rewards. |
| BR-017 | Switching PlantType changes visual artwork only. Heart Progress, GardenState stage, and execution history are preserved. No inventory, shop, currency, or per-plant progression exists. |
| BR-018 | Missing a task, taking longer, delaying a milestone, or re-planning does not erase Heart Progress or punish the user. Permanent plant death is outside the MVP. |
| BR-019 | Time-of-day (`MORNING`, `AFTERNOON`, `EVENING`, `NIGHT`) and WeatherContext affect only visual presentation (widget ambience and garden ambient layers). They must not change scheduler decisions, task priority, reminder timing, Heart Progress, or planning logic. |
| BR-020 | If weather-aware visuals are disabled, omit the weather overlay and use time-only WidgetContext; WeatherContext is not required to be `UNKNOWN`. If weather fetch is unavailable or invalid, WeatherContext may be `UNKNOWN` and presentation is time-only. `UNKNOWN` never affects scheduling, reminder timing, Heart Progress, or planning. Weather is cached coarsely; continuous GPS and location history are not stored. |

## Time and validation

- Store instants in UTC, retain an IANA user timezone and local planning date, and use start-inclusive/end-exclusive intervals.
- Validate unavailable/invalid windows, dependencies, deadlines, and conflicts before persistence.
- State-changing AI output must be strict structured data validated by the same paths as forms.

## Detailed Quick Planning rules

| ID | Rule |
|---|---|
| BR-021 | Available-window start must precede end, Task titles must contain 1–200 trimmed characters, estimates must be 1–1440 minutes, and `minimumBlockDuration` must be between 1 and `focusDuration`. The initial preview supports at most 50 Tasks and 50 fixed events, focus durations of 15–180 minutes, break durations of 0–60 minutes, and buffer percentages of 0–50; all ranges are validated before scheduling. |
| BR-022 | Fixed events are clipped to the available window and overlapping or adjacent occupied intervals are merged before free intervals and capacity are calculated. |
| BR-023 | Scheduling intervals are start-inclusive and end-exclusive, so adjacent PlanBlocks and fixed events do not overlap. |
| BR-024 | Task IDs must be unique, every dependency must reference another task in the request, self-dependencies are invalid, and the dependency graph must be acyclic. |
| BR-025 | Dependency-ready Tasks use a stable deterministic topological ordering. A dependent Task cannot start until its prerequisites are fully scheduled. |
| BR-026 | Core Tasks are considered before optional Tasks when both are dependency-ready; optional work remains unscheduled first when capacity is insufficient. |
| BR-027 | Within the same dependency-ready core/optional group, Tasks with earlier deadlines are considered before Tasks with later or no deadlines; ties are ordered by priority from high to low and then by original input position. |
| BR-028 | A non-splittable Task must occupy one continuous free interval or remain entirely unscheduled with a fragmentation reason. |
| BR-029 | A splittable Task may use multiple `FOCUS` PlanBlocks. A block must not exceed the configured focus duration and must meet the configured minimum block duration, except when the entire Task is shorter and valid; a too-small remainder is rebalanced or returned unscheduled. |
| BR-030 | For full-request demand, `requiredBreakCount = max(0, expectedFocusBlockCount - 1)`. While work continues, one explicit `BREAK` PlanBlock is placed between consecutive scheduled `FOCUS` PlanBlocks. No break follows the final `FOCUS` block. Fixed events neither become nor replace `BREAK` blocks. Breaks attributable to unscheduled work count toward full-request feasibility but are not emitted as PlanBlocks. |
| BR-031 | Buffer is `ceil((workload minutes + required break minutes) × buffer percentage / 100)` and counts toward feasibility without becoming a PlanBlock. |
| BR-032 | Let demand equal workload plus required breaks plus buffer. `COMFORTABLE` means demand is at most 80% of available minutes, `TIGHT` means demand is above 80% but no greater than available minutes, and `OVERLOADED` means demand exceeds available minutes; zero demand is `COMFORTABLE`. |
| BR-033 | Capacity status and placement are distinct: fragmentation may leave work unscheduled even when total capacity is sufficient. Unscheduled work must retain exact remaining minutes and a stable reason such as `INSUFFICIENT_CAPACITY`, `NO_CONTIGUOUS_INTERVAL`, `DEPENDENCY_UNSCHEDULED`, `MINIMUM_BLOCK_NOT_MET`, `DEADLINE_EXCEEDED`, `FIXED_TASK_CONFLICT`, or `FIXED_TASK_OUTSIDE_WINDOW`. |
| BR-034 | Identical normalized input and configuration must produce identical ordered feasibility, PlanBlock, warning, and unscheduled-work output, excluding request metadata. |
| BR-035 | A Task deadline is a latest-finish constraint. Every `FOCUS` PlanBlock for that Task must end at or before its deadline; work that cannot finish by then remains unscheduled with `DEADLINE_EXCEEDED`. |
| BR-036 | A fixed Task requires a fixed start time. Its first `FOCUS` PlanBlock begins at that time; any remaining Focus blocks and intervening Breaks form one locked sequence. The sequence is validated against windows, deadlines, fixed events, other fixed Tasks, breaks, and PlanBlock overlap, and is preserved during re-planning. A flexible Task has no fixed start and is placed automatically. |
| BR-037 | Fixed events are non-Task commitments and remain distinct from fixed Tasks. Scheduler output is one ordered `PlanBlock[]` timeline containing unchanged `FIXED_EVENT` blocks alongside generated `FOCUS` and `BREAK` blocks; the frontend must not reconstruct fixed events separately. |
