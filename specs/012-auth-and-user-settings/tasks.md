---
description: "Task list template for feature implementation"
---

# Tasks: Auth and User Settings

**Input**: Design documents from `/specs/012-auth-and-user-settings/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Automated tests (pytest) are deferred for now. Every user story requires an independently verifiable manual acceptance method.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Update `backend/requirements.txt` with `bcrypt` and `PyJWT` dependencies
- [x] T002 [P] Update `backend/app/core/config.py` with JWT settings (`SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Cập nhật canonical SQL schema và rebuild local database
- [x] T004 [P] Implement `backend/app/core/security.py` for password hashing and JWT encoding/decoding
- [x] T005 [P] Create Pydantic schemas in `backend/app/schemas/user.py` (`UserCreate`, `UserResponse`)
- [x] T006 [P] Create Pydantic schemas in `backend/app/schemas/token.py` (`TokenResponse`)
- [x] T007 [P] Create Pydantic schemas in `backend/app/schemas/user_settings.py` (`UserSettingsUpdate`, `UserSettingsResponse`)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Register and Auto-Provision Settings (Priority: P1) 🎯 MVP

**Goal**: As a new user, I want to create an account so I can start using Blooming with sensible default settings.

**Independent Test**: Can be fully tested by submitting a valid registration payload and verifying that a user profile and default settings are immediately available and accessible with the returned token.

### Tests for User Story 1
*Automated tests are deferred.*

### Implementation for User Story 1

- [x] T009 [US1] Implement user registration logic in `backend/app/services/user_service.py` (handles `User` and `UserSettings` creation in one transaction)
- [x] T010 [US1] Implement registration endpoint `POST /api/v1/auth/register` in `backend/app/api/routes/auth.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Login and Retrieve Profile (Priority: P1)

**Goal**: As a returning user, I want to log in with my credentials to access my secure profile and preferences.

**Independent Test**: Can be fully tested by logging in with valid credentials and using the returned token to retrieve the user's profile and settings.

### Tests for User Story 2
*Automated tests are deferred.*

### Implementation for User Story 2

- [x] T013 [P] [US2] Implement token extraction and validation dependency in `backend/app/api/deps.py`
- [x] T014 [US2] Implement credential verification logic in `backend/app/services/auth_service.py`
- [x] T015 [US2] Implement login endpoint `POST /api/v1/auth/login` in `backend/app/api/routes/auth.py`
- [x] T016 [US2] Implement profile endpoint `GET /api/v1/me` in `backend/app/api/routes/users.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 5 - Unauthorized Access Prevention (Priority: P1)

**Goal**: As a user, I want my data to be protected so that no one else can read or modify my settings or profile.

**Independent Test**: Can be fully tested by attempting to access the API endpoints without a token or with a fabricated/expired token.

### Tests for User Story 5
*Automated tests are deferred.*

### Implementation for User Story 5

- [x] T018 [US5] Ensure all `/me` and `/me/settings` endpoints enforce the authentication dependency in `backend/app/api/routes/users.py` and `backend/app/api/routes/user_settings.py`

**Checkpoint**: All P1 stories should now be independently functional

---

## Phase 6: User Story 3 - Configure Application Settings (Priority: P2)

**Goal**: As an authenticated user, I want to update my timezone, quiet hours, and application preferences so the experience matches my needs.

**Independent Test**: Can be fully tested by submitting a settings update and subsequently retrieving the settings to verify the changes persisted.

### Tests for User Story 3
*Automated tests are deferred.*

### Implementation for User Story 3

- [x] T020 [US3] Implement settings update logic (with partial updates and limits validation) in `backend/app/services/user_settings_service.py`
- [x] T021 [US3] Implement settings endpoints `GET /api/v1/me/settings` and `PUT /api/v1/me/settings` in `backend/app/api/routes/user_settings.py`

**Checkpoint**: User Story 3 complete.

---

## Phase 7: User Story 4 - Update Profile Information (Priority: P2)

**Goal**: As an authenticated user, I want to update my display name so the app addresses me correctly.

**Independent Test**: Can be fully tested by submitting a profile update and verifying the new display name is returned in subsequent profile requests.

### Tests for User Story 4
*Automated tests are deferred.*

### Implementation for User Story 4

- [x] T023 [US4] Implement profile update logic (ignoring protected fields) in `backend/app/services/user_service.py`
- [x] T024 [US4] Implement profile update endpoint `PUT /api/v1/me` in `backend/app/api/routes/users.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T025 Run `quickstart.md` validation scenarios against local server
- [ ] T026 Verify flow manually (automated tests deferred)
- [x] T027 Verify Alembic shows no schema drift (`alembic check`)
- [x] T028 Ensure OpenAPI schema reflects correct request/response shapes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P1)**: Can start after Foundational (Phase 2)
- **User Story 5 (P1)**: Can start after Foundational (Phase 2)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2)

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Implementation tasks:
Task: "Implement user registration logic in backend/app/services/user_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 5 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 & User Story 4
   - Developer B: User Story 2 & User Story 5
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit only when explicitly authorized; when authorized, group commits by completed task or logical unit.
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence


