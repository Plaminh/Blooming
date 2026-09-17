# Feature Specification: Auth and User Settings

**Feature Branch**: `[012-auth-and-user-settings]`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "/speckit-specify Create a new backend feature specification named **Auth and User Settings** for Blooming"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register and Auto-Provision Settings (Priority: P1)

As a new user, I want to create an account so I can start using Blooming with sensible default settings.

**Why this priority**: Without registration, no new users can access the application. This is the foundation of the MVP.

**Independent Test**: Can be fully tested by submitting a valid registration payload and verifying that a user profile and default settings are immediately available in the database.

**Acceptance Scenarios**:

1. **Given** no existing account for a valid email, **When** the user submits registration with a valid password, **Then** the system creates the unverified account, provisions default settings, sends a verification email, and returns a 201 response.
2. **Given** an existing account for an email, **When** the user attempts to register with the same email, **Then** the system rejects the registration with a clear duplicate-account conflict error.

---

### User Story 2 - Login and Retrieve Profile (Priority: P1)

As a returning user, I want to log in with my credentials to access my secure profile and preferences.

**Why this priority**: Users must be able to return to their configured environment after their session expires or when using a new device.

**Independent Test**: Can be fully tested by logging in with valid credentials and using the returned token to retrieve the user's profile and settings.

**Acceptance Scenarios**:

1. **Given** a valid registered user, **When** the user logs in with correct credentials, **Then** the system returns a valid access token.
2. **Given** a login attempt, **When** the user provides an incorrect password or an unknown email, **Then** the system returns a generic authentication error that does not reveal if the email is registered.

---

### User Story 3 - Configure Application Settings (Priority: P2)

As an authenticated user, I want to update my timezone, quiet hours, and application preferences so the experience matches my needs.

**Why this priority**: Personalization of focus/break durations and quiet hours is central to the product's value proposition.

**Independent Test**: Can be fully tested by submitting a settings update and subsequently retrieving the settings to verify the changes persisted.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** the user updates their focus and break durations within valid limits, **Then** the system saves the new settings.
2. **Given** an authenticated user, **When** the user attempts to set an invalid focus duration, **Then** the system rejects the update with a validation error.
3. **Given** an authenticated user, **When** the user updates their quiet hours crossing midnight, **Then** the system correctly persists the start and end times.
4. **Given** an authenticated user, **When** the user updates some optional settings and omits others in the payload, **Then** the system preserves the existing values for the omitted fields.

---

### User Story 4 - Update Profile Information (Priority: P2)

As an authenticated user, I want to update my display name so the app addresses me correctly.

**Why this priority**: Allows users to customize their identity within the app.

**Independent Test**: Can be fully tested by submitting a profile update and verifying the new display name is returned in subsequent profile requests.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** the user updates their display name, **Then** the system saves and returns the updated profile.
2. **Given** an authenticated user, **When** the user attempts to update a protected field (like password hash) via the profile update endpoint, **Then** the system rejects the modification or safely ignores it.

---

### User Story 5 - Unauthorized Access Prevention (Priority: P1)

As a user, I want my data to be protected so that no one else can read or modify my settings or profile.

**Why this priority**: Security and privacy are critical. Unauthenticated or cross-account access would compromise user trust.

**Independent Test**: Can be fully tested by attempting to access the API endpoints without a token or with a fabricated/expired token.

**Acceptance Scenarios**:

1. **Given** an unauthenticated request, **When** a client requests any `/me` endpoint, **Then** the system returns a 401 Unauthorized error.
2. **Given** an expired access token, **When** a client requests any `/me` endpoint, **Then** the system returns a 401 Unauthorized error.

### Edge Cases

