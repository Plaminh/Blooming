# Implementation Plan: Refactor Today Planning to LLM-First

**Feature**: `027-refactor-today-planning`
**Created**: 2026-09-25

## Technical Context

- The current Today planning flow runs `parse(message)` first, returning a PARSER tier draft if confidence is high, and falls back to LLM only if confidence is low.
- Target architecture: Run the LLM structured extraction first. Fallback to the deterministic parser only if the LLM extraction fails or the provider is down.
- Existing invariants: `_parsed_from_llm` uses the legacy `parse(message)` to strictly merge and guarantee deterministic behavior; `mock_session.add.assert_not_called()` ensures no persistence; `check_today()` performs authoritative bounds and length checks.

## Phase 0: Research

- **Decision**: No external APIs or database schema changes are required. The refactor focuses purely on the intent router control flow in `backend/app/ai/handlers/planner.py` and the corresponding unit/integration tests.
- **Rationale**: Minimal architectural churn to achieve robust semantic planning.

## Phase 1: Design & Contracts

- **Contracts**: Unchanged. `ChatResponse`, `TodayDraft`, and `PlanBlock` schemas remain identical. `preview = None` is strictly maintained.
- **Validation Guide**:
  1. Trigger intent with natural language containing implicitly marked optional tasks.
  2. Verify draft is returned with `tier="LLM"`.
  3. Verify timeline is not generated automatically.
  4. Manually cut off LLM provider and verify degraded `tier="PARSER"`, `degraded="RULES_ONLY"` or `degraded="LLM_FAILED"` behavior.

## Implementation Steps

1. **Update Tests (TDD)**: Modify `test_block10_parser.py`, `test_block_9_integration.py`, and `test_block_8_daily_plan.py` to expect `tier == "LLM"`. Setup `mock_llm` payloads where needed. Add timeout fallback tests.
2. **Refactor Planner**: Modify `backend/app/ai/handlers/planner.py::plan_day` to call `_llm_plan` first for the happy path.
3. **Preserve Fallbacks**: Retain `parse(lenient=True)` logic to run if `_llm_plan` returns None or fails.
4. **Preserve Validation**: Retain the `_parsed_from_llm` deterministic merge logic and `check_today` checks.
5. **Verify No Persistence**: Run `test_assistant_chat_contract.py` to ensure persistence invariants are unviolated.
