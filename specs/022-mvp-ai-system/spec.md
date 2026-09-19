# Feature Specification: Blooming MVP AI System

**Feature Branch**: `[022-mvp-ai-system]`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "Create a new SpecKit specification for the **Blooming MVP AI system**..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic Rule Parsing (Priority: P1)

As a user, I want simple, clear commands (like explicitly formatted task drafts) to be handled quickly and deterministically so that I don't experience AI latency or unreliability for basic actions.

**Why this priority**: Essential for maintaining a fast, reliable desktop application experience where AI does not block deterministic operations.

**Independent Test**: Can be tested by providing explicit structured inputs (e.g., "task: Clean desk, 25m") and verifying the system handles it without invoking external LLMs.

**Acceptance Scenarios**:

1. **Given** the user inputs a clearly structured deterministic command, **When** the input is parsed, **Then** the Rule-based layer resolves it successfully without invoking Groq or Gemini.
2. **Given** the user inputs ambiguous text, **When** the input is parsed, **Then** the Rule-based layer explicitly fails and delegates to the AI Router.

---

### User Story 2 - Primary AI Routing via Groq (Priority: P1)

As a user, I want my ambiguous scheduling and planning requests interpreted by a fast AI so that I get accurate task and roadmap drafts.

**Why this priority**: Core AI functionality of the MVP; Groq is defined as the primary provider for intent and draft generation.

**Independent Test**: Can be tested by providing ambiguous input that bypasses rules, verifying the request routes to Groq, and returns structured data passing schema validation.

**Acceptance Scenarios**:

1. **Given** ambiguous user input, **When** routed to Groq, **Then** Groq returns a structured output that passes schema and business validation.
2. **Given** an invalid schema response from Groq, **When** validated, **Then** it fails validation and triggers the fallback mechanism.

---

### User Story 3 - Gemini Fallback (Priority: P2)

As a user, I want the system to seamlessly retry my request with a fallback AI provider if the primary provider fails, so that I am not blocked by temporary outages.

**Why this priority**: Ensures reliability and handles primary provider downtime or complex requests Groq fails to parse.

**Independent Test**: Can be tested by mocking a Groq failure (timeout or invalid schema) and verifying the system automatically routes the request to Gemini and successfully returns a validated response.

**Acceptance Scenarios**:

1. **Given** Groq times out or returns a 500 error, **When** the AI Router catches the failure, **Then** the request is sent to Gemini.
2. **Given** both Groq and Gemini fail, **When** the AI Router exhausts fallbacks, **Then** a user-friendly error message is displayed and the system returns to its stable prior state.

---

### User Story 4 - AI Output Safety Boundary (Priority: P1)

As a user, I want the AI to only propose changes rather than directly modifying my database, so that my existing schedule and garden state remain safe from hallucinations.

**Why this priority**: Critical to the principle that AI interprets and deterministic code decides.

**Independent Test**: Can be tested by verifying that AI responses are strictly routed through schema and business validations and never directly invoke persistence layers.

**Acceptance Scenarios**:

1. **Given** a validated AI task draft, **When** the draft implies application state changes, **Then** it is presented to the user for confirmation before persistence.
2. **Given** the AI proposes values that violate Blooming business rules (e.g., invalid duration or dates), **When** validated, **Then** the request is rejected or sanitized without modifying the database.

---

### Edge Cases

- What happens when the same request is retried after a failure? The system uses Cloudflare AI Gateway infrastructure to manage identical retry attempts and network level features.
- How does the system handle rate limits from providers? The Cloudflare AI gateway logs the 429 and triggers the fallback or alerts the user gracefully if all fallbacks are exhausted.
- What happens when AI output includes unsupported fields? The Pydantic/schema validation strips or rejects them before they reach the business logic (`extra="forbid"` enforced).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST implement a Rule-based parsing layer that intercepts structured/deterministic input prior to any AI routing.
- **FR-002**: The system MUST implement an AI Router that delegates unresolved input to the Cloudflare AI Gateway.
- **FR-003**: The system MUST use Groq as the primary LLM provider for intent classification and draft generation.
- **FR-004**: The system MUST use Gemini as the fallback LLM provider if Groq fails, times out, or returns invalid schemas.
- **FR-005**: All AI output MUST be processed through strict Pydantic/schema validation before any further action.
- **FR-006**: All schema-validated AI output MUST be processed by deterministic business-rule validation before reaching the persistence layer.
- **FR-007**: The system MUST require user confirmation for any AI-generated drafts (e.g., task creation, roadmap generation) that materially change planning state.
- **FR-008**: The AI layer MUST NOT directly own or mutate scheduling decisions, Pomodoro state, reminders, task completion, rewards, or database state.
- **FR-009**: The system MUST NOT expose local-AI (Ollama) settings or require local model inference. Offline mode strictly means AI interpretation is disabled.
- **FR-010**: The system MUST track observability (route, provider success/failure, latency, validation failure, fallback) without logging sensitive user content.
- **FR-011**: The system MUST explicitly track provenance of inferred values (e.g. USER, EXTRACTED, AI_ESTIMATE, DEFAULT) to transparently show how the AI arrived at the data.
- **FR-012**: Genuine missing information must trigger a `NEEDS_CLARIFICATION` state rather than endlessly triggering fallbacks or hallucinating defaults.

### Deferred / Future Work / Out of feature 022

- **Explanation Capability**: Producing read-only, human-readable explanations of complex deterministic scheduling results is deferred and not part of MVP feature 022.

### Key Entities

- **AI Request Context**: The payload sent to the router, containing the user input and necessary context (without sensitive PII if possible).
- **Draft Proposal**: The standardized, schema-validated output from the AI (e.g., TaskDraft, RoadmapDraft) ready for user review.
- **Validation Result**: The object detailing whether the AI output passed schema and business rule checks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of defined deterministic commands (e.g. `task: <title>, <N>m`) bypass the AI layer entirely.
- **SC-002**: AI provider failures correctly trigger the Gemini fallback seamlessly, while the deterministic RuleParser processes requests in < 50ms.
- **SC-003**: 0% of AI-generated responses bypass the validation layer or directly modify the database.
- **SC-004**: Routing telemetry captures provider success/failure rates and fallback occurrences effectively.

## Assumptions

- Cloudflare AI Gateway is configured properly to route to Groq and Gemini.
- The UI layer already exists to present Draft Proposals (e.g., Today Draft, Roadmap Draft) for user confirmation.
- The desktop app environment is always connected to the internet for AI features; offline mode strictly defaults to the rule-based layer.
- Mr. Bloom UI will not be heavily modified, maintaining its role as a guide rather than a free-form chatbot.
