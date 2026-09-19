# Phase 0: Research

**Decision**: Expose `POST /today/preview` using `DeterministicScheduler` without DB interaction.
**Rationale**: Keeps LLM separate from scheduling, validates schedules accurately, and satisfies the "no fake local timeline" requirement while preventing orphaned database records.
**Alternatives considered**: Attempting to mock DB models and rollback transactions on every preview. This is significantly slower and error-prone compared to pure data classes.

**Decision**: Context-aware Chat updates will mutate `ChatRequest` and `ChatResponse`.
**Rationale**: Adding `session_id` and `current_draft` allows the backend to retrieve context securely and the LLM to process typed edit operations.
**Alternatives considered**: Rebuilding the draft entirely in the frontend prompt text. Rejected because it risks state desynchronization and violates the requirement for robust context awareness.

**Decision**: Use `planning_sessions` and `planning_messages` models for conversational memory.
**Rationale**: The tables already exist and enforce correct session ownership.
**Alternatives considered**: Creating a new chat-history table. Rejected to avoid redundant data modeling.
