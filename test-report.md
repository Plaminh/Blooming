# Chat API Contract Test Report

## Scope
Implementation and validation of the base API contract (CT-002, CT-005, CT-006, CT-007, CT-011, CT-012, CT-015) between the frontend and backend for the planning chat endpoint in the Blooming repository.

## Initial Audit

| Test ID | Requirement | Initial Status | Existing Test/File | Gap Found |
|---|---|---|---|---|
| CT-002 | Valid minimal chat request | Missing | None | No test covered a minimal request asserting only the required dependencies were hit. |
| CT-005 | Empty message | Missing | None | No tests existed for empty or whitespace-only messages blocking execution. |
| CT-006 | Exactly 2,000 characters | Missing | None | Missing boundary tests. Backend schema allowed 4,000. |
| CT-007 | Over 2,000 characters | Missing | None | Missing boundary test for message length rejection. |
| CT-011 | Maximum four suggestions | Missing | None | Schema was enforcing length 3 instead of 4 and lacked a deterministic truncating fallback. |
| CT-012 | Suggestion label length | Missing | None | Missing validation enforcing 80 chars without server errors. |
| CT-015 | Backend–frontend type compatibility | Missing | None | No static contract fixture existed linking the backend serialization schema to the frontend TypeScript type. |

## Contract Decisions

- **Chat message minimum/maximum length**: Set to max 2000 characters.
- **Whitespace handling and normalizer order**: Implemented a `mode="before"` field validator on `ChatRequest.message` that strips whitespace. If the string is purely whitespace or empty, it throws a `ValueError`, deterministically rejecting the request before Pydantic evaluates `max_length`.
- **Service/Orchestrator mocks**: Invalid requests prove they do not leak into logic providers by ensuring `mock_chat.assert_not_awaited()` and `mock_session.add.assert_not_called()`.
- **Maximum suggestion count**: The backend boundary truncates any upstream suggestions > 4 down to exactly 4 items safely.
- **Suggestion label maximum length**: The public endpoint must never return labels > 80 chars. `mode="before"` deterministic truncation slices overly long string values to 80 chars safely.
- **Preview schema typing**: Changed backend `preview` from a broad unrestricted `dict` to strictly use the concrete `TodayPreviewResponse` matching exactly what's supported on the frontend.
- **Backend/Frontend Strictness Matching**: Removed optional markers (`?`) in TypeScript `ChatResponse` for fields that Pydantic implicitly always serializes (e.g. `session_id: string | null;` instead of `session_id?: string | null;`). 
- **Frontend/backend compatibility mechanism (CT-015)**: Adopted a robust JSON fixture array (`contracts/chat_response_fixture.json`) that covers four exact shapes: minimal response, suggestions/assumptions, `TodayDraft` response, and `RoadmapDraft` response. Frontend TS validates this using an exact statically-typed copy instead of an unsafe `as ChatResponse[]` casting override. Backend tests execute a meaningful round-trip JSON dictionary comparison (`assert dumped == item`).

## Tests Added or Updated

| Test ID | Test File | Test Name | What It Verifies |
|---|---|---|---|
| CT-002 | `backend/tests/api/test_assistant_chat_contract.py` | `test_ct_002_valid_minimal_chat_request` | Verifies minimal JSON input passes optional fields safely, asserting orchestrator is called once with normalized defaults. |
| CT-005 | `backend/tests/api/test_assistant_chat_contract.py` | `test_ct_005_empty_message` | Asserts empty/whitespace-only payloads fail (422) and orchestrator is `not_awaited`. |
| CT-006 | `backend/tests/api/test_assistant_chat_contract.py` | `test_ct_006_exactly_2000_characters` | Checks boundary of a 2,000 char message surrounded by whitespace, proving exactly 2000 chars hit the route orchestrator. |
| CT-007 | `backend/tests/api/test_assistant_chat_contract.py` | `test_ct_007_over_2000_characters` | Checks boundary of a 2,001 char message correctly fails via 422, with zero DB/orchestrator calls. |
| CT-011 | `backend/tests/api/test_assistant_chat_contract.py` | `test_ct_011_maximum_four_suggestions` | Validates 0, 4, and 5 upstream suggestions. Ensures 5 truncates to 4 without throwing 500s. |
| CT-012 | `backend/tests/api/test_assistant_chat_contract.py` | `test_ct_012_suggestion_label_length` | Ensures 80 char labels pass and 81+ char labels safely truncate. |
| CT-015 | `backend/tests/api/test_assistant_chat_contract.py` | `test_ct_015_backend_frontend_type_compatibility` | Ensures backend Pydantic model correctly validates multi-case fixture and round-trips via exact-match dictionary equality. |
| CT-015 | `frontend/src/lib/api/chatContract.test.ts` | `Chat API Contract CT-015` | Enforces structural TS compile-time type matching without unsafe types and checks validity of each scenario structure inside Vitest. |

