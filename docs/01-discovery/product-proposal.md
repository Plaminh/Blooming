# Product Proposal: Blooming

## 1. Executive summary

Blooming is a Windows and Linux desktop planner for people who regularly create more work than can fit into their day. It converts natural-language intentions into a realistic Daily Plan, supports Pomodoro execution through a lightweight Mr. Bloom widget, and repairs unfinished work when reality changes.

The product uses AI where language understanding is valuable, but it does not allow an LLM to determine schedule correctness. Natural-language input is converted into structured data, validated, and passed to a deterministic scheduling engine.

The first release is a solo portfolio project. It delivers one constrained loop: daily planning and recovery, connected to long-term milestones, desktop reminders, Heart Progress, and one GardenState with selectable PlantType. Mr. Bloom is a small robot cat: warm, concise, occasionally enthusiastic, and honest about unrealistic plans. He is not a general-purpose companion.

The frozen concept is `../02-product/Blooming-Concept-Updated.md`.

## 2. Problem and value

| Element | Statement |
|---|---|
| Problem | Task lists do not show whether the planned workload fits the user's actual available time, and plans collapse after the first disruption. |
| Affected users | Students, self-directed learners, and individual knowledge workers. |
| Current impact | Over-planning creates stress, missed tasks, repeated manual rescheduling, and loss of trust in planning tools. |
| Successful outcome | The user receives a feasible, editable Daily Plan, understands any overload, follows the plan from the widget, focuses, and recovers after disruption. |

## 3. Target users and environment

- Primary user: an individual student or knowledge worker managing personal work and study.
- Devices/platforms: Windows and Linux desktop. No MVP web-only, mobile, or macOS product.
- Usage context: daily planning in the full application; widget follow-through between sessions.
- Constraints: limited attention, incomplete estimates, changing availability, and possible concern about sending personal text to an AI provider.

## 4. Proposed solution

The user describes available time and intended work in the full application. Blooming validates the Task Draft, calculates Reality Check (`COMFORTABLE` / `TIGHT` / `OVERLOADED`), and generates a non-overlapping PlanBlock timeline. The user may resolve overload or edit the result before saving.

The user selects a task, starts Pomodoro, and follows the countdown on the widget. Outcomes are `DONE`, `NEED_MORE_TIME`, `SKIP`, and `FINISHED_EARLY`. Blooming then re-plans only unfinished flexible work while preserving completed history and fixed events.

## 5. Key functional groups

| Functional group | What it does | User value |
|---|---|---|
| Daily planning | Converts a Task Draft into PlanBlocks | Replaces manual time-blocking |
| Reality Check | Calculates capacity and exposes overload | Prevents impossible plans |
| Plan review and editing | Lets the user accept or change the timeline | Preserves user control |
| Mr. Bloom in the full app | Extracts tasks, asks material clarifications, drafts plans/roadmaps, explains trade-offs | Reduces input friction while preserving user control |
| Desktop widget | Clock, reminder bubble, Pomodoro countdown, composed garden ambience | Keeps the plan present without the full app |
| Focus execution | Runs recoverable Pomodoro sessions and records FocusRun outcomes | Connects planning with action |
| Adaptive re-planning | Reschedules only remaining work | Makes the plan resilient |
| Goals and reminders | Connects Milestone reminders to a confirmed Daily Plan | Gives long-term intent a practical next step |
| Heart Progress and garden | Permanent visual progress plus one PlantType over a shared GardenState | Makes completed work visible without a shop or inventory |

## 6. AI-powered capability

- Input: the user's natural-language description of tasks, timing, constraints, and preferences, captured only in the full application.
- Output: a structured Task Draft plus explicit clarification questions when required fields are missing.
- User value: faster task capture without surrendering control over the result.
- Deterministic control: backend schema validation rejects invalid AI output; the scheduling engine, not the LLM, creates the timeline.
- Fallback: the user can enter or edit the same information through a normal form.
- The widget does not run continuous AI chat.

## 7. Initial scope

### Included

- Natural-language and structured Daily Plan creation.
- Available windows, fixed events, Reality Check, and deterministic scheduling.
- Today, Goals, and Settings in the full application; Mr. Bloom widget as a second surface.
- FocusRun timer ownership: FastAPI stores timestamps; Tauri calculates; the widget displays.
- Adaptive re-planning with protected history.
- JWT authentication, timezone, focus defaults, quiet hours, widget preferences, PlantType, and weather-context preferences.
- Desktop reminder architecture: FastAPI storage, Tauri local evaluation, tray red-dot, widget bubble.
- Heart Progress, GardenState stages through `FLOURISHING`, and visual PlantType switching.
- Presentation-only time and weather widget layers with time-only fallback.
- Dockerized FastAPI backend.

### Excluded

- Team collaboration and social features.
- Full calendar replacement or Google Calendar integration.
- OS toast/banner notifications, email, or push reminders.
- Voice input, analytics, RAG, LangGraph, and autonomous agents.
- Medical or mental-health advice.
- Multiple plant progress tracks, inventory, shop, currency, gacha, plant death, pet simulation, world map, or quests.
- Weather-driven planning or rewards.
- Mobile, web-only, and macOS releases.

## 8. Feasibility and risks

| Area/risk | Assessment | Response |
|---|---|---|
| Deterministic scheduler complexity | Amber | Start with explicit rules, pure domain logic, and boundary tests. |
| LLM output reliability | Amber | Use structured output, backend validation, clarification, and manual fallback. |
| Desktop reminder timing | Amber | Store due times in FastAPI; evaluate locally in Tauri; never poll the backend per second. |
| Weather/provider dependency | Amber | Cache coarsely; fall back to time-only presentation; never let weather change planning. |
| Scope growth | Red | Keep widget, garden, and weather at the documented presentation depth. |
| API and hosting cost | Amber | Minimize prompts, cap requests, observe usage, and preserve a non-AI input path. |
| Solo development capacity | Amber | Use a FastAPI modular monolith and one canonical document per concern. |
| Core stack | Green | Tauri 2, Svelte, FastAPI, PostgreSQL, and Docker match the frozen concept. |

## 9. Delivery sequence

| Increment | Deliverable |
|---|---|
| Scheduler A | Domain model, validation, interval normalization, feasibility, and dependency-aware ordering |
| Scheduler B | Placement, splitting, breaks, unscheduled reasons, invariant verification, and performance evidence |
| Daily planning loop | Preview, persistence, overload resolution, and validated editing |
| Conversational and execution loop | Mr. Bloom Task Draft, FocusRun execution, widget countdown, and adaptive re-planning |
| Connected MVP | Goals/reminders, Heart Progress, PlantType, weather-context visuals, deployment, and full regression |

No calendar completion dates are claimed until implementation capacity is known.

## 10. Decision

**Proceed.** The core value can be demonstrated through a constrained vertical slice, the main technical risks can be isolated and tested, and the product provides portfolio evidence across requirements, backend domain logic, a desktop shell, AI integration, testing, and deployment.
