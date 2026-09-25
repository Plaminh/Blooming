# Feature Specification: Refactor Today Planning to LLM-First

**Feature Branch**: `[###-refactor-today-planning]`

**Created**: 2026-09-25

**Status**: Draft

**Input**: User description: Refactor Mr. Bloom's new Today planning flow from deterministic-parser-first extraction to LLM-first structured extraction.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Planning (Priority: P1)

As a user planning my day, I want to express my tasks and availability in natural, flexible language (e.g., "I've got four hours this afternoon", "maybe read docs for 20 minutes") so that the system accurately understands my intent without requiring me to use specific keywords or formats.

**Why this priority**: This is the core goal of the refactoring—moving from rigid parsing to robust semantic extraction for the PLAN_DAY intent.

**Independent Test**: Can be fully tested by submitting varied natural language planning requests to the backend and verifying the returned semantic TodayDraft captures the intended tasks and availability correctly.

**Acceptance Scenarios**:

1. **Given** a user inputs "I can work between 1 PM and 5 PM. Read docs for 20 mins if there is time.", **When** the system processes the PLAN_DAY intent, **Then** the LLM extracts an availability window of 13:00-17:00 and an OPTIONAL 20-minute task for reading docs, returning a canonical TodayDraft.
2. **Given** the user submits a planning request, **When** the draft is returned, **Then** `preview` is `null` and no timeline scheduling has occurred yet.

---

### User Story 2 - Fallback to Deterministic Parser (Priority: P2)

As a user, I want the system to gracefully fall back to basic parsing if the AI provider is down or timing out, so that I can still create a basic plan for my day.

**Why this priority**: Reliability is critical; users should not be blocked from planning entirely just because the LLM provider is unavailable.

**Independent Test**: Can be fully tested by simulating an LLM provider timeout/error and verifying the system uses the deterministic parser to generate a basic TodayDraft.

**Acceptance Scenarios**:

1. **Given** the LLM provider is unavailable, **When** the user submits a PLAN_DAY request, **Then** the system catches the error, runs the legacy deterministic parser, and returns a degraded but functional TodayDraft.
2. **Given** the LLM returns completely malformed output that fails validation, **When** the backend processes it, **Then** it falls back to the deterministic parser or explicitly asks for clarification without crashing.

---

### User Story 3 - Preserved Application Authority (Priority: P1)

As the system, I need to ensure the LLM does not dictate critical domain state like task IDs, timelines, or database persistence, so that system invariants, security, and scheduling logic remain deterministic and safe.

**Why this priority**: This enforces the "Code validates, Scheduler decides, User saves" principle, ensuring the AI cannot corrupt the application state.

**Independent Test**: Can be tested via unit/integration tests verifying that LLM outputs containing malicious or hallucinatory IDs, timelines, or database instructions are ignored or rejected by the normalization/validation layers.

**Acceptance Scenarios**:

1. **Given** the LLM attempts to include a timeline or scheduler preview in its structured output, **When** the backend normalizes the data into a TodayDraft, **Then** those fields are ignored, and the returned TodayDraft relies solely on application logic (with `preview = null`).
2. **Given** the LLM attempts to output database task IDs, **When** the backend processes the plan, **Then** it generates and assigns authoritative IDs via deterministic code.

### Edge Cases

- What happens when the LLM extracts durations that violate application bounds (e.g., a 24-hour task)? The deterministic validation layer (code) must reject or cap it.
- How does system handle completely ambiguous input where the LLM cannot safely generate a structured plan? The system should return a clarification request instead of a dangerous/invalid draft.
- What happens if the LLM hallucinated categories or priorities not supported by the schema? The normalization layer discards or maps them to defaults.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST use the planner LLM as the primary path for natural-language extraction when processing the `PLAN_DAY` intent.
- **FR-002**: The system MUST NOT use the deterministic Today parser for the happy path; it MUST be demoted to a degraded fallback for when the LLM/provider fails or returns unparseable output.
- **FR-003**: The LLM MUST return structured planning semantics (e.g., `ParsedPlan`) and MUST NOT return an authoritative `TodayDraft` or scheduled timeline.
- **FR-004**: The application code MUST remain authoritative for assigning task IDs, validating dates/timezones, enforcing duration bounds, managing dependencies, computing totals, generating preview tokens, and executing scheduler behavior.
- **FR-005**: The LLM MAY interpret task titles, implied/explicit durations, Core/Optional status, availability, fixed starts, deadlines, and categories/priorities (where supported).
- **FR-006**: The backend MUST construct and validate the canonical `TodayDraft` deterministically (`assemble_today()`, `check_today()`).
- **FR-007**: The initial `TodayDraft` creation MUST return `preview = null` (no timeline generation during extraction).
- **FR-008**: The system MUST NOT persist any planning-domain entities (DailyPlan, Task, PlanBlock) before the explicit Save action.
- **FR-009**: High-confidence non-planning messages (greeting, help, status) MUST remain deterministic and not invoke the planner LLM.
- **FR-010**: The system MUST NOT alter existing behavior for `EDIT_DRAFT`, Goal/Roadmap generation, the scheduler, `/today/preview`, `/today/save`, frontend Today UI, or database schema.
- **FR-011**: Existing tests enforcing parser-first behavior (e.g., `llm.assert_not_called()`, `tier == "PARSER"`) MUST be updated to assert the new LLM-first behavior without losing coverage.

### Key Entities

- **ParsedPlan**: The structured intermediate representation extracted by the LLM containing task semantics and availability, devoid of authoritative system state.
- **TodayDraft**: The canonical, code-validated draft plan returned to the frontend, ready for explicit user scheduling and saving.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of standard `PLAN_DAY` requests without provider errors use the planner LLM instead of the deterministic parser.
- **SC-002**: Equivalent natural-language paraphrases (e.g., "Maybe read docs", "Read docs if there is time") successfully parse into OPTIONAL tasks without requiring new hardcoded regex rules.
- **SC-003**: 0% of planning-domain entities are persisted to the database before the user explicitly triggers a Save action.
- **SC-004**: All backend automated tests pass, including updated tests validating the LLM-first architecture and deterministic fallback behavior.
- **SC-005**: 100% of LLM-generated timelines, IDs, or database commands (if maliciously prompted) are rejected or ignored by the backend validation layer.

## Assumptions

- The existing `ParsedPlan` or equivalent structured output schema is flexible enough to capture availability and Core/Optional task semantics.
- The LLM provider (Gemini or otherwise configured) is capable of consistent structured JSON extraction for the `PLAN_DAY` intent.
- Frontend components expecting `TodayDraft` with `preview = null` will continue to function exactly as they do today.