## Production Code Changes

| File | Change | Reason |
|---|---|---|
| `backend/app/schemas/assistant.py` | Added valid `Any` type annotations to `mode="before"` validators for `message`, `suggestions`, `label` | Enforces preprocessing validation. |
| `backend/app/schemas/assistant.py` | Updated `preview` to concrete `TodayPreviewResponse` | Strict API typing. |
| `frontend/src/lib/api.ts` | Strengthened exported `ChatResponse` interface removing unsafe `?` | Enforces exact contract tracking matching Pydantic backend output behaviour. |
| `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts` | Replaced generic payload response with `ChatResponse` | Removed unrelated prior additions (`tz`, `isWaitingForResponse`). |

## Test Execution Results

| Command | Working Directory | Result | Passed | Failed | Blocked | Notes |
|---|---|---|---:|---:|---:|---|
| `node scripts/run-python.cjs -m pytest tests/api/test_assistant_chat_contract.py tests/unit/test_assistant_schemas.py tests/unit/test_assistant_service.py` | `E:\Blooming` | **PASS** | 17 | 0 | 0 | Contract tests and Assistant schemas/services logic passed successfully without dependencies on network APIs. |
| `cd frontend && npx vitest run src/lib/api/chatContract.test.ts` | `E:\Blooming` | **PASS** | 1 | 0 | 0 | End-to-end verification of TypeScript `ChatResponse` exactly matching JSON. |
| `cd frontend && npm run lint` | `E:\Blooming` | **PASS** | N/A | 0 | 0 | Runs `svelte-check` successfully covering complete frontend project safety. |
| `cd frontend && npx tsc --noEmit` | `E:\Blooming` | **PASS** | N/A | 0 | 0 | TypeScript strict-type compilation verification. |
| `cd frontend && npx vitest run src/lib/features/mr-bloom` | `E:\Blooming` | **PASS** | 25 | 0 | 0 | Existing Mr. Bloom frontend units passed successfully. |
| `node scripts/run-python.cjs -m pytest tests/api/test_assistant_routes.py` | `E:\Blooming` | **BLOCKED** | 0 | 0 | 20 | BLOCKED — Docker daemon unavailable. Results in `docker.errors.DockerException` blocking `PostgresContainer` startup in `conftest.py`. |

## Requirement Traceability

| Test ID | Automated Evidence | Final Status |
|---|---|---|
| CT-002 | `test_ct_002_valid_minimal_chat_request` | PASS |
| CT-005 | `test_ct_005_empty_message` | PASS |
| CT-006 | `test_ct_006_exactly_2000_characters` | PASS |
| CT-007 | `test_ct_007_over_2000_characters` | PASS |
| CT-011 | `test_ct_011_maximum_four_suggestions` | PASS |
| CT-012 | `test_ct_012_suggestion_label_length` | PASS |
| CT-015 | `test_ct_015_backend_frontend_type_compatibility`, `chatContract.test.ts` | PASS |

## Final Result
Complete.
Contract scope: PASS
Docker-dependent broader suite: BLOCKED by environment
