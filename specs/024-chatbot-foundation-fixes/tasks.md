# Tasks: Chatbot Foundation Fixes (Phase 0)

**Input**: Design documents from `/specs/024-chatbot-foundation-fixes/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, quickstart.md

**Organization**: Tasks are organized into the 10 phases defined in the implementation plan.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are exact repository paths.

---

## Phase 1: Baseline and Safety

**Purpose**: Establish a stable baseline before implementation.

- [X] T001 Run and record existing backend tests using `pytest backend/tests`
- [X] T002 Run and record existing frontend tests using `npm run test -- run` in `frontend`
- [X] T003 [P] Run backend lint and type-check using `ruff check backend/app` and `mypy backend/app`
- [X] T004 [P] Run frontend check using `npm run check` in `frontend`
- [X] T005 [P] Inspect the working tree using `git status` to verify no uncommitted changes
- [X] T006 [P] Verify `.env.example` in the repository root contains placeholders only and no real credentials

---

## Phase 2: Canonical Draft Schemas

**Purpose**: Eliminate circular imports and establish canonical schema ownership.

- [x] T007 [US3] Create canonical draft schema module in `backend/app/schemas/drafts.py` and move `MilestoneDraft`, `RoadmapDraft`, `AvailabilityWindowDraft`, `ChatTaskDraft`, `TaskDraft`, `ChatTodayDraft`, and `TodayDraft` from `backend/app/schemas/assistant.py`
- [x] T008 [US3] Update schema imports in `backend/app/schemas/assistant.py` to import from `backend/app/schemas/drafts.py`
- [x] T009 [US3] Update schema imports in `backend/app/schemas/today.py` to import `TodayDraft` from `backend/app/schemas/drafts.py`
- [x] T010 [US3] Update test imports in `backend/tests/unit/test_assistant_schemas.py` and `backend/tests/unit/test_assistant_service.py` to use `drafts.py` where necessary
- [x] T011 [US3] Run focused schema and import tests using `pytest backend/tests/unit/test_assistant_schemas.py`

---

## Phase 3: AI Configuration and Shared LLM Client

**Purpose**: Safely configure the AI client and manage its lifecycle.

- [x] T012 [US1] Add `GROQ_BASE_URL`, `GROQ_MODEL_PLANNER`, `GROQ_MODEL_ROUTER`, `GROQ_MODEL_CHITCHAT`, `AI_TIMEOUT_SECONDS`, and `AI_CHAT_RATE_LIMIT_PER_MIN` to `Settings` in `backend/app/core/config.py`
- [X] T013 [US1] Update `.env.example` to include the new AI settings with safe placeholders
- [x] T014 [US1] Refactor `backend/app/services/assistant_service.py` to use a module-level `httpx.AsyncClient` that reads from `settings.GROQ_BASE_URL` and `settings.AI_TIMEOUT_SECONDS`
- [x] T015 [US1] Update `lifespan` in `backend/app/main.py` to initialize and cleanly close the shared `httpx.AsyncClient` from `assistant_service.py`
- [x] T016 [US1] Modify LLM payload in `backend/app/services/assistant_service.py` to use `max_completion_tokens` and add `response_format: {"type": "json_schema", ...}` if `settings.GROQ_MODEL_PLANNER` supports strict mode
- [x] T017 [US1] Ensure `reasoning_effort` is sent in `backend/app/services/assistant_service.py` only if the model is `openai/gpt-oss-*` or equivalent
- [x] T018 [US1] Implement safe operational logging in `backend/app/services/assistant_service.py` without logging API keys, prompts, user messages, or full model output
- [x] T019 [US1] Implement typed LLM errors mapping (missing API key -> 503 config, HTTP 429 -> rate_limit, Timeout -> 504 timeout, other upstream -> 502) in `backend/app/services/assistant_service.py`
- [x] T020 [US1] Add focused unit tests for request construction, error mapping, and logging in `backend/tests/unit/test_assistant_service.py`

---

## Phase 4: Per-User Chat Rate Limiting

**Purpose**: Implement isolated per-process rate limiting for chat.

- [x] T021 [US1] Implement a sliding-window rate limiter class in `backend/app/core/rate_limit.py` using monotonic time and per-user keys bounded in-memory
- [x] T022 [US1] Add rate limiter dependency to `/chat` route in `backend/app/api/routes/assistant.py`, reading `settings.AI_CHAT_RATE_LIMIT_PER_MIN` and raising HTTP 429 when exceeded
- [x] T023 [P] [US1] Add deterministic tests for expiration and isolation between users in `backend/tests/unit/test_rate_limit.py`

---

## Phase 5: Reply and Draft Validation

**Purpose**: Preserve valid LLM text replies even when structured drafts fail.

- [x] T024 [US1] Modify response parsing in `backend/app/services/assistant_service.py` to load JSON as a dictionary and extract `reply` first
- [x] T025 [US1] Implement independent validation of `draft` in `backend/app/services/assistant_service.py`. Add one draft-repair attempt loop if validation fails
- [x] T026 [US1] In `backend/app/services/assistant_service.py`, handle failure of the repair attempt by setting `draft = None` while preserving the textual `reply` and appending a clarification request
- [x] T027 [US1] Ensure the generated assistant replies in `backend/app/services/assistant_service.py` never claim the draft was successfully saved if the repair failed
- [x] T028 [US1] Update mocks and add focused tests for invalid priority, zero duration, malformed drafts, and successful/failed repair in `backend/tests/unit/test_assistant_service.py` and `backend/tests/unit/test_assistant_schemas.py` ensuring the reply always survives

---

## Phase 6: Trusted Date, Timezone, and Code-Owned Fields

**Purpose**: Enforce absolute server-side authority over time and domain bounds.

- [x] T029 [US3] Read `timezone` from persisted user settings and inject current local time into the prompt context in `backend/app/services/assistant_service.py`
- [x] T030 [US3] Remove LLM's authority to populate `timezone` by setting it deterministically in `backend/app/services/assistant_service.py` before returning the draft
- [x] T031 [US3] Assign deterministic task and milestone IDs in code in `backend/app/services/assistant_service.py` instead of passing LLM-generated IDs
- [x] T032 [US3] Add `HH:MM` validation, start/end comparison, and past-window trimming to `AvailabilityWindowDraft` or a dedicated validation function in `backend/app/schemas/drafts.py`
- [x] T033 [P] [US3] Add unit tests for timezone trust, deterministic IDs, and invalid windows in `backend/tests/unit/test_assistant_schemas.py`

---

## Phase 7: Roadmap Validation

**Purpose**: Protect roadmap data integrity from hallucinated deadlines.

- [x] T034 [US3] Add validators to `RoadmapDraft` in `backend/app/schemas/drafts.py` to enforce 1-12 milestones, target date >= today, monotonic milestone ordering, and milestones <= target date
- [x] T035 [US3] Apply safe deterministic corrections (e.g., sorting milestones chronologically) in `RoadmapDraft` validators in `backend/app/schemas/drafts.py`
- [x] T036 [P] [US3] Add focused tests for zero milestones, too many milestones, past targets, unordered milestones, and out-of-bounds milestones in `backend/tests/unit/test_assistant_schemas.py`

---

## Phase 8: Frontend Chat Fixes

**Purpose**: Fix UX glitches and correctly render server data.

- [x] T037 [US2] Update `frontend/src/lib/features/mr-bloom/components/molecules/ChatComposer.svelte` `handleKeyDown` to not submit if `e.shiftKey` or `e.isComposing` is true
- [x] T038 [US2] Add `white-space: pre-wrap;` to the `.bubble` CSS class in `frontend/src/lib/features/mr-bloom/components/molecules/ChatMessage.svelte` to preserve multiline rendering
- [x] T039 [US2] Update `mrBloomStore.ts` in `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts` to add a `status?: 'failed'` flag to `ChatMessage`
- [x] T040 [US2] Modify `submitMessage` in `mrBloomStore.ts` to exclude failed messages from outgoing history array and mark the user message as failed if the API request throws
- [x] T041 [US2] Add a retry function in `mrBloomStore.ts` that resends the failed message without appending a duplicate to the chat history
- [x] T042 [US2] Modify `createMrBloomStore` initialization in `mrBloomStore.ts` to dynamically generate the greeting and timestamp based on `new Date()` instead of hardcoded `09:00`
- [x] T043 [US2] Update date-only rendering logic in timeline or draft UI components (e.g., `TimelineHourLabel.svelte` or `PlanDraftPreview.svelte`) to preserve string format and avoid UTC shifting via `new Date('YYYY-MM-DD')`
- [x] T044 [US2] Connect or visibly disable ADD TASK and ADD MILESTONE placeholder buttons in relevant `.svelte` components (e.g. `DraftReviewActionBar.svelte`) based on current store capabilities
- [x] T045 [P] [US2] Add frontend component tests for Enter vs Shift+Enter vs Composing Enter in `frontend/src/lib/features/mr-bloom/components/molecules/ChatComposer.test.ts`
- [x] T046 [P] [US2] Add frontend store tests for failed message exclusion and retry deduplication in `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.test.ts`

---

## Phase 9: Security and Configuration Audit

**Purpose**: Ensure safe credential management.

- [X] T047 [P] Verify root and backend `.gitignore` coverage includes `.env`, `venv`, `__pycache__`, `node_modules`, test caches, and add missing rules
- [X] T048 [P] Search tracked files for likely exposed credentials (e.g. `GROQ_API_KEY`) without printing values, and report filenames requiring rotation if found
- [X] T049 [P] Confirm `backend/tests/unit/test_assistant_service.py` and `backend/app/services/assistant_service.py` logs contain no auth headers, keys, user messages, or model output

---

## Phase 10: Final Verification

**Purpose**: Confirm all requirements are met and no regressions are introduced.

- [X] T050 [P] Run unit tests using `pytest backend/tests/unit`
- [X] T051 [P] Run full backend test suite using `pytest backend/tests`
- [X] T052 [P] Run backend lint and type-check using `ruff check backend/app` and `mypy backend/app`
- [X] T053 [P] Run focused frontend tests using `npm run test -- run src/lib/features/mr-bloom`
- [X] T054 [P] Run full frontend test suite using `npm run test -- run`
- [X] T055 [P] Run frontend check using `npm run check`
- [X] T056 [P] Review `git diff` to ensure no out-of-scope files were modified
- [X] T057 [P] Review `specs/024-chatbot-foundation-fixes/spec.md` to confirm all criteria are met
- [X] T058 [P] Perform manual UI smoke test outlined in `quickstart.md` if feasible in the environment

---

## Dependencies & Execution Order

- **Phase 1** must be completed first to establish baselines.
- **Phase 2** establishes the schema architecture and blocks all backend validation features (Phases 5-7).
- **Phase 3** manages the API client, blocking **Phase 4** and **Phase 5**.
- **Phase 8** (Frontend) can be executed in parallel with backend phases.
- **Phase 9** (Audit) can run in parallel with implementation.
- **Phase 10** must be executed last.

