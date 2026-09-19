---
description: "Task list template for feature implementation"
---

# Tasks: 023-planning-assistant-workflow

**Input**: Design documents from `/specs/023-planning-assistant-workflow/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Tests are required where mandated by the Constitution or feature specification. Every user story still requires an independently verifiable acceptance method.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Foundational (Backend Contracts)

**Purpose**: Core infrastructure and schema updates that MUST be complete before ANY user story can be implemented.

- [x] T001 [P] Schema Updates: Add `session_id`, `current_draft`, `intent`, `missing_fields` to `ChatRequest` and `ChatResponse` in `backend/app/schemas/assistant.py`. Expected: Support context-aware chat schema. Tests: N/A. Completion: Schema compiles.
- [x] T002 [P] Schema Updates: Add `POST /today/preview` and `POST /today/save` request/response schemas to `backend/app/schemas/today.py`. Expected: Accepts availability and tasks, returns schedule result. Tests: N/A. Completion: Schema compiles.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 2: User Story 1 - Preview and Save Today Plan (Priority: P1) 🎯 MVP

**Goal**: Replace frontend fake timeline with a deterministic backend preview and atomic save.
**Independent Test**: Generate a timeline and verify the UI accurately renders backend blocks, then save and verify DB records.

### Implementation for User Story 1

- [x] T003 [US1] Backend Scheduler: Extract scheduler logic in `backend/app/core/scheduler.py` to ensure it works entirely in-memory without DB queries. Expected: Scheduler takes `AvailabilityDraft` and `TaskDraft` lists and returns pure data blocks. Tests: Add test in `backend/tests/api/test_scheduler.py`. Completion: Pure function available.
- [x] T004 [US1] Backend API: Implement `POST /today/preview` in `backend/app/api/routes/today.py` and `backend/app/services/today_service.py` calling the pure scheduler. Expected: Validates draft, returns blocks without DB inserts. Tests: `test_today_preview` in `backend/tests/api/test_today.py`. Completion: Endpoint returns blocks.
- [x] T005 [US1] Backend API: Implement `POST /today/save` in `backend/app/api/routes/today.py` and `backend/app/services/today_service.py`. Expected: Atomically persists a validated Today draft as a DailyPlan and Tasks in one transaction. Tests: `test_today_save` in `backend/tests/api/test_today.py`. Completion: Atomic transaction works.
- [x] T006 [US1] Frontend Integration: Update `frontend/src/lib/api.ts` to add `previewTodayPlan` and `saveTodayPlan` typed API methods. Expected: Methods correctly map frontend types to backend schemas. Tests: N/A. Completion: Methods exist.
- [ ] T007 [US1] Frontend Store: Remove local fake timeline logic in `frontend/src/lib/features/mr-bloom/components/organisms/TimelineDraftPreview.svelte` (which builds entries dynamically with hardcoded breaks/buffer messages) and `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts` ("GENERATE TIMELINE", "SAVE TO TODAY"). Update the frontend to call `previewTodayPlan` to fetch and render the real deterministic backend blocks, and `saveTodayPlan` to atomically persist them. Tests: Update component tests. Completion: Fake frontend timeline generation completely replaced by API data.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 3: User Story 2 - Context-Aware Chat and Validation (Priority: P1)

**Goal**: Enable conversational editing of drafts with strict backend validation.
**Independent Test**: Ask the assistant to modify a draft and verify the backend enforces constraints before returning.

### Implementation for User Story 2

- [ ] T008 [US2] Backend Validation: Implement strict draft validation logic (time format, positive durations, max 15 tasks) in `backend/app/services/assistant_service.py`. Expected: Bad drafts from LLM are caught and repaired/rejected. Tests: `test_draft_validation`. Completion: Validator catches bad LLM output.
- [ ] T009 [US2] Backend Assistant: Update `assistant_chat` endpoint in `backend/app/api/routes/assistant.py` and `backend/app/services/assistant_service.py` to pass `session_id` and `current_draft` to the LLM. Add local timezone context (date/time) to `SYSTEM_PROMPT`. Expected: LLM receives context and edits draft. Tests: `test_chat_context`. Completion: Endpoint updated.
- [ ] T010 [US2] Frontend Integration: Update `ChatComposer.svelte` and `mrBloomStore.ts` in `frontend/src/lib/features/mr-bloom/` to send the current draft state and session ID on each message. Expected: Chat updates existing draft instead of creating new ones. Tests: Update store tests. Completion: Payload includes `current_draft`.

**Checkpoint**: User Stories 1 AND 2 should both work independently.

---

## Phase 4: User Story 3 - Persistence of Planning Sessions (Priority: P2)

**Goal**: Restore conversation history and draft state securely across page reloads.
**Independent Test**: Start a chat, refresh the page, and verify the conversation and draft are completely restored.

### Implementation for User Story 3

- [ ] T011 [P] [US3] Backend Session Store: Implement session retrieval `GET /assistant/sessions/{session_id}` in `backend/app/api/routes/assistant.py`. Expected: Returns messages and latest draft. Tests: `test_get_session`. Completion: Endpoint exists.
- [ ] T012 [US3] Backend Session Update: Update `assistant_chat` in `backend/app/api/routes/assistant.py` to persist user and assistant messages to the `PlanningMessage` table and manage `PlanningSession`. Expected: Conversation saved. Tests: `test_persist_chat`. Completion: Messages save properly.
- [ ] T013 [US3] Frontend Restore: Update `mrBloomStore.ts` to fetch the active session on load. Expected: Page refresh restores chat history without manual state loss. Tests: Update store tests. Completion: Refresh works seamlessly.

---

## Phase 5: User Story 4 - Atomic Roadmap Creation and Reliability (Priority: P2)

**Goal**: Ensure Goal and Milestones are saved atomically without leaving orphaned records on failure.
**Independent Test**: Trigger a milestone failure during roadmap save and verify no Goal is left behind in the DB.

### Implementation for User Story 4

- [ ] T014 [US4] Backend API: Refactor roadmap save in `backend/app/api/routes/goals.py` (and `goals_service.py`) to ensure Goal and Milestones are created in a single `db.begin()` transaction block. Expected: Atomic failure rolls back both. Tests: `test_atomic_roadmap_rollback`. Completion: Rollback verified.
- [ ] T015 [US4] Backend API: Enforce YYYY-MM-DD strict parsing for roadmap dates in `backend/app/schemas/goals.py` and `app.core.time_utils`. Expected: No timezone shifts on save. Tests: `test_strict_date_parsing`. Completion: Date format robust.

---

## Phase 6: User Story 5 - Provider Reliability and Scope Protection (Priority: P3)

**Goal**: Protect the assistant from off-topic queries and transient provider errors (Streaming/fallback are lower priority).
**Independent Test**: Ask an unrelated question and verify a polite refusal. Simulate a 429 error and verify it retries.

### Implementation for User Story 5

- [ ] T016 [P] [US5] Backend Provider: Add retry logic (e.g., using `tenacity`) to `httpx.AsyncClient` in `backend/app/services/assistant_service.py`. Expected: 429/5xx errors retry up to 3 times before failing gracefully. Tests: `test_provider_retry`. Completion: Retries handle transient errors.
- [ ] T017 [US5] Backend Assistant: Add explicit scope guard instructions and an `out_of_scope` intent to `SYSTEM_PROMPT` in `backend/app/services/assistant_service.py`. Expected: Unrelated questions rejected politely. Tests: `test_scope_guard`. Completion: Assistant stays on topic.

---

## Phase 7: User Story 6 - Improved UX and Accessibility (Priority: P3)

**Goal**: Provide a professional, accessible, and robust chat interface.
**Independent Test**: Use a screen reader to hear updates; test IME composition and Shift+Enter behavior.

### Implementation for User Story 6

- [ ] T018 [P] [US6] Frontend UX: Update `ChatComposer.svelte` to prevent Enter on IME composition (`isComposing`), use `textarea`, support Shift+Enter for newline, and auto-scroll. Expected: Natural chat input behavior. Tests: Component interaction tests. Completion: Input behaves like standard messengers.
- [ ] T019 [P] [US6] Frontend UX: Add `aria-live` regions and loading states (disabling submit/save buttons) in `MrBloomConversationPanel.svelte` and `TodayTimeline.svelte`. Expected: Screen readers announce updates, double submits blocked. Tests: Accessibility checks. Completion: Accessibility improved.
- [ ] T020 [P] [US6] Dataset: Create an evaluation dataset in `backend/tests/eval_dataset.json` with 20 bilingual utterances (English/Vietnamese) focusing on dates, durations, and conflicts. Expected: Covers edge cases, date resolution. Completion: Dataset ready for manual/automated evaluation.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 1)**: Must be completed first as it establishes the API contracts.
- **User Stories (Phases 2-7)**: Once Phase 1 is done, Phase 2 (US1) is blocking for Phase 3 (US2). US3, US4, US5, and US6 can largely proceed in parallel once Phase 1 is complete.
- **Execution Order**: P1 (US1, US2) → P2 (US3, US4) → P3 (US5, US6)

### Parallel Opportunities

- Foundational schema updates (T001, T002) can be done in parallel.
- Once US1/US2 are complete, the UX updates (T018, T019) and Dataset creation (T020) can proceed entirely in parallel.
- Session endpoints (T011) and Roadmap fix (T014) have no direct dependency on the today preview and can be worked on concurrently by a separate agent/developer.