- What happens when quiet hours cross midnight? The system must accept and persist `quiet_hours_start` > `quiet_hours_end`.
- How does system handle missing optional settings fields in a PUT request? It preserves the existing values.
- How does the system handle database transaction failure during registration? It rolls back completely, ensuring no orphaned user record is created without settings.
- What happens if the `active_plant` is provided in settings? It is safely preserved, as plant selection business logic is out of scope for this feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `POST /api/v1/auth/register` endpoint to create a user account and associated default settings in a single transaction.
- **FR-002**: System MUST hash passwords securely before persistence and NEVER store or return plaintext passwords.
- **FR-003**: System MUST reject duplicate email addresses with a clear conflict response.
- **FR-004**: System MUST provide a `POST /api/v1/auth/login` endpoint that validates credentials securely and returns a JWT access token.
- **FR-005**: System MUST return the identical generic authentication error for unknown users and incorrect passwords.
- **FR-006**: System MUST provide a `GET /api/v1/me` endpoint returning the authenticated user's public profile.
- **FR-007**: System MUST provide a `PUT /api/v1/me` endpoint to update explicitly editable profile fields while ignoring or rejecting attempts to modify protected fields.
- **FR-008**: System MUST provide a `GET /api/v1/me/settings` endpoint returning the authenticated user's settings.
- **FR-009**: System MUST provide a `PUT /api/v1/me/settings` endpoint allowing users to update their preferences while preserving existing values for omitted editable fields.
- **FR-010**: System MUST validate that default focus duration is within documented limits (1-720 minutes).
- **FR-011**: System MUST validate that default break duration is within documented limits (0-180 minutes).
- **FR-012**: System MUST validate that `quiet_hours_start` and `quiet_hours_end` are both provided if quiet hours are enabled.
- **FR-013**: System MUST prevent users from accessing or modifying another user's profile or settings.

### Key Entities

- **User**: Represents the user's identity, credentials (hashed), and account status.
- **UserSettings**: Represents the user's application preferences (timezone, focus/break durations, quiet hours, display names, and desktop-specific visibility preferences).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully register and log in, receiving a valid JWT access token.
- **SC-002**: Users can update their settings and profile, with the changes persisting across backend restarts.
# Feature Specification: Auth and User Settings

**Feature Branch**: `[012-auth-and-user-settings]`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "/speckit-specify Create a new backend feature specification named **Auth and User Settings** for Blooming"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register and Auto-Provision Settings (Priority: P1)

As a new user, I want to create an account so I can start using Blooming with sensible default settings.

**Why this priority**: Without registration, no new users can access the application. This is the foundation of the MVP.

**Independent Test**: Can be fully tested by submitting a valid registration payload and verifying that a user profile and default settings are immediately available in the database.

**Acceptance Scenarios**:

1. **Given** no existing account for a valid email, **When** the user submits registration with a valid password, **Then** the system creates the unverified account, provisions default settings, sends a verification email, and returns a 201 response.
2. **Given** an existing account for an email, **When** the user attempts to register with the same email, **Then** the system rejects the registration with a clear duplicate-account conflict error.

---

### User Story 2 - Login and Retrieve Profile (Priority: P1)

As a returning user, I want to log in with my credentials to access my secure profile and preferences.

**Why this priority**: Users must be able to return to their configured environment after their session expires or when using a new device.

**Independent Test**: Can be fully tested by logging in with valid credentials and using the returned token to retrieve the user's profile and settings.

**Acceptance Scenarios**:

1. **Given** a valid registered user, **When** the user logs in with correct credentials, **Then** the system returns a valid access token.
2. **Given** a login attempt, **When** the user provides an incorrect password or an unknown email, **Then** the system returns a generic authentication error that does not reveal if the email is registered.

---

### User Story 3 - Configure Application Settings (Priority: P2)

As an authenticated user, I want to update my timezone, quiet hours, and application preferences so the experience matches my needs.

**Why this priority**: Personalization of focus/break durations and quiet hours is central to the product's value proposition.

**Independent Test**: Can be fully tested by submitting a settings update and subsequently retrieving the settings to verify the changes persisted.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** the user updates their focus and break durations within valid limits, **Then** the system saves the new settings.
2. **Given** an authenticated user, **When** the user attempts to set an invalid focus duration, **Then** the system rejects the update with a validation error.
3. **Given** an authenticated user, **When** the user updates their quiet hours crossing midnight, **Then** the system correctly persists the start and end times.
4. **Given** an authenticated user, **When** the user updates some optional settings and omits others in the payload, **Then** the system preserves the existing values for the omitted fields.

---

### User Story 4 - Update Profile Information (Priority: P2)

As an authenticated user, I want to update my display name so the app addresses me correctly.

