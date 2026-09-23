# Block 8 — Daily Plan Parser Test Report

## Scope

Focused correction pass for deterministic daily-plan parsing, its production integration boundary, and the affected Block 7/assistant contracts.

## Implemented behavior

- `smart_split()` splits semicolons, newlines, conjunctions, and only commas that separate duration-bearing tasks; descriptive commas remain in task titles.
- Duration parsing handles `1h`, `90p`, `45 min`, `1h30`, `one-and-a-half hours`, `1.5 hours`, and `0.5h`.
- A trailing duration connector (`for`/`trong`) is removed from the exact title.
- `Today:` is treated as a planning prefix without stripping natural text such as `Today I need ...`.

## Determinism evidence

Every PS-001 through PS-005 representative input is parsed twice. The tests compare explicit snapshots containing task count, exact ordered titles, exact ordered durations, and exact unresolved indices. The assertions do not depend on whole-dataclass equality.

## Integration evidence

`test_integration_zero_llm_calls_for_supported_input` exercises `plan_day()` with the real parser and planner boundary. It asserts that the tier is exactly `PARSER`, both task titles and durations are exact and ordered, the LLM provider is not called, synchronous `AsyncSession.add()` and `add_all()` are not called, and asynchronous `AsyncSession.flush()` and `commit()` are not awaited.

The test uses an autospecced real `AsyncSession` contract. It does not use the `/assistant/chat` route because that route intentionally persists conversation messages independently of plan parsing.

## Automated verification

| Command (from `backend`) | Result |
|---|---|
| `pytest tests/unit/test_daily_plan_parser.py -q` | PASS — 17 passed |
| `pytest tests/api/test_block_8_daily_plan.py -q` | PASS — 1 passed |
| `pytest tests/api/test_assistant_draft_contract.py -q` | PASS — 3 passed |
| `pytest tests/api/test_block_7_happy_path.py -q` | PASS — 8 passed |
| `python -m ruff check app/ai/parser.py tests/unit/test_daily_plan_parser.py tests/api/test_block_8_daily_plan.py tests/api/test_assistant_draft_contract.py tests/api/test_block_7_happy_path.py` | PASS |
| `python -m ruff check .` | FAIL — 4 errors: duplicate `UUID` import in `app/services/user_settings_service.py`, unnecessary f-string in `tests/conftest.py`, and two unused imports in `tests/unit/test_weather_schemas.py` |
| `python -m mypy app tests` | FAIL — missing `cachetools` stubs and duplicate module naming for `tests/api/test_focus_routes.py` |
| `python -m mypy --explicit-package-bases app/ai/parser.py tests/unit/test_daily_plan_parser.py tests/api/test_block_8_daily_plan.py tests/api/test_assistant_draft_contract.py tests/api/test_block_7_happy_path.py` | FAIL — 4 errors: three nullable `called_tasks` errors in the Block 7 test and one `ChatResponse.preview` type mismatch in `app/ai/handlers/planner.py` |

No failure is characterized as pre-existing because no parent-commit baseline was run.

## Manual verification

NOT RUN.

## Changed Files

- `backend/app/ai/parser.py`
- `backend/tests/api/test_assistant_draft_contract.py`
- `backend/tests/api/test_block_7_happy_path.py`
- `backend/tests/api/test_block_8_daily_plan.py`
- `backend/tests/unit/test_daily_plan_parser.py`
- `docs/test-reports/block-08-daily-plan-parser.md`

## Final verdict

NOT READY — Block 8 must remain open
