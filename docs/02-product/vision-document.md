# Vision Document: Blooming

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Current |
| Last updated | 8 September 2026 |

## Revision history

| Date | Version | Change |
|---|---|---|
| 8 September 2026 | 1.0 | Established the personal-project vision and MVP boundary. |

## 1. Introduction and references

This document defines Blooming's product direction, users, system boundary, core features, and high-level quality goals. Detailed release commitments live in `mvp-scope.md`; observable behavior lives in the requirements and feature specifications.

References:

- `../01-discovery/product-proposal.md`
- `../01-discovery/app-survey.md`
- `mvp-scope.md`
- `../04-requirements/domain-rules.md`

## 2. Positioning

### Problem statement

| Element | Statement |
|---|---|
| The problem of | Creating task lists and schedules that ignore real capacity and become obsolete after disruption |
| Affects | Students and individual knowledge workers managing changing personal days |
| The impact is | Stress, repeated manual re-planning, abandoned plans, and reduced trust in planning tools |
| A successful solution would | Produce an understandable feasible plan, expose overload, support execution, and adapt without rewriting completed history |

### Product position statement

For individuals who need to organize busy days and long-term goals, Blooming is an adaptive conversational personal planner that turns intentions into realistic, editable plans. Unlike a task list, calendar replacement, timer, chatbot wrapper, or pet game, it separates language interpretation from deterministic scheduling, shows when work cannot fit, connects milestones to tomorrow's plan, and supports recovery.

## 3. Stakeholders and users

| Stakeholder/user | Description | Goals and needs |
|---|---|---|
| Primary user | Student or individual knowledge worker | Plan quickly, avoid overload, retain control, focus, and recover from disruption |
| Developer and maintainer | Solo project owner | Keep scope manageable, architecture testable, and documentation consistent with code |
| LLM provider | External semantic-processing service | Receive valid requests within provider limits; must not become the scheduling authority |
| Hosting provider | Runs the deployed web/API/database services | Receive secure configuration and health-checkable artifacts |

### User environment

- The user plans on a modern desktop or mobile browser.
- Planning commonly occurs before a study/work block; updates happen between sessions.
- The user may have incomplete estimates and fixed commitments.
- The experience must remain usable when the AI feature fails, times out, or is disabled.
- The interface should be calm and non-judgmental, especially after skipped or delayed work.

## 4. Product overview

### Product perspective

Blooming is a standalone personal web application. The web client communicates with the Blooming API; the API owns validation, scheduling, persistence, reminders, plant state, and re-planning. An external LLM may interpret natural language, but its output is untrusted input. Google Calendar integration, social, and team systems remain outside the MVP boundary; in-app and basic email milestone reminders are included.

### Product principles

- Tell the truth about capacity; never make an overloaded day appear feasible.
- Preserve user agency; generated plans are suggestions that remain editable.
- Separate AI interpretation from deterministic business rules.
- Preserve history; re-planning must not rewrite completed execution.
- Encourage recovery without shame or loss of earned progress.
- Prefer one working vertical slice over many disconnected features.
- Recover over perfect: missing work or a delayed milestone is not plant damage.

### Core loop

```mermaid
flowchart LR
    Intent --> RealityCheck["Reality check"]
    RealityCheck --> Plan
    Plan --> Focus
    Focus --> Adapt
    Adapt --> Progress
```

### Assumptions and dependencies

| Type | Statement | Validation or review trigger |
|---|---|---|
| Assumption | Users can provide or accept rough duration estimates. | Observe repeated correction or abandonment during usability testing. |
| Assumption | A visible overload explanation is more useful than silently dropping work. | Test overload scenarios with users. |
| Dependency | Conversational input requires an external LLM API. | Select and privacy-review a provider before implementing conversational integration. |
| Dependency | Persistence and deployment require PostgreSQL and a hosting environment. | Confirm before persistence and release work respectively. |
| Constraint | The MVP is implemented by one developer in small evidence-producing increments. | Split an increment when its acceptance evidence cannot be completed coherently. |
| Constraint | AI cost must remain bounded and the planner must work without AI. | Review after AI evaluation. |

## 5. Product features

### Reality-aware Quick Planning

The user defines an available time window, Tasks, non-Task fixed events, deadlines, core/optional and fixed/flexible classifications, and focus preferences. Blooming validates these inputs, locks fixed Tasks at their fixed start, places flexible Tasks automatically, calculates usable capacity and workload, and classifies the request as Comfortable, Tight, or Overloaded. It returns one ordered PlanBlock timeline containing Focus, Break, and unchanged Fixed Event blocks; the frontend does not reconstruct events separately.

### Plan review and editing

The user sees the generated timeline, warnings, and unscheduled tasks before committing it. Basic edits are validated against the same rules as automatic scheduling. The system does not silently shorten work or create overlaps to make an edit appear successful.

### Conversational task capture

The user speaks with Mr. Bloom, an old AI robot and the central conversational guide. He is mature, calm, practical, concise, assertive about unrealistic plans, supportive without excessive enthusiasm, and non-judgmental after disruption. He continues a long-term mission to help restore plant life in a distant machine-dominated future. An LLM converts the user's day or goal into a structured draft or asks a small number of material clarification questions. The user can review the interpreted data, and a form remains available as fallback.

### Focus execution

The user starts a focus session from a planned block and records `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, or `SKIP`. Timer state survives refresh, and execution history never changes the original past.

### Adaptive re-planning

When work takes longer, is skipped, or availability changes, Blooming freezes completed history, fixed events, and locked fixed-Task blocks, then deterministically schedules unfinished flexible work into the remaining time. It explains meaningful changes and returns anything that no longer fits.

### Goals, reminders, and living plant

The user can create a long-term goal with an editable high-level roadmap and milestones. A default reminder at 20:00 in the user's timezone on the day before a milestone deadline can start tomorrow's planning only after the user confirms work to add. One active plant represents sustained progress through backend-owned growth, health, and Water Reserve. Meaningful activity and Rest Mode support the plant; missed tasks, longer tasks, delayed milestones, and active recovery do not directly damage it.

## 6. High-level quality requirements

| Quality | Target |
|---|---|
| Performance | Scheduler preview completes within 500 ms at the backend for up to 50 tasks, excluding network latency. |
| Reliability | No accepted plan contains an overlap or a session outside its available window. |
| Persistence | Saved plans and active timer state survive browser refresh and service restart within the documented recovery model. |
| Security/privacy | Secrets and personal planning content are excluded from source control and application logs; external transfer is minimized and disclosed. |
| Accessibility | Critical planning and focus flows are keyboard-operable and do not rely on color alone. |
| AI quality/cost | Invalid AI output never reaches the scheduler unvalidated; requests are capped and have a manual fallback. |

## 7. Future direction

Possible later releases include calendar integration, preference learning, analytics, richer plant variations, and native mobile experiences. These directions do not expand the first MVP unless the core daily loop has passed correctness and usability checks.
