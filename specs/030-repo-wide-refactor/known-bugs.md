# Known Bugs Register

This register tracks existing bugs present before the repo-wide refactor began. These are documented to distinguish them from new regressions caused by the refactor.

## BUG-001: Assistant Today Save Failure
- **Feature**: Assistant Chat / Today Plan
- **Reproduction**: Trigger an explicit action to save a Daily Plan from the chat.
- **Current behavior**: Fails with `IntegrityError: daily_plans_confirmation_valid`.
- **Expected behavior**: Plan is saved successfully and session completes.
- **Severity**: High (but pre-existing)
- **Related Test**: `test_successful_today_save_completes_planning_session`

## BUG-002: Today Draft Round Trip Failure
- **Feature**: Today Plan Draft
- **Reproduction**: Load a draft and attempt to round-trip it.
- **Current behavior**: Fails with `TypeError` in parsing/serialization.
- **Expected behavior**: Draft is correctly serialized and deserialized.
- **Severity**: Medium
- **Related Test**: `test_today_draft_round_trip`

## BUG-003: Today Draft Other User Security
- **Feature**: Today Plan Draft
- **Reproduction**: Attempt to access another user's draft.
- **Current behavior**: Fails a SQLAlchemy assertion.
- **Expected behavior**: Should cleanly reject the request with a 403/404.
- **Severity**: Medium
- **Related Test**: `test_today_draft_other_user_plan`
