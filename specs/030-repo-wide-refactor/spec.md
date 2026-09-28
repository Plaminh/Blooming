# Feature Specification: Repository-Wide Architectural Refactor

**Feature Branch**: `[030-repo-wide-refactor]`

**Created**: 2026-09-28

**Status**: Draft

**Input**: User description: "Create and execute one comprehensive SpecKit feature for a repository-wide architectural refactor of the Blooming project..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Maintain Core Baseline (Priority: P1)

The refactored application must preserve the observable business behavior of the pre-refactor baseline.

**Why this priority**: The primary invariant of this refactor is `Observable business behavior before refactor == Observable business behavior after refactor`.

**Independent Test**: Can be tested by running the automated and manual baselines before and after the refactoring phase.

**Acceptance Scenarios**:

1. **Given** the system has captured the pre-refactor baseline, **When** the architectural refactor is applied, **Then** all deterministic automated tests must pass without any new regressions.
2. **Given** a manual regression test suite, **When** executed on the refactored system, **Then** the manual flows (authentication, onboarding, today plan, Mr. Bloom chat, goals, pomodoro, re-plan, garden, widget) must behave exactly as they did before the refactor.

---

### User Story 2 - Backend Separation of Concerns (Priority: P2)

The backend routing, service, and database interaction boundaries must be clearly separated and logically sound.

**Why this priority**: Thin routes and decoupled domain logic are critical for system maintainability.

**Independent Test**: Can be tested via unit tests ensuring service methods do not contain route-level HTTP logic, and routes do not contain domain or SQLAlchemy query logic.

**Acceptance Scenarios**:

1. **Given** a backend API route, **When** a request is made, **Then** it delegates application logic to a service rather than directly executing domain logic or database transactions.
2. **Given** a transaction boundary requirement, **When** a database operation is triggered from a service, **Then** the service correctly owns the transaction boundary (commit/rollback) rather than the lower-level repository helpers.

---

### User Story 3 - Frontend Architectural Consolidation (Priority: P2)

The frontend components, state, and dependencies must follow a clear feature-first architecture without duplicated logic or cyclical dependencies.

**Why this priority**: Eases future frontend development and reduces visual/logic inconsistencies.

**Independent Test**: Can be validated using static analysis (no cyclical imports) and structural reviews.

**Acceptance Scenarios**:

1. **Given** the frontend codebase, **When** checking dependency direction, **Then** shared code does not depend on feature implementations, and routes only compose feature views.
2. **Given** a reusable UI component like a Button, **When** reviewing the codebase, **Then** there is only one canonical implementation in the shared UI directory, not scattered across feature directories.

---

### User Story 4 - Database Bootstrap and Alignment (Priority: P3)

The database schema and ORM models must be aligned and correctly bootstrapped using the existing per-table SQL setup.

**Why this priority**: A correct, reproducible database setup is essential for dev environments and application robustness.

**Independent Test**: Can be verified by running the SQL installer against a fresh PostgreSQL database.

**Acceptance Scenarios**:

1. **Given** a fresh PostgreSQL instance, **When** the SQL installer runs, **Then** the complete schema initializes successfully without relying on filename order hacks.
2. **Given** the SQLAlchemy models, **When** compared to the SQL schema, **Then** table names, column types, constraints, and relationships are aligned.

### Edge Cases

- What happens when a known bug is encountered during the refactor? (It should be documented and kept, NOT fixed, unless required for the refactor to proceed).
- How does the system handle AI-based non-deterministic tests? (They must be identified and excluded from deterministic regression results).
- How do we handle stale data or unused tables? (Only remove if concrete evidence proves they are unused, no imports, no reads/writes. Document removal decisions).

## Requirements *(mandatory)*

### Functional Requirements

- **RF-001**: Existing Today planning flows must produce equivalent observable results after refactor.
- **RF-002**: Existing API contracts must remain compatible unless an explicitly documented contract cleanup is approved.
- **RF-003**: The database installer must create a working fresh schema from an empty PostgreSQL database without reintroducing Alembic.
- **RF-004**: Frontend shared code must not depend on feature implementation.
- **RF-005**: Backend routes must delegate application logic to services rather than directly own domain orchestration.
- **RF-006**: SQL schema and SQLAlchemy metadata must be verifiably aligned.
- **RF-007**: No new deterministic automated test failures may be introduced.
- **RF-008**: Manual baseline flows must remain functionally equivalent.
- **RF-009**: The AI package structure must be reorganized by responsibility (e.g. llm, nlu, drafting, coach, handlers) without changing prompt text or routing semantics.
- **RF-010**: Centralize UI design tokens (colors, typography, spacing) into a canonical token layer; feature themes can only override if there is a legitimate feature skin (like a widget).

### Key Entities

- **System Architecture**: The holistic structural organization of both frontend and backend codebases.
- **Pre-Refactor Baseline**: The recorded behavior (tests, manual cases) of the system before any changes are made.
- **Known Bug Register**: A list of bugs that existed prior to refactoring that are intentionally left unfixed to preserve behavioral equivalence.
- **Shared Primitives**: Consolidated UI components and styles.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of deterministic automated tests that passed before the refactor continue to pass after the refactor.
- **SC-002**: 100% of defined manual regression scenarios execute with equivalent behavior (Pass/Fail) compared to the pre-refactor baseline.
- **SC-003**: 0% usage of cyclical dependencies (shared code depending on feature code) in the frontend.
- **SC-004**: The database can be initialized cleanly from `install.sql` in exactly 1 pass on a fresh PostgreSQL instance.
- **SC-005**: Dead code removal leaves zero unreferenced production scripts, endpoints, or components, verified by static analysis.

## Assumptions

- No new product features, UI workflows, or AI behaviors are to be introduced during this phase.
- Existing known bugs are acceptable and will not be fixed as part of this scope.
- Automated tests are currently capable of passing deterministically (excluding AI/LLM tests).
- The current per-table SQL installer strategy is sufficient and will not be replaced by a migration tool like Alembic.
- Moving timer ownership from frontend to Rust or changing rate-limiting policies are out of scope.
