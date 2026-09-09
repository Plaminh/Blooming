# Functional Requirements

Requirements use **must** for required behavior, **should** for intended non-critical behavior, and **may** for optional behavior.

## User, settings, and assistant

Mr. Bloom is an old AI robot and Blooming's central conversational guide. He is mature, calm, practical, concise, assertive when a plan is unrealistic, supportive without excessive enthusiasm, and non-judgmental when the user falls behind. He continues a long-term mission to help restore plant life in a distant machine-dominated future; this identity does not create customization, pet, quest, campaign, or multi-agent behavior.

| ID | Requirement |
|---|---|
| FR-USER-001 | The system must register, authenticate, and log out users with JWT-based authentication. |
| FR-USER-002 | The system must enforce ownership for every user-owned read or state change. |
| FR-SET-001 | The system must store a basic profile, IANA timezone, default focus/break duration, milestone-reminder configuration, email-reminder enablement, and Rest Mode configuration. |
| FR-AI-001 | Mr. Bloom must provide onboarding, extraction, limited editing, clarification, overload/conflict explanation, recovery, milestone, and plant-status messages using the canonical intents. |
| FR-AI-002 | The system must use validated structured output for an AI response that affects state; a normal structured form must remain available when AI interpretation fails. |
| FR-AI-003 | Mr. Bloom must ask clarification only when missing information materially affects feasibility or ordering, normally no more than one or two questions. |

Where an intent is persisted, exchanged, or tested, it must be one of `CREATE_DAILY_PLAN`, `EDIT_DAILY_PLAN`, `CREATE_GOAL`, `EDIT_ROADMAP`, `REPLAN`, `EXPLAIN_PLAN`, or `GENERAL_RESPONSE`.

## Daily planning, focus, and recovery

| ID | Requirement |
|---|---|
| FR-PLAN-001 | The system must accept structured and natural-language Task input, available windows, non-Task fixed events, estimates, priority, deadline where applicable, core/optional, fixed/flexible, fixed start time for fixed Tasks, and direct dependencies. |
| FR-PLAN-002 | The system must present an editable Task Draft before scheduling natural-language input. |
| FR-PLAN-003 | The deterministic scheduler must return one ordered `PlanBlock[]` timeline containing generated `FOCUS` and `BREAK` blocks plus unchanged `FIXED_EVENT` blocks. Generated/locked blocks must fit available windows and Task deadlines and must not overlap each other or a fixed event; unchanged fixed events may overlap one another or extend partly outside a window. Each fixed Task must produce a validated locked sequence whose first `FOCUS` block begins at its fixed start time. |
| FR-PLAN-004 | The system must calculate and display `COMFORTABLE`, `TIGHT`, or `OVERLOADED`; overload must offer feasible alternatives and must not silently compress work. |
| FR-PLAN-005 | The system must persist reviewed plans and validate every manual or conversational time edit before it is accepted. |
| FR-FOCUS-001 | Today must show the timeline, current/next session, upcoming break, daily progress, appropriate plant status, and Focus Mode. |
| FR-FOCUS-002 | Focus Mode must support countdown, pause/resume, remaining time, progress, presets `25 / 5` and `50 / 10`, and a custom duration. |
| FR-FOCUS-003 | The system must record `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, or `SKIP` and store actual execution independently of planned time. |
| FR-REPLAN-001 | The system must re-plan only unfinished flexible future work, retain completed FocusRuns, fixed events, locked fixed-Task PlanBlocks, and the active session as required by BR-008, and briefly explain changes. |

## Goals, reminders, and plant

| ID | Requirement |
|---|---|
| FR-GOAL-001 | The system must create editable Goals with high-level Roadmaps, Milestones, expected outcomes, deadlines, order, status, and overall progress. |
| FR-GOAL-002 | The system must warn about downstream effects when a milestone moves and offer to shift downstream dates equally. |
| FR-REM-001 | The system must create the default day-before 20:00 local-time milestone reminder and support in-app and basic email delivery. |
| FR-REM-002 | The system must support the canonical reminder actions and require confirmation before adding tasks to tomorrow's Daily Plan. |
| FR-PLANT-001 | The system must maintain one active PlantState and render its frontend artwork from backend growth and health state. |
| FR-PLANT-002 | The system must calculate Water Reserve and decay solely from prolonged abandonment without meaningful activity or Rest Mode. |
| FR-PLANT-003 | Rest Mode must pause decay, growth, and wilting. Plant death must preserve user data/history and provide a new seed. |