**Why this priority**: Allows users to customize their identity within the app.

**Independent Test**: Can be fully tested by submitting a profile update and verifying the new display name is returned in subsequent profile requests.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** the user updates their display name, **Then** the system saves and returns the updated profile.
2. **Given** an authenticated user, **When** the user attempts to update a protected field (like password hash) via the profile update endpoint, **Then** the system rejects the modification or safely ignores it.

---

### User Story 5 - Unauthorized Access Prevention (Priority: P1)

As a user, I want my data to be protected so that no one else can read or modify my settings or profile.

**Why this priority**: Security and privacy are critical. Unauthenticated or cross-account access would compromise user trust.

**Independent Test**: Can be fully tested by attempting to access the API endpoints without a token or with a fabricated/expired token.

**Acceptance Scenarios**:

1. **Given** an unauthenticated request, **When** a client requests any `/me` endpoint, **Then** the system returns a 401 Unauthorized error.
2. **Given** an expired access token, **When** a client requests any `/me` endpoint, **Then** the system returns a 401 Unauthorized error.

### Edge Cases

- What happens when quiet hours cross midnight? The system must accept and persist `quiet_hours_start` > `quiet_hours_end`.
- How does system handle missing optional settings fields in a PUT request? It preserves the existing values.
- How does the system handle database transaction failure during registration? It rolls back completely, ensuring no orphaned user record is created without settings.
- What happens if the `active_plant` is provided in settings? It is safely preserved, as plant selection business logic is out of scope for this feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `POST /api/v1/auth/register` endpoint to create a user account and associated default settings in a single transaction.
- **FR-002**: System MUST hash passwords securely before persistence and NEVER store or return plaintext passwords.
- **FR-003**: System MUST reject duplicate email addresses with a clear conflict response.
- **FR-004**: System MUST provide a `POST /api/v1/auth/login` endpoint that validates credentials securely and returns a JWT access token.
- **FR-005**: System MUST return the identical generic authentication error for unknown users and incorrect passwords.
- **FR-006**: System MUST provide a `GET /api/v1/me` endpoint returning the authenticated user's public profile.
- **FR-007**: System MUST provide a `PUT /api/v1/me` endpoint to update explicitly editable profile fields while ignoring or rejecting attempts to modify protected fields.
- **FR-008**: System MUST provide a `GET /api/v1/me/settings` endpoint returning the authenticated user's settings.
- **FR-009**: System MUST provide a `PUT /api/v1/me/settings` endpoint allowing users to update their preferences while preserving existing values for omitted editable fields.
- **FR-010**: System MUST validate that default focus duration is within documented limits (1-720 minutes).
- **FR-011**: System MUST validate that default break duration is within documented limits (0-180 minutes).
- **FR-012**: System MUST validate that `quiet_hours_start` and `quiet_hours_end` are both provided if quiet hours are enabled.
- **FR-013**: System MUST prevent users from accessing or modifying another user's profile or settings.

### Key Entities

- **User**: Represents the user's identity, credentials (hashed), and account status.
- **UserSettings**: Represents the user's application preferences (timezone, focus/break durations, quiet hours, display names, and desktop-specific visibility preferences).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully register and log in, receiving a valid JWT access token.
- **SC-002**: Users can update their settings and profile, with the changes persisting across backend restarts.
- **SC-003**: 100% of unauthorized or unauthenticated requests to `/me` endpoints are rejected with 401 or 403 errors.
- **SC-004**: Passwords and security hashes are verifiably excluded from all API responses.
- **SC-005**: Alembic reports no unintended schema drift after applying the required migrations for new settings fields.

## Assumptions

- Standard JWT session-based access tokens are sufficient for this MVP (no refresh tokens).
- Logout MVP is implemented purely by the frontend deleting the access token; there is no refresh token or server-side revocation yet.
- Missing optional editable fields in `PUT` requests indicate they should remain unchanged.
- Frontend verify email is in scope.
- Canonical SQL will be updated directly, no forward-only migration.




## Documentation Updates
- Python version: 3.10.10
- No automated testing in this scope
- Do not create successive migrations (modify canonical SQL)
- Register returns no JWT token
- Frontend verify email is in scope
- Logout MVP: Frontend deletes JWT
