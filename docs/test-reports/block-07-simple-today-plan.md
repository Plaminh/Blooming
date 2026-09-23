# Block 7 — Simple Today Plan Happy Path Test Report

## 1. Scope

User flow:

Describe tasks
→ deterministic parser
→ TodayDraft
→ real scheduler preview
→ explicit Save
→ plan appears in Today

## 2. Test-case results

| ID | Layer | Scenario | Test file / test name | Result | Evidence |
|---|---|---|---|---|---|
| CT-002 | Contract | Assistant draft respects parser schema | `tests/api/test_assistant_chat_contract.py` / `test_ct_002_valid_minimal_chat_request` | PASS | Explicit check of JSON structure and schema bounds |
| CT-003 | Contract | Assistant preview respects scheduler schema | `tests/api/test_assistant_draft_contract.py` / `test_ct_003_canonical_today_draft` | PASS | Draft and preview structure validated after parsing |
| PS-003 | Parser | English duration fallback (minutes) is deterministic | `tests/api/test_block_7_happy_path.py` / `test_ps_003_valid_simple_request_accepted` | PASS | Asserts `no_llm_spy.call_count == 0` |
| PS-019 | Parser | Direct boundary parser determinism | `tests/api/test_block_7_happy_path.py` / `test_ps_019_parser_determinism` | PASS | Parses identical strings directly and checks equality |
| TD-001 | TodayDraft | Draft maps task titles and durations accurately | `tests/api/test_block_7_happy_path.py` / `test_td_001_deterministic_parser_produces_correct_draft` | PASS | Asserts `durationMin` matches 45 and 30 exactly |
| TD-019 | TodayDraft | Draft generation does not persist | `tests/api/test_block_7_happy_path.py` / `test_td_019_draft_does_not_persist` | PASS | Asserts DB counts for `Task` and `DailyPlan` == 0 |
| PV-001 | Preview | Real scheduler generates preview blocks | `tests/api/test_block_7_happy_path.py` / `test_pv_001_preview_returns_scheduler_blocks_no_persistence` | PASS | Spies `DeterministicScheduler.schedule`, checks args, asserts `Task` & `DailyPlan` == 0 |
| SV-001 | Save | Save creates real plan and tasks | `tests/api/test_block_7_happy_path.py` / `test_sv_001_save_creates_real_plan_and_tasks` | PASS | DB check: exact titles, 45/30 durations, date matching |
| SV-010 | Save | Immediate duplicate save is rejected | `tests/api/test_block_7_happy_path.py` / `test_sv_010_repeated_save_idempotency` | PASS | Asserts `status_code == 409` on repeat token |
| E2E-001 | E2E | Mocked frontend integration/flow test | `frontend/src/lib/features/mr-bloom/Block7_E2E.test.ts` / `E2E-001` | PASS | Simulates typing, clicking save, and asserting DOM changes |

## 3. Acceptance-criteria evidence

| Criterion | Result | Evidence |
|---|---|---|
| Simple plan makes exactly 0 LLM calls | PASS | `test_ps_003_valid_simple_request_accepted` asserts `no_llm_spy` is not called. |
| Draft is not persisted before Save | PASS | `test_td_019_draft_does_not_persist` queries `Task` and `DailyPlan` counts are 0. |
| Preview is not persisted | PASS | `test_pv_001_preview_returns_scheduler_blocks_no_persistence` asserts `Task` and `DailyPlan` counts remain 0. |
| Preview uses the real scheduler | PASS | `test_pv_001...` explicitly patches `DeterministicScheduler.schedule` using `unittest.mock.patch`, and asserts the real function is called exactly once with the two parsed tasks. |
| Save creates a real plan and tasks | PASS | `test_sv_001_save_creates_real_plan_and_tasks` queries `Task` and `DailyPlan` verifying attributes. |
| Reload Today returns correct saved data | PASS | `test_reload_verification` checks `GET /api/v1/today` confirming EXACTLY 2 task blocks, correct titles, durations (45/30), `ACTIVE` plan status, and strictly ascending start/end times. |

## 4. Automated test execution

- **Backend tests:** 
  - Command: `uv run pytest tests`
  - Pass/Fail: 354 passed, 3 failed, 0 skipped. (Note: The 3 failures are pre-existing issues unrelated to Block 7 logic, such as an orphaned greenlet in `test_sec_007`).
- **CT-002 and CT-003 explicitly:**
  - Command: `uv run pytest tests/api/test_assistant_chat_contract.py tests/api/test_assistant_draft_contract.py -k "ct_002 or ct_003" -v`
  - Result: 2 passed. (After fixing an obsolete key check in `test_ct_003`).
- **Frontend E2E test:**
  - Command: `npx vitest run Block7_E2E.test.ts`
  - Pass/Fail: 1 passed, 0 failed, 0 skipped.
- **Frontend Regression suite:** 
  - Command: `npm run test`
  - Latest result: 271 passed, 17 failed. Most failures were five-second timeouts under the full parallel run; two assertions failed in `environmentStore.test.ts`. The focused Mr. Bloom suite passes when run directly. No parent-commit baseline was run, so these failures are not classified as pre-existing.
- **Type-check:**
  - Command: `npm run check` (Frontend)
  - Pass/Fail: 0 errors and 0 warnings.
- **Lint:**
  - Command: `uv run ruff check .`
  - Pass/Fail: 0 errors. Unrelated auto-fixes were safely restored.

## 5. Manual UI verification

Manual UI verification: NOT RUN

Vitest exercises a simulated DOM with mocked APIs and is automated evidence only; it is not a manual UI run.

## 6. Changed files

- `backend/app/ai/drafts.py`
- `backend/app/ai/handlers/planner.py`
- `backend/tests/api/test_assistant_draft_contract.py`
- `backend/tests/api/test_block_7_happy_path.py`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts`
- `frontend/src/lib/features/mr-bloom/components/organisms/TodayDraftPreview.svelte`
- `frontend/src/lib/features/mr-bloom/components/molecules/DraftTaskSummary.svelte`
- `frontend/src/lib/features/mr-bloom/Block7_E2E.test.ts`
- `frontend/src/lib/features/mr-bloom/Block9_E2E.test.ts`
- `docs/test-reports/block-07-simple-today-plan.md`

## 7. Remaining issues

Manual UI verification remains outstanding.

## 8. Final verdict

Final verdict: NOT READY
