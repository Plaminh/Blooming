# Tasks: Blooming Multi-Tier Chatbot MVP

**Input**: Design documents from `/specs/025-blooming-chatbot/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are required where mandated by the Constitution or feature specification. Every user story still requires an independently verifiable acceptance method.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup & Baseline

**Purpose**: Project initialization and prerequisite verification

- [x] T001 Run and record the existing backend test baseline using `pytest`
- [x] T002 Run and record the existing frontend test baseline using `npm run test` in `frontend/`
- [x] T003 [P] Run configured lint, type-check, and format-check commands (`npm run check`, `ruff check .`, `mypy app`, frontend lint)
- [x] T004 [P] Verify the current database migration head using `alembic current`
- [x] T005 [P] Verify the feature specification checklists are complete in `specs/025-blooming-chatbot/`
- [x] T006 [P] Verify `.env.example` contains placeholders only and no production keys
- [x] T007 Confirm exact repository paths identified in `specs/025-blooming-chatbot/plan.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T008 Setup AI usage log schema and generate migration `alembic/versions/xxx_ai_usage.py` for `AiUsageLog`
- [x] T009 Create `AiUsageLog` SQLAlchemy model in `backend/app/db/models/ai_usage.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Stabilized Foundation (Priority: P1) 🎯 MVP

**Goal**: Fixes foundational UX bugs before adding complex AI tiers. Corresponds to PR 1-2.

**Independent Test**: Can be tested by invoking basic chat with various timezones and network timeouts, verifying the UI and robust backend fallbacks without triggering advanced planning flows.

### Implementation for User Story 1 (PR 1 & PR 2)

- [x] T010 [US1] Create HTTP async client provider abstraction in `backend/app/ai/providers.py`
- [x] T011 [P] [US1] Implement circuit breaker logic and 429 Retry-After parsing in `backend/app/ai/providers.py`
- [x] T012 [P] [US1] Implement rate limiter dependency `chat_rate_limit` in `backend/app/api/routes/assistant.py`
- [x] T013 [P] [US1] Update `backend/app/main.py` lifespan to initialize and close the shared `ai_client`
- [x] T014 [US1] Fix frontend IME Enter handling in `frontend/src/lib/features/mr-bloom/components/molecules/ChatComposer.svelte`
- [x] T015 [P] [US1] Fix frontend auto-scroll logic in `frontend/src/lib/features/mr-bloom/components/organisms/MrBloomConversationPanel.svelte`
- [x] T016 [P] [US1] Fix frontend multi-line display and retry logic in `frontend/src/lib/features/mr-bloom/components/molecules/ChatMessage.svelte`
- [x] T017 [US1] Write test for provider circuit breaker in `backend/tests/unit/test_providers.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: Foundational Data Model & Contracts (Priority: P2)

**Goal**: Prepare the backend data model and API contracts for the upcoming chatbot tiers.

- [x] T018 [US2] Update canonical `TodayDraft` and `TaskDraft` schemas in `backend/app/schemas/drafts.py`
- [x] T019 [US2] Update `_normalize_and_schedule` in `backend/app/services/today_service.py` to map `breakAfterMin` to `preferred_break_duration_minutes`
- [x] T020 [US2] Fix `test_today_preview.py` imports and ensure baseline tests pass

---

## Phase 5: User Story 2 - Router & Rule Fallback (Priority: P2)

**Goal**: Establish the core tier pipeline, allowing deterministic rules and chitchat to work without planning complexity. Corresponds to PR 4 & 5.

**Independent Test**: Send conversational intents ("Hello", "Thank you") to verify the LLM Chitchat tier handles them. Send rule-based intents ("Skip optional tasks") to verify the Rule Handler processes them immediately.

### Implementation for User Story 2 (PR 4 & PR 5)

