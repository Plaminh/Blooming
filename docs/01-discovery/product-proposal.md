# Product Proposal: Blooming

## 1. Executive summary

Blooming is a personal planning application for people who regularly create more work than can fit into their day. It converts tasks, fixed events, time constraints, and preferences into a realistic timeline. It then supports execution through focus sessions and adapts the unfinished plan when reality changes.

The product uses AI where language understanding is valuable, but it does not allow an LLM to determine schedule correctness. Natural-language input is converted into structured data, validated, and passed to a deterministic scheduling engine. This boundary makes the result explainable, repeatable, and testable.

The first release is a solo portfolio project. It delivers one constrained loop: daily planning and recovery first, connected to long-term milestones, reminders, and one living plant without becoming a project-management system or pet game. Mr. Bloom, an old AI robot, is the central conversational guide: mature, calm, practical, concise, assertive about unrealistic plans, supportive without excessive enthusiasm, and non-judgmental after disruption.

## 2. Problem and value

| Element | Statement |
|---|---|
| Problem | Task lists do not show whether the planned workload fits the user's actual available time. |
| Affected users | Students and individual knowledge workers who plan busy days and frequently need to adjust them. |
| Current impact | Over-planning creates stress, missed tasks, repeated manual rescheduling, and loss of trust in planning tools. |
| Successful outcome | The user receives a feasible, editable schedule, understands any overload, focuses on the next session, and can recover after disruption. |

## 3. Target users and environment

- Primary user: an individual student or knowledge worker managing personal work and study.
- Devices/platforms: responsive web application, initially optimized for a modern desktop browser and usable on mobile web.
- Usage context: daily planning before work, quick checks between sessions, and re-planning after interruptions.
- Constraints: limited attention, incomplete task estimates, changing availability, and possible concern about sending personal text to an AI provider.

## 4. Proposed solution

The user enters or describes the tasks they want to complete, the time available, and fixed events. Blooming validates the request, calculates total workload including breaks and buffer, classifies feasibility, and generates a non-overlapping timeline. The user may resolve overload or edit the result before saving it.

During execution, Blooming presents the current session and a focus timer. The user records `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, or `SKIP`. Blooming then re-plans only the unfinished portion of the day while preserving completed history and fixed events.

## 5. Key functional groups

| Functional group | What it does | User value |
|---|---|---|
| Quick planning | Converts structured tasks and time constraints into sessions | Replaces manual time-blocking |
| Reality check | Calculates capacity and exposes overload | Prevents impossible plans |
| Plan review and editing | Lets the user accept or change the timeline | Preserves user control |
| Mr. Bloom Assistant | Extracts tasks and goals, asks material clarifications, drafts plans/roadmaps, explains trade-offs, and guides recovery | Reduces input friction while preserving user control |
| Focus execution | Runs recoverable focus sessions and records outcomes | Connects planning with action |
| Adaptive re-planning | Reschedules only remaining work | Makes the plan resilient |
| Goals and reminders | Connects editable milestones to future Daily Plans | Gives long-term intent a practical next step |
| Plant continuity | Uses one active plant and Water Reserve to reflect meaningful activity | Makes recovery visible without punishment |

## 6. AI-powered capability

- Input: the user's natural-language description of tasks, timing, constraints, and preferences.
- Output: a structured planning request plus explicit clarification questions when required fields are missing.
- User value: faster task capture without surrendering control over the result.
- Deterministic control: backend schema validation rejects or repairs invalid AI output; the scheduling engine, not the LLM, creates the timeline.
- Fallback: the user can enter or edit the same information through a normal form.

## 7. Initial scope

### Included

- Structured daily planning request.
- Available window and fixed events.
- Workload and overload classification.
- Deterministic scheduling with breaks and task splitting.
- Basic timeline review and editing.
- Plan persistence.
- Natural-language interpretation with validation and fallback.
- Focus timer and execution outcomes.
- Adaptive re-planning.
- JWT authentication, basic profile, timezone, focus/break defaults, reminder settings, and Rest Mode.
- Long-term goals, editable roadmaps and milestones, in-app and basic email reminders.
- One active plant with growth/health state and Water Reserve.
- Deployment of a usable web MVP.

Plant deterioration represents prolonged abandonment without meaningful activity or Rest Mode; an individual missed task or delayed milestone does not directly damage the plant.

### Excluded

- Team collaboration and social features.
- Full calendar replacement or calendar integration.
- Complex web push notification behavior.
- Voice input, analytics, advanced personalization, and autonomous agents.
- Medical or mental-health advice.
- Multiple plants, inventory, shop, currency, gacha, pet-care simulation, world map, quests, or robot customization.

## 8. Feasibility and risks

| Area/risk | Assessment | Response |
|---|---|---|
| Deterministic scheduler complexity | Amber | Start with explicit rules, pure domain logic, and boundary tests; reduce heuristics before sacrificing correctness. |
| LLM output reliability | Amber | Use structured output, backend validation, clarification, and manual fallback. |
| Increment size | Amber | Split work into independently testable outcomes and keep WIP at one. |
| Scope growth | Red | Keep retained goals/reminders and plant behavior at the documented minimal depth; exclude integrations and game systems. |
| API and hosting cost | Amber | Minimize prompts, cap requests, observe usage, and preserve a non-AI input path. |
| Solo development capacity | Amber | Use a modular monolith, reuse one canonical document per concern, and defer non-critical polish. |
| Core web stack | Green | Next.js, Spring Boot, PostgreSQL, and Docker are suitable for the intended scale. |

## 9. Delivery sequence

| Increment | Deliverable |
|---|---|
| Scheduler A | Domain model, validation, interval normalization, feasibility, and dependency-aware ordering |
| Scheduler B | Placement, splitting, breaks, unscheduled reasons, invariant verification, repeatability, and performance evidence |
| Daily planning loop | Preview UI/API, persistence, overload resolution, and validated editing |
| Conversational and execution loop | Mr. Bloom input, FocusRun execution, and adaptive re-planning |
| Connected MVP | Goals/reminders, plant/Rest Mode, deployment, and full regression |

No calendar completion dates are claimed until implementation capacity is known.

## 10. Decision

**Proceed.** The core value can be demonstrated through a constrained vertical slice, the main technical risks can be isolated and tested, and the product provides strong portfolio evidence across requirements, backend domain logic, AI integration, testing, and deployment.
