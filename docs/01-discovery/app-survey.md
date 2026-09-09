# Existing App Survey

## 1. Objectives and selection

This survey examines products that represent four parts of Blooming's intended loop: automatic scheduling, deliberate daily planning, visual timelines with AI input, and focus gamification. The review informs Blooming's MVP boundary and interaction principles; it is not a claim that the products are feature-identical.

| Product | Category | Why selected | Evidence date |
|---|---|---|---|
| Motion | AI calendar and task scheduler | Strong reference for automatic prioritization and dynamic scheduling | 8 September 2026 |
| Sunsama | Guided daily planner | Strong reference for realistic workload review and deliberate timeboxing | 8 September 2026 |
| Structured | Visual timeline and AI planner | Close reference for timeline clarity, editable AI-created tasks, and re-planning | 8 September 2026 |
| Forest | Gamified focus timer | Strong reference for immediate visual reward and gentle focus accountability | 8 September 2026 |

## 2. Product analysis

### Motion

#### Features and workflow

- Prioritizes tasks and places them into calendar time blocks.
- Uses deadlines, priorities, and availability when auto-scheduling.
- Dynamically changes the schedule when the day changes.
- Includes project and meeting capabilities beyond Blooming's personal MVP.

#### Strengths and weaknesses

- Strength: automation reduces repeated calendar maintenance.
- Weakness for Blooming's target: a highly automated experience can make the scheduling rationale and overload trade-offs less visible.
- Lesson for Blooming: adopt automatic recovery, but show feasibility, unscheduled work, and the reason for meaningful changes.

### Sunsama

#### Features and workflow

- Guides the user through a daily planning ritual.
- Brings tasks into a daily list and timeboxes them on a calendar.
- Encourages the user to plan less than the theoretical workday capacity.
- Supports auto-scheduling and auto-rescheduling while retaining deliberate user review.

#### Strengths and weaknesses

- Strength: calm, intentional planning and workload awareness match Blooming's philosophy.
- Weakness for Blooming's target: the workflow centers on existing task and calendar systems rather than conversational capture and a single personal loop.
- Lesson for Blooming: adopt a review-before-commit step and an explicit daily capacity check.

### Structured

#### Features and workflow

- Combines tasks, calendar events, and focus sessions in one visual timeline.
- Structured AI can create tasks from written or spoken instructions and can consider existing events.
- AI-created tasks can be edited before they are added to the timeline.
- Current product documentation lists re-planning on selected platforms and distinguishes free from Pro features.

#### Strengths and weaknesses

- Strength: the timeline gives a clear answer to “what happens next?” and retains user editability.
- Weakness for Blooming's target: documented feature availability varies by platform, and the evidence reviewed does not expose a deterministic capacity model.
- Lesson for Blooming: use a simple timeline and editable AI output, but make workload classification and scheduler invariants explicit.

### Forest

#### Features and workflow

- Runs countdown or stopwatch focus sessions.
- Grows a virtual tree while the user focuses and adds completed trees to a persistent forest.
- Uses immediate visual feedback and optional distraction controls.
- Provides focus history and progression beyond a plain timer.

#### Strengths and weaknesses

- Strength: progress becomes emotionally visible without requiring complex game mechanics.
- Weakness for Blooming's target: focus is largely separate from planning feasibility and re-planning.
- Lesson for Blooming: reward completed execution, not merely task creation; keep the first garden state simple and avoid punitive loss of earned progress.

## 3. Comparison matrix

| Capability | Blooming target | Motion | Sunsama | Structured | Forest | Finding |
|---|---|---|---|---|---|---|
| Natural-language planning | Convert intent to validated structured input | Partial | No primary conversational flow found | Yes | No | Conversation is useful only if the user can review and correct the result. |
| Automatic scheduling | Deterministic sessions inside explicit constraints | Yes | Yes/assisted | Partial | No | Blooming should automate time placement while exposing the rules and result. |
| Overload handling | Quantified capacity plus unscheduled tasks | At-risk deadline signals | Explicit workload guidance | No equivalent capacity evidence found | No | Transparent overload is a central differentiation. |
| Editing and re-planning | Manual edits plus history-preserving re-plan | Yes | Yes | Yes on supported features/platforms | No | Blooming must treat user control as part of correctness. |
| Focus execution | Timer linked to planned session and actual outcome | Not central in reviewed evidence | Tracks work/time | Focus sessions included | Core feature | Link the plan directly to actual execution. |
| Plant continuity | One active plant, meaningful-activity growth, Water Reserve, and non-punitive recovery | No | No | No core garden loop | Core tree/forest loop | Use a single integrated plant, not a forest or pet economy. |

## 4. Conclusions for Blooming

- Patterns to adopt: Motion's automatic recovery, Sunsama's deliberate capacity review, Structured's visual editable timeline, and Forest's immediate visible reward.
- Patterns to avoid: hiding overload, making the LLM the source of schedule truth, over-automating without explanation, and building a large reward economy before the planning loop works.
- Market gap pursued by Blooming: one personal loop that combines conversational capture, explicit overload detection, deterministic scheduling, focus execution, and history-preserving re-planning.
- Differentiation: Blooming separates semantic interpretation from scheduling correctness and explains what could not fit instead of silently producing an impossible plan.
- MVP decision: prioritize scheduling correctness and the daily loop first while retaining minimal long-term goals/reminders and one non-punitive plant system; defer integrations and advanced gamification.

## Sources

- [Motion product overview](https://www.usemotion.com/) — accessed 8 September 2026.
- [Motion auto-scheduling help](https://www.usemotion.com/help/time-management/auto-scheduling) — accessed 8 September 2026.
- [Sunsama product overview](https://www.sunsama.com/) — accessed 8 September 2026.
- [Sunsama daily planning guide](https://help.sunsama.com/docs/usage-guides/daily-planning/) — accessed 8 September 2026.
- [Sunsama timeboxing guide](https://help.sunsama.com/docs/usage-guides/timeboxing/) — accessed 8 September 2026.
- [Structured product overview](https://structured.app/) — accessed 8 September 2026.
- [Structured AI task creation](https://help.structured.app/en/articles/331074) — accessed 8 September 2026.
- [Structured free and Pro feature matrix](https://help.structured.app/en/articles/1897986) — accessed 8 September 2026.
- [Forest product overview](https://forestapp.cc/) — accessed 8 September 2026.

## Limitations

This first survey is based on official product and help documentation rather than extended hands-on testing. Pricing was intentionally excluded because it changes frequently and does not affect the current MVP architecture.
