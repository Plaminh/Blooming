# Research & Architecture Decisions: Refactor Today into an Execution-Only Dashboard

**Feature**: `028-today-execution-dashboard`  
**Date**: 2026-09-26  

---

## 1. Context Handoff from Today to Mr. Bloom

### Decision
Today will navigate to Mr. Bloom passing query parameters for plan date and (optional) selected task ID:
`/mr-bloom?date=${encodeURIComponent(planDate)}&taskId=${encodeURIComponent(taskId)}`

When Mr. Bloom opens with `date` in query parameters:
1. If an active draft matching that date already exists in `mrBloomStore`, keep it.
2. If no draft exists or the draft belongs to another date, fetch the confirmed plan directly as a lossless draft (`GET /today/draft?date=${date}`).
3. Set `activeDraft` to the generated `TodayDraft` and set `previewMode` to `'today'`. If `taskId` was passed, highlight or select that task in the draft preview.
4. In Mr. Bloom, any user edits (via draft editor buttons or natural language chat) apply patches to `TodayDraft`, immediately resetting `preview: null`. To save, the user generates a timeline preview (validated deterministically by `/today/preview` and the scheduler), reviews it, and clicks "SAVE", which calls `/today/save` with `replace_existing: false` (to trigger the 409 conflict canonical confirmation), then `replace_existing: true` and navigates back to `/today?date=${date}`.

### Rationale
- Reuses the existing `TodayDraft`, `applyPatch`, `previewTodayPlan`, and `saveTodayPlan` architecture already implemented and tested in Mr. Bloom.
- Preserves the core invariant: **"Code validates, Scheduler decides, User saves."**
- Guarantees zero unvalidated manual mutations to the persisted schedule.
- Cleanly separates Today (read-only execution dashboard) from Mr. Bloom (authoring, conversational guidance, structural plan changes).

### Alternatives Considered
- *In-place modal in Today*: Rejected because editing schedule structure requires full scheduler validation, reality checks, and potentially assistant trade-off suggestions, which already live natively in Mr. Bloom's workspace.
- *Separate dedicated edit screen*: Rejected as unnecessary duplication; Mr. Bloom is the designated planner and coach for Blooming.

---

## 2. Right Rail Layout & Execution Actions

### Decision
Refactor `RightRail.svelte` to be completely read-only for metadata while exposing execution actions:
1. **Remove**:
   - `isEditing` state, `startEditing()`, `handleSave()`
   - Pencil icon edit toggle in header
   - Title input, duration input, category dropdown, notes textarea
   - Save / Cancel buttons
2. **Display as Static Read-Only**:
   - Task icon and title
   - Scheduled start/end time and duration string
   - Description / notes (or "No description")
   - Category badge (e.g. Learning, Work, Personal, Uncategorized)
   - Task status badge (Upcoming, In-Progress, Completed)
3. **Execution & Navigation Actions**:
   - **START FOCUS**: Retain preset selector (25/5, 50/10, Custom) and "START FOCUS" button. (Disabled if completed or break).
   - **MARK COMPLETE**: Add explicit button calling `PATCH /today/tasks/{task_id}/status` with `{ status: "COMPLETED" }`. Awards Leaves via ledger, marks completed, emits `desktop.scheduleUpdated()`. (Disabled if already completed or break).
   - **ADJUST WITH MR. BLOOM**: Secondary button transitioning to `/mr-bloom?date=${currentDate}&taskId=${task.task_id}` for structural edits.

### Rationale
- Satisfies FR-006, FR-007, FR-008.
- Keeps execution fast and tactile: a user can complete a task or launch a focus timer without leaving Today.
- Eliminates any possibility of unvalidated duration or category drift.

### Alternatives Considered
- *Checkboxes directly on the timeline card*: Kept timeline cards clean and focused on schedule geometry and status badges; Right Rail provides the primary inspected execution action area with clear feedback.

---

## 3. Bottom Actions & Quick Replan

### Decision
Refactor `BottomActions.svelte`:
1. Remove `EDIT MANUALLY` button.
2. Add `QUICK REPLAN` button:
   - Triggers `onQuickReplan`, which calls `POST /today/replan?target_date=YYYY-MM-DD`.
   - The backend deterministic scheduler shifts remaining unfinished tasks relative to the current time.
   - Refreshes the local schedule and updates timeline geometry.
3. Keep `ADJUST WITH MR. BLOOM` (formerly "REPLAN WITH MR. BLOOM"):
   - Triggers `onReplan`, which navigates to `/mr-bloom?date=${currentDate}` for structural alterations.

### Rationale
- Clarifies the conceptual boundary:
  - **Quick Replan**: Deterministic rearrangement of *existing* tasks for the current day. No chat needed.
  - **Adjust with Mr. Bloom**: Structural addition, removal, or modification of task definitions and constraints.

---

## 4. Frontend API & Backend Endpoint Audit

### Callers & Usage Audit Findings
- `PATCH /today/tasks/{task_id}`:
  - Frontend callers: Only `frontend/src/routes/(app)/today/+page.svelte` (`handleSaveTask`).
  - Backend callers: Only route handler in `backend/app/api/routes/today.py`. Not called by Mr. Bloom, Focus, Reminders, or Widget.
  - Tests: No direct calls in backend tests.
  - **Decision**: Keep endpoint intact in backend for backward compatibility and test stability. Remove only the unused frontend call in `today/+page.svelte` once the UI edit mode is removed.
- `DELETE /today/tasks/{task_id}`:
  - Does NOT exist under `/today`. (Only `DELETE /planning/tasks/{task_id}` exists for planning sessions).
  - No action needed.
- `PATCH /today/tasks/{task_id}/status`:
  - Implemented in `backend/app/api/routes/today.py` and `today_service.py`.
  - Already handles idempotent completion, timestamp recording, and awarding Leaves (`award_resources(..., leaves=LEAVES_PER_TASK)`).
  - **Decision**: Wire directly to the new "MARK COMPLETE" action on Today.
- `POST /today/replan?target_date=YYYY-MM-DD`:
  - Implemented in `backend/app/api/routes/today.py` and `today_service.py`.
  - **Decision**: Wire directly to the "QUICK REPLAN" action in `BottomActions.svelte`.

---

## 5. Skip Behavior Audit

### Findings
- Standalone skip without replanning does NOT exist on the Today screen.
- In Focus/Widget, concluding a session with outcome `SKIP` triggers `today_service.replan_today(db, user_id)` (or `POST /today/replan?target_date=YYYY-MM-DD`), ensuring future blocks are dynamically realigned.
- **Decision**: Do not introduce any standalone skip button to Today. All skips remain tied to focus outcomes and automatic deterministic replanning.
