import os

content = """# Feature Specification: Blooming Multi-Tier Chatbot MVP

**Feature Directory**: `specs/025-blooming-chatbot`
**Created**: 2026-09-20
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stabilized Foundation (Priority: P1)
Users need a stable chat interface that correctly handles timezone differences, multi-line formatting, and gracefully fails on network/provider issues without crashing.

**Why this priority**: Fixes foundational UX bugs before adding complex AI tiers. Corresponds to PR 1-2.
**Independent Test**: Can be tested by invoking basic chat with various timezones and network timeouts, verifying the UI and robust backend fallbacks without triggering advanced planning flows.

**Acceptance Scenarios**:
1. **Given** a message sent by the user, **When** the provider rate-limits the request, **Then** the circuit breaker trips, logs the failure, and returns a graceful degraded response.
2. **Given** a user in UTC+7, **When** rendering dates, **Then** dates remain fixed without UTC shifting issues.

### User Story 2 - Canonical Drafts & Zero-LLM Scheduling (Priority: P2)
Users need to reliably preview, edit, and save their daily schedules using rules and deterministic parsing, even when their AI budget is fully exhausted (RULES_ONLY mode).

**Why this priority**: Ensures the core value proposition (planning) works regardless of LLM availability. Corresponds to PR 3-6.
**Independent Test**: Can be tested by typing "lập lịch 60p học, 30p họp" in RULES_ONLY mode, verifying that a draft is assembled, previewed with the real scheduler, and can be edited and saved without external LLM calls.

**Acceptance Scenarios**:
1. **Given** a structured text input for tasks, **When** processed by the deterministic parser, **Then** tasks are extracted with default durations from the estimates table and mapped to a canonical TodayDraft.
2. **Given** a generated draft, **When** the user manually removes a task via the UI, **Then** a patch is applied to the draft, updating the preview without a full LLM regeneration.

### User Story 3 - Intelligent Planner Cascade & Repair (Priority: P3)
Users provide complex or ambiguous planning requests and receive intelligent scheduling (via LLM cascade) that respects their constraints, repairs itself when overloaded, and asks for clarification if necessary.

**Why this priority**: Enhances the zero-LLM baseline with AI understanding for edge cases. Corresponds to PR 7-9.
**Independent Test**: Can be tested by providing ambiguous tasks with dependencies and observing the cascade fall back to a larger model if the small model fails, ultimately generating a valid draft.

**Acceptance Scenarios**:
1. **Given** a complex request with missing time constraints, **When** processed, **Then** the LLM cascade generates a valid DayPlan and outputs assumptions about the omitted details.
2. **Given** a plan that exceeds the available time window, **When** previewed, **Then** the coach generates a Reality Check showing OVERLOADED and provides quick-reply patches (e.g., dropping optional tasks).

### User Story 4 - Historical Calibration & Proactive Nudges (Priority: P4)
Users benefit from personalized time estimates based on their past task completion durations, and receive gentle, event-driven nudges (e.g., when behind schedule) to replan their day.

**Why this priority**: Delivers advanced retention and personalization mechanics after core planning is solid. Corresponds to PR 13-14.
**Independent Test**: Can be tested by simulating task completions, observing the median duration adjust, and triggering a Pomodoro "NEED_MORE_TIME" event to verify the exact nudge.

**Acceptance Scenarios**:
1. **Given** 5 completed "Work" tasks that took 50% longer than estimated, **When** generating a new "Work" task, **Then** the system applies a 1.5x calibration multiplier to the estimate.
2. **Given** a user is behind schedule, **When** loading the Today view, **Then** they receive an event-driven nudge to replan the day.

## Requirements *(mandatory)*

### Functional Requirements by Area

#### 1. Provider and Budget Behavior (REQ-PROV)
- **REQ-PROV-001**: System MUST route requests to purpose-based models with ordered fallbacks (e.g., `groq:llama-3.1-8b-instant`, `groq:openai/gpt-oss-20b`).
- **REQ-PROV-002**: System MUST use a shared asynchronous HTTP client lifecycle.
- **REQ-PROV-003**: System MUST support `strict: true` for compatible models and `json_object` format with inline schemas for others.
- **REQ-PROV-004**: System MUST implement a circuit-breaker opening upon consecutive failures, applying `retry-after` cooldowns for HTTP 429s.
- **REQ-PROV-005**: System MUST enforce a per-authenticated-user request limit and a global daily call cap according to a rolling 24-hour token budget.
- **REQ-PROV-006**: System MUST dynamically select between `NORMAL`, `LEAN`, and `RULES_ONLY` modes based on budget thresholds (e.g., >=85% used implies RULES_ONLY).
- **REQ-PROV-007**: System MUST log AI usage (tokens, latency, outcome) securely, excluding all chat/message content from the logs.
- **REQ-PROV-008**: System MUST return useful HTTP 200 degraded responses for quota exhaustion rather than throwing 500/503 errors.

#### 2. Assistant Contract and Orchestration (REQ-ORCH)
- **REQ-ORCH-001**: The ChatRequest/ChatResponse contracts MUST manage explicit properties for intent, tier, session, draft, preview, assumptions, and degraded mode.
- **REQ-ORCH-002**: System MUST separate reply parsing from draft validation.
- **REQ-ORCH-003**: System MUST attempt at most one draft repair, and only when the current mode is `NORMAL` and quota allows.
- **REQ-ORCH-004**: System MUST inject trusted server context (timezone, current time, language, quiet hours, plan, calibration) explicitly; the client cannot authoritatively set these.
- **REQ-ORCH-005**: System MUST generate at most one clarification question per response.

#### 3. Deterministic Routing and Handlers (REQ-ROUT)
- **REQ-ROUT-001**: System MUST normalize text deterministically (including Vietnamese diacritics and explicit 'đ' handling) prior to routing.
- **REQ-ROUT-002**: System MUST use weighted rule matching for intent routing (e.g., GREETING, STATUS_*, HELP_*), invoking the LLM only for classification if confidence is low.
- **REQ-ROUT-003**: System MUST resolve STATUS and HELP intents using static bilingual knowledge bases or real application services, without LLM hallucinations.
- **REQ-ROUT-004**: System MUST handle CHITCHAT via a template pool first, invoking a small LLM only if the user remains off-topic below streak limits, terminating with a return-to-planning suggestion.
- **REQ-ROUT-005**: System MUST enforce deterministic precedence for crisis/safety keywords, outputting a fixed supportive response without any diagnosis or planning.

#### 4. Planning and Scheduling (REQ-PLAN)
- **REQ-PLAN-001**: System MUST process `PLAN_DAY` using a deterministic parser grammar to extract durations, dates, priorities, and unresolved segments with confidence scoring.
- **REQ-PLAN-002**: System MUST provide static longest-keyword-first estimates and category mapping for unresolved tasks.
- **REQ-PLAN-003**: System MUST implement a planner cascade: parser (if high confidence) -> small model -> large model -> lenient/manual fallback.
- **REQ-PLAN-004**: System MUST segregate LLM-facing flat schemas from nested domain schemas, assembling canonical drafts server-side with deterministic IDs and constraints.
- **REQ-PLAN-005**: System MUST execute the real `/today/preview` integration for scheduling validation.
- **REQ-PLAN-006**: System MUST generate code-backed Reality Check coaching (COMFORTABLE, TIGHT, OVERLOADED) and repair suggestions (e.g., drop optional tasks).
- **REQ-PLAN-007**: System MUST require explicit user confirmation to replace an existing plan.

#### 5. Goals and Roadmap (REQ-GOAL)
- **REQ-GOAL-001**: System MUST generate a structured RoadmapDraft with 1 to 12 chronologically ordered milestones capped by a target date.
- **REQ-GOAL-002**: System MUST fallback to generating a deterministic, equally-spaced timeline if LLM generation fails or budget is exhausted.
- **REQ-GOAL-003**: System MUST persist goals and milestones atomically; if any milestone fails insertion, the entire goal creation must roll back.
- **REQ-GOAL-004**: System MUST automatically sync milestone reminders upon atomic goal creation.

#### 6. Editing and Actions (REQ-EDIT)
- **REQ-EDIT-001**: System MUST apply state modifications exclusively via a validated patch-operation allowlist without mutating the source draft directly.
- **REQ-EDIT-002**: System MUST evaluate deterministic editor rules before invoking the LLM editor, matching tasks by ordinal or fuzzy title.
- **REQ-EDIT-003**: The LLM editor MUST output patch structures rather than returning full regenerated drafts.
- **REQ-EDIT-004**: System MUST support whitelisted mood actions (e.g., `SKIP_OPTIONAL_TODAY`) that execute only via explicit user interaction, never automatically by the LLM.

#### 7. Persistence (REQ-PERS)
- **REQ-PERS-001**: System MUST isolate and authenticate all database accesses to the authenticated user.
- **REQ-PERS-002**: System MUST commit the user's message to `PlanningSession` immediately, rather than waiting for LLM resolution.
- **REQ-PERS-003**: System MUST manage recent chat history authoritatively on the server; client-provided history arrays must be ignored.
- **REQ-PERS-004**: System MUST complete a session only after a successful save action.

#### 8. Learning and Proactive Behavior (REQ-LEARN)
- **REQ-LEARN-001**: System MUST calibrate future duration estimates based purely on eligible, completed, AI-sourced tasks combined with their associated focus run durations.
- **REQ-LEARN-002**: System MUST NOT calibrate estimates explicitly provided by the user.
- **REQ-LEARN-003**: System MUST issue proactive nudges strictly via event-driven mechanisms (e.g., missing deadline, Pomodoro triggers) enforcing cooldowns and quiet hours, avoiding LLM polling.

#### 9. Frontend Behavior (REQ-FRONT)
- **REQ-FRONT-001**: Client MUST use canonical API types, abolishing duplicated local draft schemas.
- **REQ-FRONT-002**: Client MUST replace fake timeline calculations with the real `/today/preview` state, resolving overlapping UI logic.
- **REQ-FRONT-003**: Client MUST handle keyboard inputs safely (IME-safe Enter, Shift+Enter) and prevent form submission spam.
- **REQ-FRONT-004**: Client MUST gracefully render "Failed" message states with a retry button to avoid duplicating outgoing history.
- **REQ-FRONT-005**: Client MUST render degraded mode banners, quick replies, and explicit Reality Check blocks.

#### 10. Security and Privacy (REQ-SEC)
- **REQ-SEC-001**: All provider credentials MUST remain strictly backend-only.
- **REQ-SEC-002**: `.env.example` MUST contain ONLY placeholders, no functional keys.
- **REQ-SEC-003**: Database queries MUST be scoped to the authenticated user.
- **REQ-SEC-004**: Logging infrastructure MUST actively strip prompt content, message replies, and raw model outputs.
- **REQ-SEC-005**: Destructive actions (e.g., replacing plans) MUST require explicit API validation and user intent.

### Key Entities
- **PlanningSession**: Represents a discrete conversational boundary (OPEN, AWAITING_CLARIFICATION, COMPLETED, CANCELLED).
- **AiUsageLog**: Tracks token utilization, model names, latency, and outcome without recording PII or conversation content.
- **TodayDraft / RoadmapDraft**: Canonical data structures defining the state of uncommitted plans.
- **ChatResponse / ChatRequest**: Ephemeral structured data bounding all client-server communications.

## Traceability Matrix

| Phase / PR | Associated Requirements | Included in MVP |
|------------|-------------------------|-----------------|
| PR 1 (Provider layer & Config) | REQ-PROV-001 to 005, REQ-SEC-001 to 004 | Yes |
| PR 2 (Frontend minor fixes) | REQ-FRONT-003, REQ-FRONT-004 | Yes |
| PR 3 (Canonical schemas) | REQ-ORCH-001, REQ-PLAN-004, REQ-FRONT-001 | Yes |
| PR 4 (Router & Rules) | REQ-ROUT-001 to 005 | Yes |
| PR 5 (Parser & Cascade) | REQ-PLAN-001 to 003, REQ-PLAN-005 to 006 | Yes |
| PR 6 (Frontend Save/Preview) | REQ-FRONT-002, REQ-PLAN-007 | Yes |
| PR 7 (Planner LLM & Repair) | REQ-ORCH-002 to 003, REQ-ORCH-005 | Yes |
| PR 8 (Budget Guard & Degradation) | REQ-PROV-006 to 008, REQ-FRONT-005 | Yes |
| PR 9 (Clarify & Roadmap) | REQ-GOAL-001 to 004 | Yes |
| PR 10 (Editor & Patches) | REQ-EDIT-001 to 003 | Yes |
| PR 11 (Persistence) | REQ-PERS-001 to 004 | Yes |
| PR 12 (Mood & Actions) | REQ-EDIT-004 | Yes |
| PR 13 (Calibration) | REQ-LEARN-001 to 002 | Yes |
| PR 14 (Proactive Nudges) | REQ-LEARN-003 | Yes |
| Section 14 (BYOK) | N/A | **DEFERRED** |

## Testing Requirements

- **Provider Routing & Resilience**: Tests MUST mock the provider boundary. Test 429 Retry-After, fallback cascades, circuit breakers, and behavior under invalid JSON output.
- **Router Coverage**: At least 50 bilingual test cases matching Vietnamese normalization, mood flags, and intent routing.
- **Parser Coverage**: At least 40 cases testing deterministic extraction of durations, ambiguous times, dependencies, and formatting variations.
- **Rules Execution**: Full coverage of real service-backed responses (e.g., STATUS_TODAY triggering actual DB queries) without mock hallucination.
- **Budget Simulation**: Test 24-hour rolling quotas, per-user isolation, threshold degradation (LEAN/RULES_ONLY), and privacy compliance in usage logs.
- **Evaluation Tooling**: Create a manual `scripts/eval_chat.py` script defaulting to `ollama` for LLM quality evaluation, requiring explicit opt-in for `groq` execution.
- **Constraint**: No acceptance criterion may depend solely on calling a live external LLM model.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: The system processes 100% of trivial planning requests (via `RULES_ONLY`/Parser mode) without consuming any external LLM tokens.
- **SC-002**: Model failover (HTTP 429 or 503) succeeds in <1.5s latency overhead without bubbling 500 errors to the user.
- **SC-003**: The backend correctly calculates token utilization, restricting high-usage paths when global rolling thresholds hit 85% capacity.
- **SC-004**: Users successfully preview and save daily drafts without any client-side timezone shifting bugs.
- **SC-005**: 100% of AI requests log latency, model, and token usage into `ai_usage_log` while containing exactly 0 bytes of raw conversational content.

## Assumptions
- Target environments are either localized offline setups (Ollama) or constrained cloud setups (Groq free tier) meaning latency/rate-limit mitigations are strictly required.
- `BYOK` (Bring Your Own Key) functionality is out of scope for the MVP and deferred to future planning phases.
- Front-end integration assumes SvelteKit components mapped via canonical OpenAPI models.
- Existing authentication and user session lifecycles are assumed stable and will be reused to scope database queries.
"""

with open(r"E:\Blooming\specs\025-blooming-chatbot\spec.md", "w", encoding="utf-8") as f:
    f.write(content)
