# Implementation Plan: Refactor Today into an Execution-Only Dashboard

**Branch**: `028-today-execution-dashboard` | **Date**: 2026-09-26 | **Spec**: [specs/028-today-execution-dashboard/spec.md](spec.md)

**Input**: Feature specification from `specs/028-today-execution-dashboard/spec.md`

---

## Summary

This plan defines the smallest safe refactor to transform the `/today` screen into a strict, read-only execution dashboard. Today will exclusively handle schedule inspection, date navigation, focus execution, task completion, and deterministic quick replanning. All structural plan modifications (creating, removing, reordering tasks, altering durations, editing metadata, or changing availability) are removed from Today and delegated cleanly to Mr. Bloom via context handoff. The deterministic scheduler remains the sole authority for timeline geometry and preview tokens.

---

## Technical Context

- **Language/Version**: TypeScript 5.x (Frontend), Python 3.11 (Backend)
- **Primary Dependencies**: SvelteKit 2 / Svelte 5 (Frontend), FastAPI / Pydantic v2 (Backend), SQLAlchemy 2.0 (ORM)
- **Storage**: PostgreSQL (persisting `daily_plans`, `plan_blocks`, `tasks`, `plan_revisions`, `reward_events`)
- **Testing**: Vitest + `@testing-library/svelte` (Frontend), pytest + pytest-asyncio (Backend)
- **Target Platform**: Desktop (Tauri 2 on Windows/Linux)
- **Project Type**: Desktop UI + Local Backend Modular Monolith
- **Performance Goals**: Schedule inspection and UI tab transitions < 50ms; Quick Replan scheduler roundtrip < 200ms
- **Constraints**: No unvalidated plan mutations; zero schema drift; no orphaned skip gaps; maintain backward compatibility for existing endpoints

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Does the plan align with the Spec-driven development workflow? *(Yes: specify → plan → tasks → implement → verify).*
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite, FastAPI/Python/Pydantic, and PostgreSQL/SQLAlchemy boundaries? *(Yes).*
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries? *(Yes: scheduler validates all timeline generation; user explicitly confirms save).*
- [x] Are explicit contracts and type safety boundaries defined? *(Yes: contracts created in `contracts/`).*
- [x] Is the proposed implementation the simplest that satisfies the spec? *(Yes: reuses existing Mr. Bloom draft editing flow, removes manual form code from Today).*
- [x] Are testable behavior and quality gates defined? *(Yes: component, integration, and manual test cases updated).*
- [x] Does the UX handle loading, partial, and failure states gracefully? *(Yes: empty state, network errors, and unscheduled task warnings preserved).*
- [x] Are resource efficiency and platform scope strictly followed? *(Yes: lightweight UI changes, no new background daemons).*
- [x] Are security and privacy principles respected? *(Yes: user ownership and tenant isolation preserved).*

---

## Project Structure

### Documentation (this feature)

```text
specs/028-today-execution-dashboard/
├── plan.md              # This file
├── research.md          # Phase 0 architectural findings and caller audit
├── data-model.md        # Phase 1 entities, mutation classification, state transitions
├── quickstart.md        # Phase 1 runnable verification guide
├── contracts/           # Phase 1 interface contracts
│   ├── today-ui-actions.md
│   ├── mr-bloom-handoff.md
│   └── today-api.md
└── checklists/
    └── requirements.md
```

### Source Code Impact Areas

```text
frontend/src/
├── lib/
│   ├── api/
│   │   └── types.ts                                             # Deprecate TodayTaskEdit usage
│   └── features/
│       ├── mr-bloom/
│       │   └── stores/
│       │       └── mrBloomStore.ts                              # Handle ?date=&taskId= handoff from Today
│       └── today/
│           ├── types.ts                                         # Update Today props & task actions
│           ├── components/
│           │   ├── organisms/
│           │   │   ├── RightRail.svelte                         # Read-only task details + Start Focus + Mark Complete + Adjust
│           │   │   ├── RightRail.test.ts                        # New unit test for read-only RightRail
│           │   │   ├── BottomActions.svelte                     # Quick Replan + Adjust with Mr. Bloom (no Edit Manually)
│           │   │   └── BottomActions.test.ts                    # New unit test for BottomActions
│           │   └── molecules/
│           │       └── TimelineCard.svelte                      # Preserved read-only card
│           └── TodayView.test.ts                                # Update component tests
└── routes/
    └── (app)/
        ├── today/
        │   └── +page.svelte                                     # Remove edit handlers, wire Mark Complete & Quick Replan
        └── mr-bloom/
            └── +page.svelte                                     # Verify param handoff

docs/testing/
└── Blooming-Manual-Test-Scenarios.md                            # Update TODAY-UI-03 to read-only; add Adjust Plan scenario
```

