<!--
Sync Impact Report:
- Version change: none -> 1.0.0
- Modified principles:
  - N/A (New Constitution)
- Added sections:
  - 1. Spec-driven development
  - 2. Planning correctness and deterministic ownership
  - 3. Clear architectural boundaries
  - 4. Type safety and explicit contracts
  - 5. Simple, maintainable implementation
  - 6. Testable behavior and quality gates
  - 7. Recoverable and accessible user experience
  - 8. Resource efficiency and platform scope
  - 9. Security and privacy
  - 10. Controlled scope and change management
- Removed sections: N/A
- Templates requiring updates (⚠ pending / ✅ updated):
  - .specify/templates/plan-template.md (✅ updated)
  - .specify/templates/spec-template.md (✅ checked, no update needed)
  - .specify/templates/tasks-template.md (✅ updated)
- Follow-up TODOs: none
-->
# Blooming Constitution

## Core Principles

### 1. Spec-driven development
- Every substantial feature must follow Specify → Clarify → Plan → Tasks → Analyze → Implement → Verify against the specification, plan, tasks, and acceptance scenarios.
- Implementation must remain traceable to user stories and acceptance scenarios.
- Product requirements must not be invented during implementation.
- Small bug fixes may use a lighter workflow only when they do not change product behavior or architecture.

### 2. Planning correctness and deterministic ownership
- Blooming’s primary purpose is realistic daily planning and recovery.
- AI may interpret natural language, ask clarification, suggest, and explain.
- AI output is untrusted and must be schema-validated.
- Deterministic application code owns scheduling, conflicts, timestamps, reminders, focus state, rewards, persistence, and authorization.
- The UI must never invent authoritative domain state. Explicit development fixtures and non-production mock flows are permitted when isolated from production integrations, clearly identified as examples, and incapable of being mistaken for persisted authoritative data.

### 3. Clear architectural boundaries
- Desktop shell: Tauri 2 and Rust.
- Desktop UI: SvelteKit, TypeScript, and Vite.
- Backend: FastAPI, Python, and Pydantic.
- Persistence: PostgreSQL and SQLAlchemy.
- The backend remains a modular monolith unless evidence justifies another architecture.
- The main application and desktop widget are separate presentation surfaces with shared typed concepts.
- Frontend feature modules must not directly own backend business rules.

### 4. Type safety and explicit contracts
- Avoid untyped data and implicit state transitions.
- External input, AI output, API responses, and persisted data must be validated at their trust boundaries.
- Canonical domain terms and enum values must be defined once and reused.
- Planned values and actual execution values must remain distinct.
- API contracts must be documented before frontend and backend integration.

### 5. Simple, maintainable implementation
- Prefer the smallest design that satisfies the current specification.
- Do not create speculative stores, services, repositories, abstractions, or dependencies.
- Keep route files and controllers thin.
- Organize code by cohesive feature and expose intentional public interfaces.
- Reuse components only when genuine reuse exists.
- Preserve existing user work and avoid unrelated rewrites.

### 6. Testable behavior and quality gates
- Critical domain invariants require automated tests.
- Frontend state transitions and recovery paths require component or integration tests.
- Backend endpoints require authorization, validation, and ownership tests.
- Desktop timer, reminder, sleep recovery, and window-lifecycle behavior require integration evidence when implemented.
- Formatting, type checking, linting, and relevant automated tests must pass before a feature is considered complete.
- A feature is not complete merely because it renders successfully.

### 7. Recoverable and accessible user experience
- Critical screens must define loading, empty, validation, partial, failure, and recovery behavior.
- User-entered data must be preserved after recoverable failures.
- Completed history must not be silently rewritten.
- Important status must not rely on color alone.
- Core full-application flows must be keyboard operable.
- Desktop messages must remain useful, dismissible, and non-intrusive.

### 8. Resource efficiency and platform scope
- The MVP targets Windows and Linux desktop environments.
- The widget must remain lightweight when the main application is closed.
- Hidden animations must pause.
- Timers and reminders must not poll the backend every second.
- External data must use bounded, coarse refresh and caching where appropriate.
- Mobile, web-only, macOS, local LLM inference, and unnecessary background services are outside the current platform scope unless introduced by a future approved specification.

### 9. Security and privacy
- Provider secrets and API keys must exist only in backend-controlled configuration and must never be embedded in the frontend.
- Authentication and authorization must be enforced by the backend.
- Logs must not expose tokens, passwords, personal planning content, or provider secrets.
- Store only the location precision required by the approved weather feature.
- New external services require an explicit specification of data sent, failure behavior, and cost limits.

### 10. Controlled scope and change management
- The frozen product concept is the canonical source for product scope, but it may be revised through an explicit documented decision.
- Specifications must reference canonical product decisions rather than duplicate conflicting versions.
- Out-of-scope ideas must not enter implementation tasks silently.
- Each feature branch must have one clear deliverable and verifiable completion criteria.
- Do not commit, push, merge, delete, or rewrite unrelated work without explicit authorization.

## Governance

- This constitution takes precedence over feature plans and task lists.
- Any intentional violation must be documented in the feature plan with rationale, impact, and a simpler alternative considered.
- Constitution changes require a reason, affected-artifact review, and semantic version update.

**Version**: 1.0.0 | **Ratified**: 2026-09-11 | **Last Amended**: 2026-09-11
