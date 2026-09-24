# Feature Specification: Multi-Day Plans, Recurring Tasks and Chat Stability

**Feature Directory**: `specs/026-multi-day-recurring-tasks`
**Created**: 2026-09-24
**Status**: Implemented, awaiting review

## Why

Owner-reported problems with Mr. Bloom:

1. No recurring tasks ("mỗi ngày học tiếng Anh 30 phút" became one task for today).
2. No multi-day planning ("thứ 2 …, thứ 4 …", "ngày kia", "tuần này" were all put on today).
3. Many small mistakes in understanding Vietnamese.
4. The chat sometimes froze.

## Behaviour

### Stability (freeze fixes)

| Cause | Fix |
| --- | --- |
| Discard/Save/session-restore while a reply was pending left `isWaitingForResponse` stuck, so the composer stayed disabled until reload. | `sendMessage` releases the composer even when its reply is discarded (`mrBloomStore.ts`). |
| `fetch` had no timeout. | Every request aborts after 30 s, chat after 75 s, with a readable 408 error (`api.ts`). |
| One chat turn could chain router + 3 planner models + repair, 20–30 s each. | `llm_deadline` caps all provider calls of a turn at `AI_REQUEST_BUDGET_SECONDS` (45 s). Each call's timeout shrinks to the time left, and budget-caused timeouts do not trip a model's circuit breaker (`providers.py`). |
| Replanning twice crashed (500) when the first replan left tasks unscheduled: the revision stored UUID strings, the reader called `.get()`. | `_snapshot_task_ids` reads both shapes. Replan revisions keep `created_task_ids` / `task_draft_map` (`today_service.py`). |

### Understanding fixes (router / parser / editor)

- Vietnamese keywords are matched **with accents** when the user typed accents (`accent_aware_search`). Examples: "chắc chắn" is no longer "chán" (MOOD), "uống nước" is no longer a garden question, and "chạy bộ" is no longer "bỏ".
- "Lên kế hoạch cả tuần này" plans instead of showing statistics.
- A bare hour ≥ 6 or an hour with a period ("họp 9h30", "2h chiều") is a **start time**, not a duration. "trong 8h" is still a duration.
- "2 tiếng rưỡi" = 150 min. Leftover fillers ("mình", "theo thứ tự:", "chắc chắn") are removed from titles, and "ôn" is no longer eaten as English "on".
- Editor: "nhận thêm 2 email" no longer multiplies every duration. Scaling needs "nhân 2" / "scale by 2".
- `set_plan_date` compares against the user's local date, not the server's.

### Multi-day plans

- The parser reads a day per segment: "hôm nay", "mai" / "ngày mai" / "sáng mai", "ngày kia", "thứ 2…CN" (with "tuần sau"), English weekdays, and `dd/mm[/yyyy]`.
- A day applies from where it is named onwards. A single day that closes the whole message ("… ngày mai") applies to every task.
- The earliest named day becomes the draft's `planDate`. Tasks for later days go into `deferred_tasks`.
- "Tuần này / tuần sau ôn thi 10 tiếng" is split into equal sessions (multiples of 5 min, at least 30 min) over the remaining days of that week.
- **Saving** stores later-day tasks as `PENDING` tasks with `tasks.planned_date`. It no longer creates an empty ACTIVE plan for that day, which used to block planning the day (`PLAN_EXISTS`) and to delete the task on replace.
- When the user plans that day (even with just "Lập lịch hôm nay"), the draft includes the waiting tasks (`sourceTaskId`). Saving reuses the row instead of duplicating it. Replacing a plan returns reused tasks to their day instead of deleting them.
- `GET /today` for a day without a plan returns `pending_tasks` (DEFERRED / RECURRING). "Hôm nay có gì?" mentions them. `replan_today` also picks up tasks waiting for today.
- The draft UI shows the plan date and a "Saved for other days" list with remove buttons (`remove_deferred_task` patch).

### Recurring tasks

- The parser understands "mỗi ngày / hàng ngày / every day", "hàng tuần / weekly", "mỗi thứ 2 và thứ 4 / every Monday and Wednesday", "các ngày trong tuần / weekdays", "mỗi cuối tuần", and "… trong tuần này" (repeats until Sunday).
- `TaskDraft.recurrence` (`freq`, `weekdays`, `until`) travels in the draft and is shown as a badge.
- Saving creates a `recurring_tasks` template, reusing an identical active one so that re-saving does not double future days. The saved task links to it via `tasks.recurring_task_id`.
- Planning a later day adds due occurrences automatically (`recurringTaskId`) unless one already exists for that day.
- Chat: "Việc lặp lại của tôi là gì?" lists templates. "Dừng lặp lại <tên>" deactivates one; an unclear name gets a question with one quick reply per task. Planned days are never touched.
- API: `GET /api/v1/recurring-tasks`, `PATCH /api/v1/recurring-tasks/{id}` `{is_active}`.

## Data model

- New table `recurring_tasks` (`database/tables/15a_recurring_tasks.sql`, loaded before `tasks`).
- `tasks.planned_date DATE`, `tasks.recurring_task_id UUID → recurring_tasks ON DELETE SET NULL`, plus two partial indexes.
- Existing databases: `database/migrations/04_multi_day_and_recurring_tasks.sql` (idempotent, run by `npm run db:migrate`).

## Out of scope / follow-ups

- There is no UI screen for managing recurring tasks yet (the API exists).
- Occurrences are created when a day is **planned**, not by a background job, so the Today screen of an unplanned day lists them as `pending_tasks` only.
- Frontend unit tests were written but not run in this change (no `node_modules` locally). Run `npm run check` and `npm run test` in `frontend/`.

## Verification

- `backend`: `pytest tests/unit tests/api/test_assistant_chat_contract.py` → 427 passed (includes `test_multi_day_and_fixes.py`, 55 regression cases).
- DB-backed tests (`tests/api/test_multi_day_recurring.py`, updated `test_deferred_save.py`) need Docker/PostgreSQL and were not run in this change.
