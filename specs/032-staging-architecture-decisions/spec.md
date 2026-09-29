# Feature Specification: Staging Architecture Decisions

**Feature Branch**: `feature/staging-readiness`

**Created**: 2026-09-29

**Status**: Completed

**Input**: User description: "Block 0 - Staging Architecture Decisions"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Staging Session Lifetime (Priority: P1)

As a staging user on the desktop app, I want my login session to last for 24 hours so that I don't get unexpectedly logged out after returning from hours of sleep or being away from the app.

**Why this priority**: Without a stable session in the absence of a refresh token, testing staging builds is frustrating and fails frequently on wake.

**Independent Test**: Can be independently verified by checking the configured token expiry and ensuring network failures don't trigger logout.

**Acceptance Scenarios**:

1. **Given** the ADR-001 documentation, **When** reviewed, **Then** it explicitly configures staging access token lifetime to 24 hours and clarifies handling of network timeouts versus 401s.

---

### User Story 2 - Email Verification via Hosted Route (Priority: P1)

As a staging user registering for an account, I want the email verification link sent by Brevo to point to a valid hosted verification page instead of localhost, so that I can successfully verify my email.

**Why this priority**: Staging users cannot verify their accounts if links point to localhost.

**Independent Test**: Can be independently tested by reviewing ADR-002 and ensuring the documented configuration contract mandates a hosted URL.

**Acceptance Scenarios**:

1. **Given** the ADR-002 documentation, **When** reviewed, **Then** it defines the contract for email verification links pointing to a hosted URL instead of localhost.

---

### User Story 3 - Reminder Timing and Resynchronization Ownership (Priority: P2)

As a developer, I want a clear boundary where Rust/Tauri owns reliable timing/lifecycle triggers and Svelte owns data synchronization, so that future blocks do not introduce conflicting sync architectures.

**Why this priority**: Prevents architectural drift and duplicated work in upcoming blocks.

**Independent Test**: Can be verified by reviewing the architecture documentation and ensuring no actual Rust-to-Svelte implementation is prematurely introduced in Block 0.

**Acceptance Scenarios**:

1. **Given** the architecture documentation is reviewed, **When** checking ownership, **Then** it clearly states Rust/Tauri owns the trigger and Svelte owns a central `resync()` function.

### Edge Cases

- What happens when a token naturally expires after 24 hours? The user will have to log in again. (Refresh tokens are explicitly out of scope for Block 0).
- What happens when the user clicks the email link on a device that doesn't have the desktop app installed? The hosted web route will handle verification independently (Tauri deep linking is out of scope).

## Requirements *(mandatory)*

### Architecture & Config Contracts

- **AC-001**: Staging environment configuration contract MUST define `ACCESS_TOKEN_EXPIRE_MINUTES=1440` (24 hours).
- **AC-002**: Staging environment configuration contract MUST define `EMAIL_VERIFICATION_FRONTEND_URL` pointing to a hosted staging URL, not localhost.

### Functional Requirements

- **FR-001**: Architecture/error-handling contract MUST distinguish between network timeouts/offline states and actual authentication failures (401). Implementation is deferred to Block 5.
- **FR-002**: System MUST maintain Brevo as the email delivery provider.
- **FR-003**: Architecture documentation MUST define Rust/Tauri as the owner of reliable timing and lifecycle triggers.
- **FR-004**: Architecture documentation MUST define Svelte as the owner of a central `resync()` function responsible for fetching sessions, reminders, and refreshing plant state.

### Key Entities

- **Access Token**: A 24-hour JWT for staging environments.
- **Verification Email**: Delivered via Brevo containing a token link to the hosted frontend.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 24-hour staging token policy is explicitly configured or documented.
- **SC-002**: No localhost assumption remains in the documented staging verification contract.
- **SC-003**: Reminder ownership has exactly one clear documented boundary (Rust=trigger, Svelte=fetch).
- **SC-004**: No accidental refresh-token, deep-link, or reconnect implementation is introduced in this block.

## Assumptions

- This block represents architecture decisions and minimal configuration only.
- Later blocks (Block 0.5, Blocks 1-5) will implement the concrete runtime behavior. Deep linking is future/post-MVP, refresh tokens are production hardening, and DB migrations belong to Block 7.
- The environment variable `EMAIL_VERIFICATION_FRONTEND_URL` or equivalent contract will be identified and documented.
