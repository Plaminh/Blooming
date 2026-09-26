# Quickstart Validation Guide: Today Execution-Only Dashboard

**Feature**: `028-today-execution-dashboard`  
**Date**: 2026-09-26  

This guide provides runnable scenarios to verify that the Today dashboard is strictly execution-only, read-only for metadata, and correctly delegates structural plan modifications to Mr. Bloom.

---

## Prerequisites & Setup

1. **Backend Running**:
   ```bash
   npm run dev:backend
   ```
2. **Frontend Running**:
   ```bash
   npm run dev:frontend
   ```
3. **Database Seeded**: Ensure a user account exists with a confirmed plan for today containing at least 2 tasks.

---

## Automated Verification Commands

Run frontend unit & component tests covering Today and Mr. Bloom:

```bash
# In frontend directory
npm test -- src/lib/features/today/
npm test -- src/lib/features/mr-bloom/
```

Run backend contract and security tests:

```bash
# In backend directory
pytest tests/api/test_today_routes.py tests/unit/test_today_service.py
```

---

## Manual Verification Scenarios

### Scenario 1: Read-Only Inspection of Scheduled Tasks
1. Navigate to `/today`.
2. Click on a scheduled task block in the timeline.
3. **Verify**:
   - The Right Rail opens showing the task's title, duration, time window, category, and notes.
   - All fields are plain text (no `<input>`, no `<select>`, no `<textarea>`).
   - The header has no edit toggle (pencil icon), Save, or Cancel buttons.
   - The bottom action area has no "EDIT MANUALLY" button.

### Scenario 2: Executing Work — Start Focus & Mark Complete
1. Select an upcoming task in the Right Rail.
2. Select a focus preset (e.g., `25/5`) and click `"START FOCUS"`.
3. **Verify**: Focus session begins, task badge changes to `in-progress`, desktop widget updates.
4. Select another task and click `"MARK COMPLETE"`.
5. **Verify**:
   - Task transitions to `completed` with a checkmark badge.
   - The Leaf balance increments by 1.
   - Subsequent clicks on the completed task show disabled focus/complete buttons.

### Scenario 3: Quick Replan for Real-World Delays
1. On an active day with uncompleted tasks, click `"QUICK REPLAN"` in Bottom Actions.
2. **Verify**:
   - Deterministic scheduler recalculates the remaining blocks starting from current time.
   - Timeline cards adjust their vertical positions dynamically without navigating away or asking chat questions.

### Scenario 4: Adjusting Plan Structure via Mr. Bloom
1. Select a task in the Right Rail.
2. Click `"ADJUST WITH MR. BLOOM"` (or click `"ADJUST WITH MR. BLOOM"` in Bottom Actions).
3. **Verify**:
   - App navigates to `/mr-bloom?date=...&taskId=...`.
   - Mr. Bloom loads the current plan as an editable `TodayDraft`.
   - Editing task duration or removing a task invalidates the previous timeline preview.
   - User clicks `"Generate Timeline"` (or asks Mr. Bloom) → deterministic scheduler issues a fresh preview.
   - User clicks `"SAVE"` → plan is persisted, and app redirects to `/today` displaying the new schedule.