- [x] T021 [US2] Update `assistant.ChatRequest` to include standard fields (`history`, `draft`, `garden`, `tz`)
- [x] T022 [US2] Create the unified router pipeline entry point in `backend/app/services/assistant_service.py`
- [x] T023 [US2] Implement deterministic rule handlers in `backend/app/ai/handlers/rules.py`
- [x] T024 [P] [US2] Implement deterministic routing in `backend/app/ai/router.py`
- [x] T025 [P] [US2] Migrate basic chitchat logic to `backend/app/ai/handlers/chitchat.py`
- [x] T026 [P] [US2] Connect `chat` in `backend/app/services/assistant_service.py` to the AI handlers
- [x] T027 [US2] Update frontend `AssistantApi.chat` types to reflect new request contract
- [x] T026A [P] [US2] Implement validation, fixes, and repair logic in `backend/app/ai/validators.py`
- [x] T027A [US2] Remove fake timeline generation in `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts`
- [x] T028 [US2] Integrate real `/today/preview` state into `frontend/src/lib/features/mr-bloom/components/organisms/TimelineDraftPreview.svelte`
- [x] T029 [US2] Write tests for deterministic parser in `backend/tests/unit/test_parser.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Intelligent Planner Cascade & Repair (Priority: P3)

**Goal**: Intelligent scheduling via LLM cascade that respects constraints and repairs itself. Corresponds to PR 7-9.

**Independent Test**: Provide ambiguous tasks with dependencies and observe cascade to a larger model if the small model fails.

### Implementation for User Story 3 (PR 7 - 9)

- [x] T031 [US3] Implement LLM task and day plan output schemas in `backend/app/ai/handlers/planner.py`
- [x] T032 [US3] Implement parser-to-LLM cascade and retry loop in `backend/app/ai/handlers/planner.py`
- [x] T033 [US3] Implement dynamic token usage querying and mode switching (NORMAL/LEAN/RULES_ONLY) in `backend/app/ai/budget.py`
- [x] T034 [P] [US3] Add degraded mode banner component in `frontend/src/lib/features/mr-bloom/components/molecules/DegradedBanner.svelte`
- [x] T035 [US3] Implement clarification question generation for missing data in `backend/app/ai/handlers/clarify.py`
- [x] T036 [US3] Implement atomic goal and milestone creation in `backend/app/services/goals_service.py`
- [x] T037 [US3] Write cascade tests in `backend/tests/unit/test_cascade.py`

**Checkpoint**: All core planning user stories should now be independently functional.

---

## Phase 6: User Story 4 - Editing, Persistence & Actions (Priority: P4)

**Goal**: Patch editor, session persistence, and mood handlers. Corresponds to PR 10-12.

**Independent Test**: Change a task using manual text commands, verifying the patch applies without regenerating the draft.

### Implementation for User Story 4 (PR 10 - 12)

- [x] T038 [US4] Implement `PatchOp` schemas and `apply_patch` endpoint in `backend/app/ai/patches.py`
- [x] T039 [US4] Implement deterministic editor rules in `backend/app/ai/editor_rules.py`
- [x] T040 [US4] Implement LLM editor fallback in `backend/app/ai/handlers/editor.py`
- [x] T041 [US4] Modify `backend/app/api/routes/assistant.py` to persist interactions to `planning_sessions` and `planning_messages`
- [x] T042 [P] [US4] Implement mood handlers and crisis detection in `backend/app/ai/handlers/mood.py`
- [x] T043 [US4] Implement whitelist actions endpoint `POST /assistant/actions/{name}` in `backend/app/api/routes/assistant.py`
- [x] T044 [US4] Write patch application tests in `backend/tests/unit/test_patches.py`

---

## Phase 7: User Story 5 - Calibration & Proactive Nudges (Priority: P5)

**Goal**: Historical duration calibration and proactive desktop nudges. Corresponds to PR 13-14.

**Independent Test**: Complete tasks and observe median duration adjusts. Trigger a "NEED_MORE_TIME" Pomodoro event to verify proactive nudges.

### Implementation for User Story 5 (PR 13 - 14)

- [x] T045 [US5] Implement historical calibration query logic in `backend/app/ai/calibration.py`
- [x] T046 [US5] Apply calibration multipliers to AI-estimated task durations in `backend/app/ai/drafts.py`
- [x] T047 [P] [US5] Implement proactive event nudges (e.g., Pomodoro triggers) in `backend/app/ai/proactive.py`
- [x] T048 [P] [US5] Update Tauri `emitTo` handlers for cross-window deduplication in `frontend/src/lib/platform/desktopWindow.ts`
- [x] T049 [US5] Write calibration logic tests in `backend/tests/unit/test_calibration.py`

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T050 [P] Write `scripts/eval_chat.py` for explicitly opted-in Groq evaluation against 30 test prompts
- [ ] T051 Run complete quickstart.md manual validation (Ollama, RULES_ONLY)
- [x] T052 Verify database usage logs contain no private text data

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - Sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### Parallel Opportunities

- Tests and linting tasks in Setup can run in parallel.
- Frontend UI fixes (T014-T016) can run in parallel with backend provider work (T010-T013).
- Adding UI banners (T034) can be done in parallel with backend logic (T033).
- Proactive event-driven nudge logic on desktop (T048) can be developed independently of the backend.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready
