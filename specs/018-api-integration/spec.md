# Feature Specification: API Integration

**Feature Branch**: `[018-api-integration]`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Integrate all existing Blooming frontend screens with the local FastAPI backend and PostgreSQL database, replacing the remaining mock data and mock actions with real authenticated API calls."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authentication and Session Management (Priority: P1)

Users can sign in to their accounts and maintain an authenticated session across all features, ensuring their data remains secure and personalized.

**Why this priority**: Authentication is the foundation for all user-specific data access. No other features can reliably save or load data without a working session.

**Independent Test**: Can be fully tested by signing in via the existing login form, verifying the application routes correctly, and ensuring subsequent API calls include the authorization token.

**Acceptance Scenarios**:

1. **Given** a user is signed out, **When** they submit valid credentials, **Then** they are authenticated, their session is maintained, and they are routed according to existing onboarding rules.
2. **Given** a user provides invalid credentials, **When** they submit the form, **Then** backend validation errors are displayed.
3. **Given** an authenticated user, **When** their session expires or becomes invalid, **Then** their local session is cleared securely and they are prompted to sign in again.
4. **Given** a user starts the app, **When** they previously authenticated, **Then** their session is seamlessly restored.

---

### User Story 2 - Today and Planning Workflow (Priority: P1)

Users can view, manage, and complete their current-day plans and tasks using data persisted securely in the backend, allowing reliable daily scheduling.

**Why this priority**: The daily workflow is the core use case of the application.

**Independent Test**: Can be tested by navigating to the Today screen, creating tasks, completing them, and refreshing the app to verify data persistence.

**Acceptance Scenarios**:

1. **Given** a user opens the Today screen, **When** data loads, **Then** they see their tasks and sessions fetched from the backend.
2. **Given** a user has no tasks for the day, **When** the Today screen loads, **Then** a meaningful empty state is displayed.
3. **Given** a user interacts with a task (create, edit, complete, delete), **When** the action succeeds, **Then** the UI and backend states reflect the change and derived info is updated.
4. **Given** a backend error occurs during a mutation, **When** the request fails, **Then** the UI shows an error and avoids displaying stale or artificially successful state.

---

### User Story 3 - Pomodoro Focus Sessions (Priority: P1)

Users can run focus timers locally on their device, which log their successful focus periods to the backend for accurate historical tracking.

**Why this priority**: Focus tracking drives statistics and garden rewards.

**Independent Test**: Can be tested by starting, running, and completing a timer, then checking if the focus session was recorded properly in the backend.

**Acceptance Scenarios**:

1. **Given** a user starts a timer, **When** the timer runs, **Then** the countdown is handled entirely by the frontend without per-second API requests.
2. **Given** a focus session ends or is cancelled, **When** it completes, **Then** the result is persisted to the backend safely without duplicate submissions.
3. **Given** the persistence request fails, **When** an error occurs, **Then** the UI reconciles the state and does not falsely indicate successful logging.

---

### User Story 4 - Goals and Milestones (Priority: P2)

Users can organize their long-term objectives using goals and milestones synchronized with the backend.

**Why this priority**: Goals provide the overarching structure for the user's focus sessions.

**Independent Test**: Can be tested by loading the Goals screen, adding new goals/milestones, and verifying they appear upon refresh.

**Acceptance Scenarios**:

1. **Given** a user visits the Goals screen, **When** goals load, **Then** they only see goals and milestones belonging to their account.
2. **Given** a user updates a milestone, **When** the change is saved, **Then** the milestone list and aggregate goal progress remain consistent.

---

### User Story 5 - Garden Progression and Rewards (Priority: P2)

Users can view and manage their virtual garden, using earned currency and progression data stored safely in the backend.

**Why this priority**: The garden is a key motivational component, relying directly on valid focus session data.

**Independent Test**: Can be tested by viewing garden state, purchasing a plant if currency allows, and ensuring the transaction persists.

**Acceptance Scenarios**:

1. **Given** a user views the Garden, **When** the state loads, **Then** unlocked, locked, and selected items accurately reflect backend progression data.
2. **Given** a user attempts an action (e.g., watering, selecting), **When** the backend accepts it, **Then** currency and plant states update consistently.
3. **Given** a user lacks sufficient currency, **When** they try to unlock a plant, **Then** the action is rejected and the optimistic UI behavior does not permanently misrepresent success.

---

### User Story 6 - Statistics and History (Priority: P2)

Users can review their past activity and performance metrics calculated and provided by the backend.

**Why this priority**: Provides insight into user productivity over time.

