# Feature Specification: Mr. Bloom Upgrade (LLM-first multi-day, day review, chat completion)

**Feature Directory**: `specs/030-mr-bloom-upgrade`
**Created**: 2026-09-27
**Status**: Implemented, awaiting review
**Builds on**: 026 (multi-day & recurring), 027 (LLM-first planning), 028 (Today execution dashboard)

## Why

- 027 made the planner LLM-first. The LLM normalisation set `recurrence=None` and `spread=None` and used one day for every task. On the main path, "Mỗi ngày học tiếng Anh" therefore stopped repeating, and "Thứ 2 học toán, thứ 4 họp" put both tasks on today. The multi-day test only passed when forced into `RULES_ONLY`.
- Users could plan a day but had no way to close it: no review, and no simple way to move unfinished work forward.
- 028 keeps plan structure in Mr. Bloom. Telling Mr. Bloom "mình xong báo cáo rồi" did nothing.

## Behaviour

### 1. LLM-first planning keeps days, repetition and weekly spreading

- `LLMTask` gains optional `day` (`today` / `tomorrow` / `day_after_tomorrow` / `monday`…, `next_monday`… / `YYYY-MM-DD`), `repeat` (`DAILY` / `WEEKLY` / `WEEKDAYS` / `WEEKENDS`), `repeat_days`, and `spread_over` (`THIS_WEEK` / `NEXT_WEEK`). The prompt explains them.
- Code stays authoritative. Unknown day strings are ignored. `duration_min` above 480 is rejected unless `spread_over` is set, and even then is capped at 7 × 480.
- The parser's literal evidence wins. Each LLM task is matched to the deterministic parse of the same task (exact title, or a unique best token-set match). If the parser read a day, repetition or weekly total from the user's words, those are used; otherwise the validated model fields are used. Ambiguous matches borrow nothing.

### 2. Day review and moving unfinished work (new)

- New intent `DAY_REVIEW` ("Tổng kết hôm nay", "Hôm nay mình làm được gì rồi?", "How did I do today?"). Generic "review … today" stays a task.
- Reply: tasks done / total, focus time (from statistics), and open tasks. Quick replies: **Move unfinished to tomorrow** (`CARRY_OVER_UNFINISHED`) and, before 21:00, **Replan the rest of today**.
- `POST /assistant/actions/CARRY_OVER_UNFINISHED` (`today_service.carry_over_unfinished`):
  - Moves unfinished tasks of today's plan, including overflow tasks, to tomorrow as `PENDING` with `planned_date`.
  - Clears their clock constraints and removes only their future blocks. History, focus runs and rewards stay.
  - Skips tasks with a running focus session and tasks already moved. Running it twice is safe.
  - Tomorrow's draft then carries them in (026 mechanism).
- Evening greetings (from 17:00) offer "Tổng kết hôm nay".

### 3. Completing tasks from chat (new)

- New intent `COMPLETE_TASK` for past-tense completion: "mình đã xong bài tập toán", "xong rồi", "I finished the report". Planning phrases with a time ("phải xong trước 5h") are unaffected.
- One matching open task in today's plan is marked `COMPLETED` through the same service as Today's "Mark complete" (+1 Leaf, idempotent). This is an execution mutation (028); plan structure is untouched.
- If no task or several tasks match, Mr. Bloom asks with one quick reply per open task instead of guessing.

### 4. Repetition edits on a draft (new)

- Patch op `set_recurrence {task_id, recurrence | null}` works on today's and deferred draft tasks.
- Chat: "Cho việc 1 lặp lại mỗi ngày", "Việc 2 lặp lại thứ 2 và thứ 4", "make task 2 repeat every Monday and Friday", "Bỏ lặp lại việc 1" (stops repeating, keeps the task). With no frequency, Mr. Bloom asks.
- With a draft open, these route to `EDIT_DRAFT`, not to a new plan or to stopping a saved recurring task.
- UI: each draft task has a **Repeat** selector (Does not repeat / Every day / Weekdays / Every week).

### 5. Waiting work is visible

- The `MORNING_NO_PLAN` nudge names the tasks waiting for today.
- An unplanned day on Today lists its waiting tasks (deferred, and ↻ recurring) instead of "No tasks scheduled".

### 6. Correctness fixes

- A task counts as "already scheduled" only when it has a block in *that day's* plan. Before this fix, a task that had any block on another day could never be carried over, and reuse on save was refused.
- Replacing today's plan never deletes a task that was moved to another day.

## Out of scope

- A settings screen for recurring templates (API and chat exist).
- Automatic end-of-day carry-over without the user's click.

## Verification

- Backend: `pytest tests/unit tests/api/test_assistant_chat_contract.py`: 531 passed. `tests/unit/test_mr_bloom_upgrade.py` holds 32 new cases.
- Frontend: `vitest` passes the affected suites, and `svelte-check --fail-on-warnings` is clean (with `PUBLIC_API_BASE_URL` set).
- Not run locally (no Docker): `tests/api/test_carry_over.py`, `tests/api/test_multi_day_recurring.py`.