---

## Detailed Workstreams

### 1. Frontend Today UI Cleanup
- **RightRail.svelte**:
  - Delete `isEditing` state, `startEditing()`, `handleSave()`, and local input state (`editTitle`, `editDuration`, `editCategory`, `editDescription`).
  - Remove pencil icon edit toggle in `<header class="panel-strip">`.
  - Remove all inline inputs (`<input>`, `<select class="category-select">`, `<textarea class="notes-textarea">`).
  - Render title, duration, time window, description, and category strictly as read-only labels/badges.
  - Remove direct Delete controls (confirming none exist or can be accessed).
- **BottomActions.svelte**:
  - Remove the `"EDIT MANUALLY"` button and its associated `onEdit` prop.
  - Add `"QUICK REPLAN"` button (calls `onQuickReplan`).
  - Rename `"REPLAN WITH MR. BLOOM"` button to `"ADJUST WITH MR. BLOOM"` (calls `onAdjustWithMrBloom`).
- **today/+page.svelte**:
  - Remove `rail?.startEditing()` invocation.
  - Remove `handleSaveTask` and any imports of `TodayTaskEdit`.
  - Pass read-only and execution callbacks to `RightRail` and `BottomActions`.

### 2. Execution Actions Preservation & Enhancement
- **Start Focus**:
  - Retain `onStartFocus` in `RightRail` with preset options (25/5, 50/10, Custom).
  - Preserve `desktop.scheduleUpdated()` and widget activation synchronization.
- **Mark Complete**:
  - Add `"MARK COMPLETE"` button to `RightRail.svelte`.
  - In `today/+page.svelte`, implement `handleMarkComplete(taskId: string)`:
    - Calls `api.patch('/today/tasks/' + taskId + '/status', { status: 'COMPLETED' })`.
    - Updates local block/task status in `tasks` array to `completed`.
    - Triggers `desktop.scheduleUpdated()`.
    - Awards Leaves automatically via existing backend service logic.
    - Button disabled if task is already completed or block is a break.
- **Quick Replan**:
  - In `today/+page.svelte`, implement `handleQuickReplan()`:
    - Calls `api.post('/today/replan')`.
    - Refreshes schedule data via `applySchedule(data)`.
    - Displays unscheduled task warning banner if any tasks no longer fit.
    - Preserves plan revision history.
- **Date Navigation & Timeline Rendering**:
  - Retain `handleDateChange` and date header rendering unchanged.

### 3. Adjust with Mr. Bloom Context Handoff
- In `today/+page.svelte`:
  - When user clicks `"ADJUST WITH MR. BLOOM"` from Right Rail: navigate to `/mr-bloom?date=${planDate}&taskId=${selectedTask.task_id}`.
  - When user clicks `"ADJUST WITH MR. BLOOM"` from Bottom Actions: navigate to `/mr-bloom?date=${planDate}`.
- In `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts`:
  - On page load / store initialization, check URL search params:
    - If `date` is present and differs from current active draft:
      - Call `api.get('/today/draft?date=' + date)` to fetch confirmed plan directly as a lossless draft.
      - Convert plan blocks into `TodayDraft` with `tasks` and `availability`.
      - Set `activeDraft` in `mrBloomStore` with `previewMode: 'today'` and `preview: null`.
    - If `taskId` is present, store as active focused task in the draft preview.
  - Reuses the existing Mr. Bloom flow: editing the draft invalidates previous preview → user clicks "Generate Timeline" → scheduler issues preview token → user clicks "SAVE" → plan updates and redirects back to `/today`.

### 4. Frontend API Cleanup
- `TodayTaskEdit`: Mark deprecated in `frontend/src/lib/api/types.ts`.
- Remove `api.patch('/today/tasks/' + id, updates)` from `today/+page.svelte`.
- Ensure `api.patch('/today/tasks/' + id + '/status', { status: 'COMPLETED' })` and `api.post('/today/replan')` are cleanly typed.

