# Tasks: MVP AI System

**Input**: Design documents from `specs/022-mvp-ai-system/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/api-contracts.md, quickstart.md

**Tests**: Required by constitution (backend endpoints require validation/authorization tests). Every user story requires an independently verifiable acceptance method per quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Exact file paths are included in all descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure verification

- [X] T001 Ensure `httpx` and `pydantic` dependencies exist in `backend/requirements.txt`
- [X] T002 Add required AI Gateway env variables to `backend/.env.example` (`AI_GATEWAY_URL`, `GROQ_API_KEY`, `GEMINI_API_KEY`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Create schema models (`AIRequestContext`, `ValidationResult`, `TaskDraft`, `TodayDraftProposal`, `RoadmapDraftProposal`) in `backend/app/models/ai_schemas.py`
- [X] T004 [P] Create router shell and interface structure in `backend/app/services/ai_router.py`
- [X] T005 [P] Create `POST /api/v1/planning/draft` endpoint shell in `backend/app/api/routes/planning.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Deterministic Rule Parsing (Priority: P1) 🎯 MVP

**Goal**: Simple, clear commands are handled deterministically without invoking external LLMs.

**Independent Test**: Scenario 1 from `quickstart.md` (cURL requesting a explicit task command returns instantly without AI latency).

### Tests for User Story 1
- [X] T006 [P] [US1] Create unit tests for RuleParser in `backend/tests/unit/test_rule_parser.py`

### Implementation for User Story 1
- [X] T007 [US1] Implement `RuleParser` logic in `backend/app/services/rule_parser.py`
- [X] T008 [US1] Integrate `RuleParser` into `backend/app/services/ai_router.py` logic flow

**Checkpoint**: At this point, User Story 1 should be fully functional.

---

## Phase 4: User Story 4 - AI Output Safety Boundary (Priority: P1)

**Goal**: AI only proposes changes; strict schema and business validation guarantees no direct database mutation or malformed data.

**Independent Test**: Sending malformed drafts or requesting DB changes fails validation safely without side effects.

*(Note: Executed before US2/US3 to ensure all AI responses are properly gated before connecting to real LLMs)*

### Tests for User Story 4
- [X] T009 [P] [US4] Create validation boundary tests in `backend/tests/services/test_ai_router.py` ensuring invalid schemas are rejected

### Implementation for User Story 4
- [X] T010 [US4] Implement `BusinessValidator` logic in `backend/app/services/business_validator.py` utilizing the Pydantic schemas

**Checkpoint**: Safe boundary established. Ready to plug in AI providers.

---

## Phase 5: User Story 2 - Primary AI Routing via Groq (Priority: P1)

**Goal**: Ambiguous scheduling requests are interpreted by the fast Groq AI provider.

**Independent Test**: Scenario 2 from `quickstart.md` (cURL requesting ambiguous task planning returns structured data via Groq).

### Tests for User Story 2
- [X] T011 [P] [US2] Create unit tests mocking `httpx` responses for Groq in `backend/tests/services/test_groq_provider.py`

### Implementation for User Story 2
- [X] T012 [US2] Implement `GroqProvider` using `httpx` in `backend/app/services/groq_provider.py`
- [X] T013 [US2] Integrate `GroqProvider` into the main `backend/app/services/ai_router.py` orchestration logic

**Checkpoint**: Primary AI routing works.

---

## Phase 6: User Story 3 - Gemini Fallback (Priority: P2)

**Goal**: Seamless retry with a fallback AI provider if Groq fails or times out.

**Independent Test**: Scenario 3 from `quickstart.md` (Simulate Groq API failure and confirm response still succeeds via Gemini).

### Tests for User Story 3
- [X] T014 [P] [US3] Create unit tests mocking `httpx` responses for Gemini in `backend/tests/services/test_gemini_provider.py`
- [X] T015 [P] [US3] Add fallback integration test in `backend/tests/services/test_ai_router.py` verifying Gemini is called if Groq raises an error

### Implementation for User Story 3
- [X] T016 [US3] Implement `GeminiProvider` using `httpx` in `backend/app/services/gemini_provider.py`
- [X] T017 [US3] Update `backend/app/services/ai_router.py` with try/except fallback logic to invoke `GeminiProvider`
- [X] T018 [US3] Update `backend/app/api/routes/planning.py` to map meta response data (`fallback_triggered`) per `api-contracts.md`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T019 Execute all test scenarios in `quickstart.md` manually to confirm end-to-end functionality. (Automated integration complete. Live provider smoke test pending real credentials.)
- [X] T020 Review `backend/app/services/ai_router.py` to ensure telemetry/logging aligns with observability requirements (no sensitive PII logging)

---

## Phase 8: End-to-End Reconciliation

**Purpose**: Fix provider assumptions, time/timezone issues, schemas, and error boundaries.

- [X] T021 Implement `AIProvider` abstraction and move `GroqProvider` and `GeminiProvider` to it.
- [X] T022 Update `AIRequestContext` with strict Pydantic `extra="forbid"` and provenance types (`InferredValue`).
- [X] T023 Implement `BusinessValidator` in `backend/app/services/business_validator.py`.
- [X] T024 Fix configuration in `backend/app/core/config.py` and `.env.example`.
- [X] T025 Resolve time/timezone properly in `planning.py`.
- [X] T026 Update `RuleParser` to narrow scope to distinct deterministic action.
- [X] T027 Add explicit schemas for `TodayDraftProposal` and `RoadmapDraftProposal`.
- [X] T028 Update all unit tests (`test_ai_router`, `test_rule_parser`, `test_groq_provider`, `test_gemini_provider`) to reflect the reconciled schemas and abstractions.
- [X] T029 Update `spec.md`, `plan.md`, `data-model.md`, `contracts/api-contracts.md`, and `quickstart.md` to reflect true end-to-end behavior.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational phase
- **US4 (Phase 4)**: Depends on Foundational phase; conceptually bounds AI providers so completed next.
- **US2 (Phase 5)**: Depends on US4 (Safety Boundary)
- **US3 (Phase 6)**: Depends on US2 (Groq implementation) to establish fallback logic
- **Polish (Final Phase)**: Depends on all user stories

### Parallel Opportunities

- Foundational model creation, endpoint stubs, and router stubs can all be created in parallel (T003, T004, T005).
- All unit tests across stories can be drafted in parallel.
- `RuleParser` (US1) and `GroqProvider` (US2) can technically be implemented in parallel by different developers and wired together in the router afterward.

---

## Parallel Example: Foundational Phase

```bash
# Launch models and router stubs simultaneously:
Task: "T003 [P] Create schema models in backend/app/models/ai_schemas.py"
Task: "T004 [P] Create router shell and interface structure in backend/app/services/ai_router.py"
Task: "T005 [P] Create POST /api/v1/planning/draft endpoint shell in backend/app/api/routes/planning.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & Phase 2.
2. Complete Phase 3 (US1).
3. **STOP and VALIDATE**: Verify rule parser handles deterministic commands instantly. 
4. Deploy MVP increment without any LLM network calls enabled.

### Incremental Delivery

1. Foundation + US1 (Rule Parser)
2. Add US4 (Safety boundaries established in router)
3. Add US2 (Groq provider active)
4. Add US3 (Gemini fallback active)
