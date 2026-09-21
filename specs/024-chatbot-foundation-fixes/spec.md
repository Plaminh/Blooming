# Feature Specification: Chatbot Foundation Fixes (Phase 0)

**Feature Branch**: `[024-chatbot-foundation-fixes]`

**Created**: 2026-09-20

**Status**: Draft

**Input**: User description: "Implement Phase 0 — Foundation Bug Fixes for the Blooming chatbot..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stable LLM Communications (Priority: P1)

As a user, I want the chatbot to communicate reliably with the Groq AI service and gracefully handle errors so that my app doesn't crash or expose sensitive keys when issues occur.

**Why this priority**: Essential foundation for any chatbot feature; prevents crashes, improves error visibility, and secures credentials.

**Independent Test**: Can be fully tested by triggering timeouts, rate limits, and missing API key errors, observing correct typing of application errors and safe logs.

**Acceptance Scenarios**:

1. **Given** an absent or blank API key, **When** I send a message, **Then** a "config" application error is returned.
2. **Given** a rate-limited Groq response (HTTP 429), **When** I send a message, **Then** a "rate_limit" application error is returned.
3. **Given** a network timeout, **When** I send a message, **Then** a "timeout" application error is returned.
4. **Given** a model response with malformed JSON, **When** parsing fails, **Then** a "bad_output" application error is returned.
5. **Given** an invalid draft with a valid text reply, **When** the draft repair fails once, **Then** the text reply is preserved and returned with a null draft.

---

### User Story 2 - Consistent and Trustworthy UI Behavior (Priority: P2)

As a user, I want the chat interface to behave naturally (auto-scrolling, proper line breaks, correct Enter/Shift+Enter handling) and display accurate dates so that I can interact seamlessly.

**Why this priority**: Directly impacts user experience and trustworthiness of the application.

**Independent Test**: Can be tested manually in the UI by sending messages, using IME input, sending multi-line messages, and verifying date displays.

**Acceptance Scenarios**:

1. **Given** the chat history updates, **When** a new message is added or waiting state changes, **Then** the view auto-scrolls to the bottom after DOM update.
2. **Given** I type a message with line breaks, **When** it renders in the chat bubble, **Then** the line breaks are preserved visually.
3. **Given** I am composing text using a Vietnamese IME (e.g. Telex/VNI), **When** I press Enter to select a word, **Then** the message is not submitted prematurely.
4. **Given** a user message fails to send, **When** I click "Retry", **Then** the exact failed message is resent without duplicating it in the history.
5. **Given** a date-only plan value from the backend, **When** it renders in the UI, **Then** the date is displayed without unintended timezone shifting.

---

### User Story 3 - Robust Domain State Constraints (Priority: P1)

As a system, I need the application backend—not the LLM—to enforce critical domain boundaries like timezones, task IDs, durations, and roadmap validity to guarantee system integrity.

**Why this priority**: Protects the database and backend logic from unpredictable LLM outputs and timezone mismatches.

**Independent Test**: Can be tested via backend unit tests verifying that server-side validation correctly intercepts, corrects, or rejects invalid model drafts.

**Acceptance Scenarios**:

1. **Given** an LLM output omitting timezone, **When** the backend processes the draft, **Then** it injects the timezone from persisted user settings.
2. **Given** an LLM draft with out-of-order or past roadmap milestones, **When** validated, **Then** it applies deterministic, safe corrections (like sorting) or returns a repair issue if unfixable.
3. **Given** a draft time window where end time is before start time, **When** validated, **Then** it rejects it or uses server-side defaults.

### Edge Cases

- What happens when a user spams messages? The per-user, per-process rate limiter (60-second window) rejects excess requests with a HTTP 429 status and user-friendly message.
- How does system handle LLM hallucinating absolute dates? Application code converts relative dates to absolute, overriding any model-provided absolute dates.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use a centralized Groq HTTP client that reads URL, models, timeouts, and rate limits from config.
- **FR-002**: System MUST NOT log API keys, headers, prompts, user messages, or model response content.
- **FR-003**: System MUST map failures (missing key, 429, timeout, bad JSON, upstream) to specific typed application errors.
- **FR-004**: System MUST implement an isolated, per-user, 60-second sliding window rate limiter for the chat endpoint.
- **FR-005**: System MUST separate reply text parsing from draft validation. A valid reply MUST NOT be discarded if the draft is invalid.
- **FR-006**: System MUST allow exactly one repair attempt for an invalid draft before returning the valid reply with an empty draft.
- **FR-007**: System MUST derive timezone and current date/time from server-side user settings and server clock, never trusting client or LLM timezone.
- **FR-008**: System MUST calculate/assign task IDs, milestone IDs, calculated totals, and deterministically validate all time windows (valid HH:MM, end > start, not in past).
- **FR-009**: System MUST validate roadmap (1-12 milestones, target date >= today, milestones ordered and <= target date), applying deterministic safe corrections where possible.
- **FR-010**: System MUST define canonical shared draft models in a dedicated module to resolve circular dependencies between assistant and today preview schemas.
- **FR-011**: System MUST scroll chat to bottom after history/wait state changes (post-DOM update).
- **FR-012**: System MUST preserve newline characters in chat bubbles.
- **FR-013**: System MUST NOT submit messages on Enter if Shift is pressed or if `KeyboardEvent.isComposing` is true.
- **FR-014**: System MUST exclude failed messages from request history and retry must not append duplicate user messages.
- **FR-015**: System MUST dynamically generate the greeting based on actual local time and detected language, removing hard-coded text.
- **FR-016**: System MUST render date-only plan values accurately without applying local timezone shifts.
- **FR-017**: System MUST explicitly disable or properly connect existing "ADD TASK" and "ADD MILESTONE" controls depending on local draft-store support.

### Key Entities

- **ChatResponse**: Contains the separated reply (text) and optional draft (structured data).
- **Draft Schemas**: Canonical representations of suggested tasks, schedules, and roadmaps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All existing and newly introduced Phase 0 tests pass 100% of the time.
- **SC-002**: Log outputs generated during chat operations contain 0 instances of secrets, prompts, or user message content.
- **SC-003**: 100% of users experiencing draft validation failures still receive the text reply rather than a generic application error.
- **SC-004**: Rate limit correctly restricts only the specific authenticated user exceeding the threshold, with 0 false positives for other users.
- **SC-005**: Date-only fields are rendered with 100% accuracy matching the backend value, across any local timezone.

## Assumptions

- We assume no implementation of multi-tier router, planner, editor, mood handler, chitchat system, persistent chat sessions, calibration, proactive notifications, or other later phases.
- We assume the existing database schema and application routing setup will be reused without new database migrations (unless strictly required to fix a Phase 0 defect).
- We assume the centralized HTTP client is cleanly closeable on application shutdown.
