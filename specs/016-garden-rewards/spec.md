# Feature Specification: 016-garden-rewards

**Feature Branch**: `016-garden-rewards`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Create feature 016-garden-rewards based on the checklist in 05-garden-rewards(1).md..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Garden State and Catalog (Priority: P1)

The user opens the Garden screen and sees their current plant, owned plants, and available balances (Water and Leaves) loaded from the real backend instead of mock data. They can view the plant catalog with correct locked/unlocked states.

**Why this priority**: Without loading real state, no further garden interactions are meaningful. This is the foundation of the feature.

**Independent Test**: Can be tested by opening the application, logging in, and verifying the Garden UI matches the database state for the user.

**Acceptance Scenarios**:
1. **Given** a user with existing Garden state and resources, **When** they navigate to the Garden, **Then** they see their correct balances, selected plant, and catalog unlock statuses.
2. **Given** a new user without Garden state, **When** they navigate to the Garden, **Then** an initial Garden state is safely created and displayed.

---

### User Story 2 - Earn Rewards via Work (Priority: P1)

The user completes a Pomodoro session and is awarded Water. They complete a Task or Milestone and are awarded Leaves. These rewards are granted exactly once per qualifying event, even if the request is retried.

**Why this priority**: The core loop of the app connects work to garden rewards. This must be functional and idempotent to prevent reward farming.

**Independent Test**: Complete a Pomodoro, verify Water increases. Retry the submission, verify it does not increase again.

**Acceptance Scenarios**:
1. **Given** a valid Pomodoro completion, **When** the session is submitted, **Then** Water is awarded exactly once and recorded in the ledger.
2. **Given** a qualifying Task/Milestone completion, **When** it is submitted, **Then** Leaves are awarded exactly once.
3. **Given** an already-rewarded completion event, **When** it is re-submitted or retried, **Then** no duplicate rewards are granted.

---

### User Story 3 - Unlock and Select Plant (Priority: P1)

The user spends their accumulated resources to unlock a new plant from the catalog, then selects it to be their active plant in the Garden.

**Why this priority**: Users need a way to spend their rewards to feel progress in the Garden.

**Independent Test**: Click an affordable locked plant to unlock it, verify balances decrease, then select the new plant and verify the UI updates.

**Acceptance Scenarios**:
1. **Given** a user with sufficient resources, **When** they choose to unlock a plant, **Then** the cost is deducted atomically, ownership is recorded, and the plant becomes unlocked.
2. **Given** a user with insufficient resources, **When** they try to unlock a plant, **Then** the action is rejected and balances remain unchanged.
3. **Given** an owned plant, **When** the user selects it, **Then** it becomes the active plant and persists across application reloads.

---

### User Story 4 - Water Plant for Vitality (Priority: P1)

The user spends Water to water their active plant. The plant's vitality is updated based on the watering timestamp, without relying on background jobs.

**Why this priority**: Completes the core garden interaction loop by requiring users to return and maintain their plant.

**Independent Test**: Water the plant, observe Water balance decrease, and verify vitality displays correctly based on the new timestamp.

**Acceptance Scenarios**:
1. **Given** a user with sufficient Water, **When** they water their plant, **Then** Water is deducted, the `last_watered_at` timestamp is updated, and vitality is recalculated correctly.
2. **Given** multiple concurrent water requests, **When** they arrive, **Then** Water is not overspent.

### Edge Cases

- User has no Garden state yet.
- Catalog is empty or temporarily unavailable.
- Plant does not exist or is unavailable.
- User attempts to select a locked plant.
- User attempts to unlock an already-owned plant.
- User has insufficient Leaves or Water.
- Two unlock or watering requests arrive concurrently.
- The same completion event is submitted repeatedly.
- A completed item is reopened and completed again.
- `last_watered_at` is missing, old, or in a different timezone representation.
- The selected plant is removed from the active catalog but remains in historical ownership data.
- API request fails after the UI enters a pending state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST load and persist the authenticated user's Garden state (balances, owned plants, selected plant, watering timestamps).
- **FR-002**: System MUST provide an API for the plant catalog that distinguishes locked, unlocked, and selected states based on real user ownership.
- **FR-003**: System MUST award 1 Water exactly once for a valid Pomodoro completion.
- **FR-004**: System MUST award 1 Leaf exactly once for any Task or Milestone completion.
- **FR-005**: System MUST deduct cost atomically when unlocking a plant and prevent duplicate deductions.
- **FR-006**: System MUST persist the user's selected plant and ensure exactly one plant is active.
- **FR-007**: System MUST maintain a durable, idempotent reward ledger for all resource changes, preventing double spending or negative balances.
- **FR-008**: System MUST calculate plant vitality lazily from `last_watered_at` using a deterministic formula (Maximum vitality is 100, decays 10 points per 24 hours, watering costs 1 Water and adds +10 vitality).
- **FR-009**: System MUST enforce that the backend is authoritative for all reward eligibility, costs, balances, and vitality, ignoring frontend-supplied amounts.
- **FR-010**: System MUST connect existing Garden UI components to these backend APIs without redesigning the layout or replacing existing assets.

### Key Entities

- **GardenState**: User's current selected plant, balances (Water, Leaves).
- **PlantCatalog/Plant**: Available plants, their IDs, display assets, and unlock costs.
- **PlantOwnership**: Record of which plants the user has unlocked.
- **RewardLedger**: Immutable transaction log of resource grants and spends (source event ID, type, amount) to guarantee idempotency.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Real persisted user state and plant catalog render successfully in the Garden UI.
- **SC-002**: Valid Pomodoro and Task/Milestone completions grant exact respective rewards idempotently (0% duplicate reward rate on retries).
- **SC-003**: Unlocking a plant correctly deducts the exact cost once and persists ownership reliably.
- **SC-004**: Restarting or reloading the application preserves all Garden state, selections, and balances 100% of the time.
- **SC-005**: Plant vitality calculates correctly across time intervals without requiring any background processes.
- **SC-006**: Balances mathematically cannot become negative under concurrent load.

## Assumptions

- We assume existing Pomodoro and Task/Milestone completion models/flows exist and can be hooked into for reward generation.
- We assume the existing UI is largely structurally ready to receive real data bindings.
- We assume timezone-safe timestamps (UTC) are used consistently across the application for the vitality calculation.
- We assume that if the repository already has established rules for rewards or vitality, they take precedence over the needs clarification questions.
