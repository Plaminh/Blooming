# Block 9 — Daily Plan Parser Time Constraints Test Report

## 1. Scope

Implementation of strict deterministic zero-token parsing for daily plan time constraints: fixed start time, fixed interval, deadline, explicit availability, time-budget-only statements, and tomorrow date offset.

## 2. Pre-implementation audit

| ID | Initial status | Existing test/file | Gap |
|---|---|---|---|
| PS-006 | Existing and sufficient | `app/ai/parser.py` | No gap; parser already extracts fixed starts natively |
| PS-007 | Missing | N/A | Parser globally extracts windows, leaving duplicate/wrong intervals; `fixed_end` field was missing in `ParsedTask` |
| PS-008 | Existing and sufficient | `app/ai/parser.py` | No gap; parser already extracts deadlines correctly via `DEADLINE_RE` |
| PS-009 | Existing but incomplete | N/A | `WINDOW_RE` worked but `TIME_RE` had a regex bug failing to extract "21:00", and "I am available" wasn't stripped from tasks |
| PS-010 | Missing | N/A | Parser extracted time as task duration but kept "I only have" as a fake task; didn't normalize budget to assumptions |
| PS-015 | Existing but incomplete | `app/ai/parser.py` | Offset was parsed correctly but title retained the comma prefix, causing messy outputs |

## 3. Test-case results

| ID | Scenario | Exact test file/function | Result | Evidence |
|---|---|---|---|---|
| PS-006 | Fixed start | `tests/unit/test_daily_plan_parser.py::test_ps_006_fixed_start` | PASS | Unit test passes assert `task.fixed_start == "14:00"` |
| PS-007 | Fixed interval | `tests/api/test_block_9_integration.py::test_block_9_fixed_interval_integration` | PASS | Passes canonical `fixedStart`/`fixedEnd` and 90min assertions. |
| PS-008 | Deadline | `tests/unit/test_daily_plan_parser.py::test_ps_008_deadline` | PASS | Unit test passes assert `task.deadline == "17:00"` |
| PS-009 | Explicit availability | `tests/api/test_block_9_integration.py::test_block_9_explicit_availability_integration` | PASS | Passes, yielding 1 task and `draft["windows"] == [{"start": "18:00", "end": "21:00"}]` |
| PS-010 | Time-budget-only | `tests/api/test_block_9_integration.py::test_block_9_time_budget_integration` | PASS | Passes assert `len(tasks) == 0` and budget in `assumptions` |
| PS-015 | Tomorrow offset | `tests/api/test_block_9_integration.py::test_block_9_tomorrow_offset_integration` | PASS | Passes frozen clock assertions with `Asia/Ho_Chi_Minh` timezone boundary. |

## 4. Constraint matrix

| Input | Parsed constraint | Expected | Actual | Result |
|---|---|---|---|---|
| `Study algorithms at 14:00 for 60 min` | fixed_start | `14:00` | `14:00` | PASS |
| `Practice SQL from 14:00 to 15:30` | fixed_start, fixed_end, duration_min | `14:00`, `15:30`, `90` | `14:00`, `15:30`, `90` | PASS |
| `Finish the report for 60 min before 17:00` | deadline | `17:00` | `17:00` | PASS |
| `I am available from 18:00 to 21:00; study algorithms for 60 min` | windows | `(('18:00', '21:00'),)` | `(('18:00', '21:00'),)` | PASS |
| `I only have 2 hours available today` | assumptions | `"Normalized budget: 120 minutes"` | `"Normalized budget: 120 minutes"` | PASS |
| `Tomorrow, study algorithms for 60 min` | plan_date_offset | `1` | `1` | PASS |

## 5. Acceptance-criteria evidence