**Independent Test**: Can be tested by navigating to Statistics, changing periods, and verifying that the data accurately corresponds to the backend without carrying over previous values.

**Acceptance Scenarios**:

1. **Given** a user views statistics, **When** they select a period, **Then** data is fetched from the backend and mapped correctly to charts and cards.
2. **Given** a user has no activity in a period, **When** statistics load, **Then** legitimate zero values are handled distinctly from missing data or empty states.
3. **Given** a previous statistics request was successful, **When** a new request fails, **Then** charts do not retain the previous values falsely.

---

### User Story 7 - Settings and User Profile (Priority: P3)

Users can manage their account preferences, which persist across sessions and devices.

**Why this priority**: Essential for personalization, but less critical than daily planning or timers.

**Independent Test**: Can be tested by changing a setting, refreshing the application, and observing the setting's retention.

**Acceptance Scenarios**:

1. **Given** a user opens Settings, **When** the screen loads, **Then** their saved profile and preferences are mapped to the controls.
2. **Given** a user updates a setting, **When** saving fails, **Then** the unsaved input remains intact with an appropriate error, unless existing UX explicitly resets it.

---

### Edge Cases

- What happens when a user attempts an action right as their authentication token expires? (Request should be blocked, or gracefully fail as a 401 and redirect to login, preserving their intended action where possible).
- How does the system handle rapid navigation or rapid filter changes? (Should avoid race conditions, cancelling outdated requests or safely dropping stale responses).
- What happens if the backend is unreachable (network failure)? (Should show a generic connection error state instead of a blank screen).
- How does the UI handle zero-valued statistics versus incomplete API responses? (Zeros are plotted normally, empty data shows empty states, missing data shows an error).
- What happens if the backend rejects an action due to a conflict or validation issue? (The error detail is preserved and presented to the user).

## Requirements *(mandatory)*

### Functional Requirements

#### Shared API Client
- **FR-001**: System MUST provide a reusable API client configured with the local FastAPI base URL.
- **FR-002**: System MUST attach the current user's authentication credential to all protected requests automatically.
- **FR-003**: System MUST gracefully handle successful responses, validation errors, auth failures (401), missing resources (404), conflicts (409), and 5xx errors across all modules.
- **FR-004**: System MUST preserve backend error details for presentation in the UI and prevent silent continuation after API failures.
- **FR-005**: System MUST NOT log access tokens, passwords, sensitive information, or full private payloads.

#### Feature Replacements
- **FR-006**: System MUST replace all mock data and mock actions in Authentication, Onboarding, Today, Pomodoro, Goals, Garden, Settings, and Statistics screens with real API calls.
- **FR-007**: System MUST use existing backend endpoints without inventing new payloads or entities.
- **FR-008**: System MUST display appropriate loading, background refresh, empty, validation, and error states using existing shared UI patterns.
- **FR-009**: System MUST prevent duplicate submissions caused by repeated clicks or lifecycle events during API calls.
- **FR-010**: System MUST refresh or invalidate related data cleanly after successful mutations.

#### Component-Specific Rules
- **FR-011**: Pomodoro timers MUST remain frontend-controlled during countdowns, only communicating with the backend for persistence events (start, complete, cancel, update).
- **FR-012**: Companion widget timer and polling behavior MUST remain frontend-only without newly introduced WebSocket/SSE persistence.

### Key Entities

- **Auth Session**: Secure token validating user identity for protected features.
- **Task/Daily Plan**: User's items scheduled for the current day.
- **Focus Record**: Historical entry of a completed Pomodoro session.
- **Goal/Milestone**: Long-term objectives mapping to tasks or focus time.
- **Garden State**: Representation of plants, unlocks, currency, and progress based on focus effort.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the listed screens (Authentication, Onboarding, Today, Pomodoro, Goals, Garden, Settings, Statistics) operate against the local backend instead of mock data.
- **SC-002**: Authenticated sessions are respected, with 0 protected API calls occurring without valid credentials.
- **SC-003**: Network and validation failures trigger explicit error states rather than silent failures or false success UI updates.
- **SC-004**: UI rendering matches backend constraints natively, with 0 instances of optimistic UI permanently conflicting with a rejected backend operation.

## Assumptions

- The existing FastAPI backend is feature-complete for the listed screens.
- Any backend constraints (validation rules, database schemas) reflect the final intended product behavior.
- The project's existing token and session structure is secure and adequate for the MVP.
- Offline-first functionality, cloud deployment, and mobile support remain explicitly out of scope for this integration effort.
- The UI design is final and does not require a visual overhaul.
