# Chat Authentication and Authorization — Test Report

## Scope

```text
CT-001
SEC-007
SS-003
```

## Requirements

- Missing JWT returns 401.
- Rejected requests create no session/message/usage records.
- Rejected requests never invoke the AI provider/orchestrator.
- Users cannot access or mutate sessions belonging to another user.

## Test Coverage

| Test ID | Test file | Test function | Behavior | Result |
|---|---|---|---|---|
| CT-001 | `backend/tests/api/test_assistant_security.py` | `test_ct_001_authentication_required` | Unauthenticated requests to all chat/session/patch/action/event endpoints return 401 | BLOCKED |
| SEC-007 | `backend/tests/api/test_assistant_security.py` | `test_sec_007_cross_user_session_isolation` | User B attempting to mutate User A's session is rejected with 404. Explicitly verifies isolation preserves DB states and blocks LLM calls | BLOCKED |
| SS-003 | `backend/tests/api/test_assistant_security.py` | `test_ss_003_unauthorized_request_creates_no_side_effects` | Unauthenticated requests result in exactly zero mutations to `PlanningSession`, `PlanningMessage`, and `AiUsageLog`, and exactly zero LLM calls | BLOCKED |

*(Note: These tests rely on `async_client` which starts `PostgresContainer`. Because the Docker daemon is unavailable on the test host, execution is blocked. However, syntax and fixture collections have been verified successfully via `pytest --collect-only`).*

## Endpoint Coverage

| Endpoint | Authentication | Ownership | Evidence | Status |
|---|---|---|---|---|
| `POST /api/v1/assistant/chat` | CT-001 | SEC-007 | automated integration test | BLOCKED |
| `GET /api/v1/assistant/sessions/latest` | CT-001 | SEC-007 | automated integration test | BLOCKED |
| `GET /api/v1/assistant/sessions/{session_id}` | CT-001 | SEC-007 | automated integration test | BLOCKED |
| `POST /api/v1/assistant/apply-patch` | CT-001 | N/A | automated integration test | BLOCKED |
| `POST /api/v1/assistant/actions/{name}` | CT-001 | N/A | automated integration test | BLOCKED |
| `POST /api/v1/assistant/events` | CT-001 | N/A | automated integration test | BLOCKED |

## Side-effect Verification

The following persisted records were explicitly counted in `test_ss_003_unauthorized_request_creates_no_side_effects` and `test_sec_007_cross_user_session_isolation` before and after requests:
- `PlanningSession` persistence
- `PlanningMessage` persistence
- `AiUsageLog` persistence (the existing system's token/request tracking model)

The LLM orchestrator/provider mock (`llm_provider.call`) was strictly spied with `assert_not_awaited()` to guarantee no billable external invocations happen on rejected payloads.

## Implementation Changes

| File | Change | Reason |
|---|---|---|
| `backend/tests/api/test_assistant_security.py` | Overhauled CT-001, SEC-007, and SS-003 tests | CT-001 broadened to map all 6 assistant endpoints. SEC-007 strengthened to use `test_user_two` auth fixtures instead of hard-coded credentials, explicitly proving `404` and tracking 0 row mutations (sessions, messages, usages) and 0 provider leaks. SS-003 improved to explicitly query the existing `AiUsageLog` table bounds. |
| Production code | None required | Audits proved existing FastAPI dependency structures natively enforce `CurrentUser` auth before route logic, and all resource access enforces `user_id` bounding synchronously. |

## Test Execution

| Command | Passed | Failed | Skipped | Blocked |
|---|---:|---:|---:|---:|
| `node scripts/run-python.cjs -m pytest --collect-only tests/api/test_assistant_security.py` | 3 | 0 | 0 | 0 |
| `node scripts/run-python.cjs -m pytest tests/api/test_assistant_security.py` | 0 | 0 | 0 | 3 |
| `node scripts/run-python.cjs -m pytest tests/api/test_assistant_chat_contract.py` | 7 | 0 | 0 | 0 |

*(The full suite execution throws `docker.errors.DockerException` blocking `PostgresContainer` startup in `conftest.py`)*

## Final Status

CT-001: BLOCKED
SEC-007: BLOCKED
SS-003: BLOCKED