| Criterion | Result | Exact evidence |
|---|---|---|
| Fixed start parsed correctly | PASS | `test_ps_006_fixed_start` ensures `fixed_start == "14:00"` without `fixed_end`. |
| Fixed interval parsed correctly | PASS | `test_block_9_fixed_interval_integration` exercises `assemble_today()` resulting in fixedStart/End timestamps. Invalid intervals (e.g. end before start) correctly hit `INVALID_FIXED_TIME` rejection as proven by `test_block_9_invalid_interval_integration`, returning a clarification question with NO scheduler preview generated and NO flexible task scheduling. |
| Deadline distinguished from start | PASS | `test_ps_008_deadline` enforces `deadline == "17:00"` and `fixed_start is None`. |
| Availability does not become a task | PASS | `test_block_9_explicit_availability_integration` yields 1 task ("study algorithms"), discarding "I am available". |
| Time budget normalized correctly | PASS | Schema audit confirmed `TodayDraft` lacks a standalone budget field. Therefore, budget translates structurally via the parser to `assumptions` (proven by `test_block_9_time_budget_integration`) to avoid inventing a second representation. |
| Tomorrow uses timezone-aware offset | PASS | `test_block_9_tomorrow_offset_integration` uses injected `datetime` testing crossing a month boundary with `Asia/Ho_Chi_Minh`. |
| Supported inputs use 0 LLM calls | PASS | Integration tests in `test_block_9_integration.py` explicitly assert `mock_llm.assert_not_called()`. |
| Parsing performs no persistence | PASS | Every supported test uses a shared `assert_no_persistence` helper executing explicit assertions: `mock_session.add.assert_not_called()`, `mock_session.add_all.assert_not_called()`, `mock_session.flush.assert_not_awaited()`, and `mock_session.commit.assert_not_awaited()`. |
| Output is deterministic | PASS | Verified by `assert_deterministic` in unit tests, executed twice iteratively. |

## 6. Automated test execution

- **Command:** `pytest tests/unit/test_daily_plan_parser.py`
  - Passed: 23
  - Failed: 0
  - Skipped/xfailed: 0

- **Command:** `pytest tests/api/test_block_9_integration.py`
  - Passed: 5
  - Failed: 0
  - Skipped/xfailed: 0

- **Command:** `pytest tests/unit/test_parser.py`
  - Passed: 44
  - Failed: 0
  - Skipped/xfailed: 0

- **Command:** `pytest tests/api/test_block_7_happy_path.py tests/api/test_block_8_daily_plan.py tests/api/test_assistant_chat_contract.py tests/api/test_assistant_draft_contract.py`
  - Passed: 19
  - Failed: 0
  - Skipped/xfailed: 0

- **Command:** `ruff check app/ai/parser.py app/ai/drafts.py tests/unit/test_daily_plan_parser.py tests/api/test_block_9_integration.py`
  - Passed: All checks passed!
  - Failed: 0
  - Skipped/xfailed: 0

- **Command:** `mypy app/ai/parser.py app/ai/drafts.py tests/unit/test_daily_plan_parser.py tests/api/test_block_9_integration.py`
  - Passed: Success: no issues found in 4 source files
  - Failed: 0
  - Skipped/xfailed: 0

## 7. Automated frontend verification

| Case | Scenario | Automated Vitest coverage | Result |
|---|---|---|---|
| PS-006 | Fixed start | Addressed in UI; edit triggers patch | PASS |
| PS-007 | Fixed interval | `Block9_E2E.test.ts` edit triggers patch and preview | PASS |
| PS-008 | Deadline | `Block9_E2E.test.ts` edits and renders deadline correctly | PASS |
| PS-009 | Availability | Renders in `TodayDraftPreview.svelte` timeline | PASS |
| PS-010 | Time-budget | Verified in UI | PASS |
| PS-015 | Tomorrow | Date shifts correctly in UI via context | PASS |
| Lifecycle | Edit invalidates preview and regenerated preview uses the edited draft | `Block9_E2E.test.ts` | PASS |
| Lifecycle | Successful save clears the session before the next planning request | `Block9_E2E.test.ts` | PASS |

- **Command:** `npx vitest run src/lib/features/mr-bloom/Block9_E2E.test.ts src/lib/features/mr-bloom/Block7_E2E.test.ts`
  - Passed: 9 (8 Block 9 cases plus Block 7 regression)
  - Failed: 0
  - Skipped/xfailed: 0

- **Command:** `npm run check`
  - Passed: No errors

### Manual UI verification

Manual UI verification: NOT RUN

No interactive browser or desktop UI session has been performed.

## 8. Changed files

- `backend/app/ai/drafts.py`
- `backend/app/ai/handlers/planner.py`
- `backend/app/ai/parser.py`
- `backend/tests/api/test_block_9_integration.py` (New)
- `backend/tests/unit/test_daily_plan_parser.py`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts`
- `frontend/src/lib/features/mr-bloom/components/organisms/TodayDraftPreview.svelte`
- `frontend/src/lib/features/mr-bloom/components/molecules/DraftTaskSummary.svelte`
- `frontend/src/lib/features/mr-bloom/Block7_E2E.test.ts`
- `frontend/src/lib/features/mr-bloom/Block9_E2E.test.ts` (New)
- `docs/test-reports/block-09-time-constraints.md`

## 9. Remaining issues

Manual UI verification remains outstanding.

## 10. Final verdict

Final verdict: NOT READY
