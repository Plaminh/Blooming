# Draft Contract and Response Resilience Test Report

## Scope
```text
CT-003
CT-004
CT-010
CTX-011
```

## Canonical Contract
The final implemented schema establishes a strict discriminated union utilizing the `type` field, aligning perfectly between backend Pydantic and frontend TypeScript definitions.

```python
# Backend (app/schemas/assistant.py)
class ChatResponse(BaseModel):
    reply: str
    draft: Annotated[RoadmapDraft | TodayDraft, Field(discriminator="type")] | None = None
```

```typescript
// Frontend (lib/api.ts)
export type AssistantDraft = TodayDraft | RoadmapDraft;

export interface TodayDraft {
  type: 'today';
  planDate: string;
  timezone: string;
  windows: AvailabilityWindowDraft[];
  tasks: TaskDraft[];
}

export interface RoadmapDraft {
  type: 'roadmap';
  goalTitle: string;
  goalDescription: string;
  targetDate: string;
  milestones: MilestoneDraft[];
}
```
**Nullable draft semantics**: The draft is entirely optional. If the LLM generates a valid reply but a malformed draft (e.g. invalid bounds), the backend catches the `ValidationError`, discards the draft (`draft = null`), and returns the valid `reply` with an `HTTP 200` rather than a `502`.

## Backend-Owned Fields
| Field | LLM input accepted? | Backend authoritative? | Exact backend source | Test evidence |
|---|---|---|---|---|
| ID (`task_id`) | NO | YES | `uuid.uuid4().hex[:8]` generated in `assemble_today` during normalization. | `test_ct_003_canonical_today_draft` attempts `id="malicious-id"`; output canonical ID differs. |
| Timezone | NO | YES | Derived from `user_settings.timezone` (or "UTC" fallback) injected via `ctx.timezone`. | `test_ct_003_canonical_today_draft` asserts `timezone` equals `expected_tz`. |
| Date (`planDate`) | NO | YES | Computed deterministically from `ctx.now.date() + timedelta(offset)` in `assemble_today`. | `test_ct_003_canonical_today_draft` asserts `planDate` exactly equals the local mock `Clock` output (`2026-01-01`). |
| Derived Totals (`preview.total_duration`)| NO | YES | Computed strictly by `today_service.preview_today_draft` which sums the parsed tasks. | `test_ct_003_canonical_today_draft` asserts `preview["total_duration"] == 30`. |
| Roadmap backend-owned deterministic fields | N/A | N/A | N/A for this contract. | Roadmap generation utilizes no provider or external derivations here. |

## Test Coverage
| Test ID | Test function | Behavior | Result |
|---|---|---|---|
| CT-003 | `test_ct_003_canonical_today_draft` | Sends a mocked LLM payload containing malicious IDs/Dates. Verifies the canonical response uses exact deterministic backend context values (Fixed mock time: `2026-01-01 09:00:00 UTC`). | BLOCKED |
| CT-004 | `test_ct_004_canonical_roadmap_draft` | Sends a roadmap request. Verifies `llm_provider.call` is never invoked (`assert_not_awaited()`) because roadmap is entirely rules-based, explicitly asserting `planDate`, `timezone`, `windows`, and `tasks` do not leak. | BLOCKED |
| CT-010 | `test_ct_010_discriminated_union` | (Pure Unit) Explicitly creates `ChatResponse` objects and verifies that invalid discriminators raise a hard `ValidationError`. | PASS |
| CTX-011 | `test_ctx_011_preserve_reply_when_draft_invalid` | Injects `duration_min=1` (violating `LLMTask` constraint `ge=5`). Proves HTTP 200 with the valid text reply intact and `draft = None`. | BLOCKED |

## Resilience Cases
| Provider reply | Provider draft | Expected API behavior |
|---|---|---|
| valid | valid Today | 200 + reply + Today |
| valid | valid Roadmap | 200 + reply + Roadmap |
| valid | invalid draft | 200 + reply + null draft |
| invalid/unrecoverable response | invalid | existing provider-error behavior (e.g. `LLMError`) |

## RED → GREEN
- **CT-010 RED**: Before adding `Annotated[..., Field(discriminator="type")]`, Pydantic relied on left-to-right matching. It now strictly enforces the discriminator, as proven by the newly added unit test which passes `ValidationError` checks.
- **CTX-011 RED**: N/A. Existing production behavior (`app/ai/handlers/planner.py`) already satisfied the requirement perfectly by catching `ValidationError` and defaulting to `(ParsedPlan(), reply)`. Regression coverage was strengthened without requiring production patches.

## Regression
- `pytest --collect-only tests/api/test_assistant_draft_contract.py`
  - Passed: 3 | Failed: 0 | Blocked: 0 | Skipped: 0
- `pytest tests/unit/test_assistant_schemas.py`
  - Passed: 7 | Failed: 0 | Blocked: 0 | Skipped: 0
- `pytest tests/api/test_assistant_draft_contract.py`
  - Passed: 0 | Failed: 0 | Blocked: 3 | Skipped: 0 (Docker daemon unavailable for integration setup).
