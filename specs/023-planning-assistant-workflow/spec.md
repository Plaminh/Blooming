# Feature Specification: Planning Assistant Workflow

**Feature Branch**: `023-planning-assistant-workflow`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: Build a production-ready “Mr. Bloom Planning Assistant” workflow by fixing the current disconnect between the planning chatbot, scheduler, persistence layer, and frontend previews.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preview and Save Today Plan via Backend Scheduler (Priority: P1)

Users need to see accurate, deterministically scheduled timeline previews based on their natural language input, and successfully save those plans to the database atomically.

**Why this priority**: Without this, the assistant provides fake local timelines, leading to a broken and misleading user experience where the UI claims schedules are saved when they are not.

**Independent Test**: Can be fully tested by generating a timeline preview using the assistant, verifying that the backend scheduler logic is applied instead of frontend fake logic, and confirming that "Save to Today" results in a persisted plan in the database.

**Acceptance Scenarios**:

1. **Given** a generated Today draft, **When** the user selects "GENERATE TIMELINE", **Then** the draft is validated and normalized by the backend, run through the real scheduler, and the frontend renders the returned blocks and reality check without recomputing.
2. **Given** a previewed timeline, **When** the user selects "SAVE TO TODAY", **Then** the tasks and daily plan are persisted in one atomic database transaction, and a success message is shown only after server confirmation.

---

### User Story 2 - Context-Aware Chat and Deterministic Validation (Priority: P1)

Users should be able to edit their planning drafts conversationally and reliably, while ensuring all output from the assistant strictly adheres to validation rules before it reaches the frontend.

**Why this priority**: Users expect the assistant to understand manual edits and their current timezone context without breaking application constraints.

**Independent Test**: Can be fully tested by asking the assistant to make a modification to an existing draft ("Change the second task to 45 minutes") and ensuring the update applies correctly and passes backend schema validation.

**Acceptance Scenarios**:

1. **Given** an existing draft with manual frontend edits, **When** the user sends a new message to the assistant, **Then** the request includes the current draft context and session ID, and the assistant accurately targets modifications.
2. **Given** an assistant response with invalid time format or negative duration, **When** the backend receives the LLM output, **Then** it automatically repairs or retries the response, returning a controlled error if it still fails to validate.

---

### User Story 3 - Persistence of Planning Sessions (Priority: P2)

Users should be able to reload the application without losing their current planning conversation and drafts, maintaining a secure link between sessions and the final saved plans.

**Why this priority**: Preserves user work and provides an authoritative backend record of planning conversations.

**Independent Test**: Can be fully tested by starting a chat session, refreshing the browser, and seeing the conversation history and draft accurately restored from the database.

**Acceptance Scenarios**:

1. **Given** an active chat, **When** the user refreshes the page, **Then** the session and latest valid draft are restored from the backend, and history is accurately populated without cross-user leakage.
2. **Given** a completed daily plan creation, **When** the plan is saved, **Then** it is explicitly linked to the corresponding `PlanningSession` record in the database.

---

### User Story 4 - Atomic Roadmap Creation and Reliability (Priority: P2)

Users should confidently create long-term roadmaps without risking partial data creation when an error occurs during milestone processing.

**Why this priority**: Fixes current reliability issues in roadmap generation, ensuring data integrity for goals.

**Independent Test**: Can be fully tested by initiating a roadmap save that triggers a milestone validation error and verifying that no orphaned goal is left in the database.

**Acceptance Scenarios**:

1. **Given** a validated Roadmap draft, **When** the user saves it and a milestone fails validation, **Then** the entire transaction rolls back, leaving no partially created goal.
2. **Given** a Roadmap draft with date values, **When** the payload is processed, **Then** dates are preserved purely as `YYYY-MM-DD` strings without local timezone mutation errors.

---

### User Story 5 - Provider Reliability and Scope Protection (Priority: P3)

The assistant should handle rate limits gracefully and refuse to answer requests outside of its designated productivity scope.

**Why this priority**: Hardens the system against provider outages and prevents misuse of the LLM for general chatbot queries.

**Independent Test**: Can be fully tested by asking the assistant a general knowledge question (e.g., "Write a poem") and verifying that it politely declines and guides the user back to planning.

**Acceptance Scenarios**:

1. **Given** a transient 5xx error or 429 from the LLM provider, **When** the backend calls the provider, **Then** it applies bounded retry with exponential backoff.
2. **Given** an off-topic user prompt, **When** the assistant responds, **Then** it returns an `out_of_scope` intent and politely refuses to answer.

---

### User Story 6 - Improved UX and Accessibility (Priority: P3)

Users should have a seamless, accessible chat interface that correctly handles loading states, keyboard interactions, and visual cues.

**Why this priority**: Eliminates rough edges like double-submissions and poor accessibility, improving the overall professional feel of the product.

**Independent Test**: Can be fully tested using keyboard navigation and screen readers to generate and save a plan.

**Acceptance Scenarios**:

1. **Given** the user is typing an IME composition, **When** they press Enter, **Then** the message is not prematurely sent.
2. **Given** a pending API request, **When** the user interacts with the UI, **Then** the save/generate actions are disabled and the user cannot duplicate the submission.

## Functional Requirements *(mandatory)*

- The backend must provide an endpoint to preview a Today draft using the existing deterministic scheduler without persisting records to the database.
- The backend must provide an endpoint to atomically persist a validated Today draft and its tasks to the database in a single transaction.
- The backend must supply the LLM with the current date, time, and user timezone context for relative date resolution.
- The backend must validate all LLM output strictly (e.g., positive durations, valid `HH:MM` times, no cyclic dependencies) and apply one automatic retry upon validation failure.
- The backend must store and restore planning sessions and conversation messages securely, ensuring users can only access their own sessions.
- The frontend must send the current manual draft edits and session ID to the backend when sending chat messages.
- The frontend must render timeline previews using the exact structure returned by the backend without local recalculations or hardcoded break blocks.
- The backend must atomically persist Roadmaps (Goals and Milestones).
- The system must include a scope guard to prevent the LLM from answering off-topic queries.
- The frontend chat interface must use an appropriate `aria-live` region, disable buttons during API requests, prevent Enter from sending during IME composition, and support Shift+Enter for newlines.
- A small bilingual (English/Vietnamese) evaluation dataset must be created to verify intent and output generation.

## Assumptions *(optional)*

- The existing deterministic scheduling logic in `app.core.scheduler` (or equivalent service) can be decoupled from database operations to support the preview requirement.
- The current database schema for `PlanningSession` and `PlanningMessage` is sufficient and requires minimal or no new migrations.
- Structured JSON output is supported by the primary LLM provider (Groq).

## Success Criteria *(mandatory)*

- 100% of generated timelines rendered in the UI match the deterministic output of the backend scheduler.
- 0% of failed "Save to Today" attempts result in a false success message on the frontend.
- Users can successfully refresh the page during an active planning session and recover their conversation history and draft state.
- 100% of roadmap saves are strictly atomic (either all goals and milestones are saved, or none are).
- The system gracefully recovers from transient LLM provider failures without exposing stack traces or raw API errors to the client.

## Key Entities *(optional)*

- `PlanningSession`: The conversation context and link to the final saved plan.
- `PlanningMessage`: The individual chat messages (user, assistant, system) stored within a session.
- `TodayDraft` / `RoadmapDraft`: The structured payload representing the intended plan before persistence.
- `DailyPlan`: The persisted day plan generated from the draft.
- `Goal` and `Milestone`: The persisted roadmap entities.