### 5. Backend Impact & Endpoint Maintenance
- Keep `PATCH /today/tasks/{task_id}` intact in `backend/app/api/routes/today.py` for backward compatibility. (Audit confirmed no external callers in app; keep for test safety).
- Confirm `DELETE /today/tasks/{task_id}` does not exist (no action needed).
- Verify `PATCH /today/tasks/{task_id}/status` and `POST /today/replan?target_date=YYYY-MM-DD` are fully covered and operational.
- Zero changes to the scheduler algorithm (`DeterministicScheduler`).

### 6. Skip Behavior Verification
- Confirm that no standalone "Skip" button exists on Today.
- Any skip outcome remains strictly attached to focus session completion (via Widget or Focus run) which immediately triggers replanning via `today_service.replan_today`, preventing timeline gaps.

### 7. Automated Test Plan
- **New Tests**:
  - `RightRail.test.ts`: Verify read-only rendering, absence of inputs/edit toggle, presence of Start Focus, Mark Complete, and Adjust with Mr. Bloom.
  - `BottomActions.test.ts`: Verify absence of Edit Manually, presence of Quick Replan and Adjust with Mr. Bloom.
- **Updated Tests**:
  - `TodayView.test.ts`:
    - Remove tests asserting edit mode or `handleSaveTask`.
    - Add tests for `Mark Complete` execution mutation.
    - Add tests for `Quick Replan` action.
    - Add tests for navigation to `/mr-bloom` with date and taskId.
- **Regression Tests**:
  - Run all `src/lib/features/today/` and `src/lib/features/mr-bloom/` tests to ensure zero breakages.

### 8. Manual Test Suite Updates
- In `docs/testing/Blooming-Manual-Test-Scenarios.md`:
  - Update `TODAY-UI-03`: Rename from "Edit Task Metadata Directly from Today Right Rail" to "TODAY-UI-03 — Today Task Details Are Read-Only".
  - Add scenario: "Adjust Existing Plan with Mr. Bloom".

---

## Implementation Order

1. **Step 1 - Test Scaffolding**: Create unit tests defining the new read-only contract (`RightRail.test.ts`, `BottomActions.test.ts`).
2. **Step 2 - BottomActions Refactoring**: Remove "Edit Manually", add "Quick Replan" and "Adjust with Mr. Bloom".
3. **Step 3 - RightRail Refactoring**: Remove edit state and form inputs; make task details read-only; add "Mark Complete" and "Adjust with Mr. Bloom".
4. **Step 4 - Today Page Wiring**: Wire `handleMarkComplete` and `handleQuickReplan` in `today/+page.svelte`; remove `handleSaveTask`.
5. **Step 5 - Mr. Bloom Handoff**: Enhance `mrBloomStore` to initialize `TodayDraft` from `/today?date=...` when routed with adjustment params.
6. **Step 6 - Dead Code Removal**: Clean up unused props, imports, and handlers in frontend Today feature.
7. **Step 7 - Automated Test Suite Execution**: Run Vitest on `today` and `mr-bloom`; fix any regressions.
8. **Step 8 - Manual Test Documentation Update**: Update `docs/testing/Blooming-Manual-Test-Scenarios.md`.
9. **Step 9 - End-to-End Verification**: Verify full user flow from Today to Mr. Bloom and back.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Users want to tweak a typo without opening Mr. Bloom | Low/Medium | Clarify UI messaging: Mr. Bloom is the intelligent co-planner; opening Mr. Bloom takes 1 click and maintains schedule integrity. |
| Stale preview when adjusting plan in Mr. Bloom | High | `mrBloomStore.applyPatch` automatically sets `preview: null`, forcing fresh scheduler timeline generation before save. |
| Existing tasks losing IDs when edited in Mr. Bloom | High | `TaskDraft` preserves `sourceTaskId` when converted from `TodayBlock`, ensuring the backend updates existing tasks rather than re-creating them. |
| Backend breaking due to premature endpoint deletion | Medium | Endpoints `PATCH /today/tasks/{task_id}` are preserved in backend code; only the frontend caller is removed. |
