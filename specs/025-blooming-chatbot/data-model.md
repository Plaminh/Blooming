# Data Model: Blooming Chatbot Foundation

## 1. Canonical Draft Entities (Pydantic / API layer)

These represent the core uncommitted state for plans and goals.

### `TodayDraft`
- `type`: `Literal["today"]`
- `planDate`: `date`
- `timezone`: `str`
- `windows`: `list[AvailabilityWindowDraft]`
- `tasks`: `list[TaskDraft]`

### `TaskDraft`
- `id`: `str`
- `title`: `str`
- `durationMin`: `int` (5–480)
- `priority`: `Literal["URGENT", "HIGH", "MEDIUM", "LOW"]`
- `importance`: `Literal["CORE", "OPTIONAL"]` *(Existing in DB, newly surfaced)*
- `category`: `TaskCategory | None` *(Existing in DB, newly surfaced)*
- `estimateSource`: `Literal["USER", "RULE", "AI", "HISTORY"]`
- `breakAfterMin`: `int | None` *(Maps to DB `preferred_break_duration_minutes`)*
- `deadline`: `datetime | None`
- `schedulingType`: `Literal["FLEXIBLE", "FIXED"]`
- `fixedStart`: `datetime | None`
- `fixedEnd`: `datetime | None`
- `dependencies`: `list[str]`
- `splittable`: `bool`

### `RoadmapDraft`
- `type`: `Literal["roadmap"]`
- `goalTitle`: `str`
- `goalDescription`: `str`
- `targetDate`: `date`
- `milestones`: `list[MilestoneDraft]`

### `MilestoneDraft`
- `id`: `str`
- `title`: `str`
- `targetDate`: `date`
- `expectedOutcome`: `str | None`

## 2. New Database Entities

### `AiUsageLog`
A strictly operational log for AI request tracing and budget guards. No conversational content or PII is recorded.

**Table**: `ai_usage_log`
- `id`: `BIGSERIAL PRIMARY KEY`
- `user_id`: `UUID` (Foreign key to `users`, `ON DELETE SET NULL`)
- `created_at`: `TIMESTAMPTZ NOT NULL DEFAULT now()`
- `purpose`: `VARCHAR(20) NOT NULL` (e.g., ROUTER, CHITCHAT, PLANNER, EDITOR)
- `provider`: `VARCHAR(20) NOT NULL`
- `model`: `VARCHAR(80) NOT NULL`
- `prompt_tokens`: `INT`
- `completion_tokens`: `INT`
- `latency_ms`: `INT`
- `outcome`: `VARCHAR(20) NOT NULL` (OK, REPAIRED, RATE_LIMITED, ERROR, BAD_OUTPUT)

**Indexes**:
- `ai_usage_recent_idx` on `(created_at DESC)`
- `ai_usage_user_recent_idx` on `(user_id, created_at DESC)`

**Retention**: Rows older than 30 days are purged upon startup.

## 3. Existing Database Entities Leveraged

### `PlanningSession` & `PlanningMessage`
The backend already defines these tables but underutilizes them.
- `PlanningSession.session_type`: Used for `DAILY_PLAN`, `PLAN_EDIT`, `REPLAN`, `ROADMAP`.
- `PlanningSession.status`: Used for `OPEN`, `AWAITING_CLARIFICATION`, `COMPLETED`, `CANCELLED`.
- `PlanningMessage.structured_payload`: `JSONB` for persisting intentions, tiers, drafts, and degraded states.

### `Task` and `FocusRun` (For Calibration)
- Calibration will compute median duration ratios using `Task.estimated_duration_minutes` vs `SUM(FocusRun.actual_duration_seconds)`.
- No schema changes are required for this MVP (a feedback table is deferred to a future phase).

## 4. Migration Requirements
- **Up Migration**: Create `ai_usage_log` and its two indexes.
- **Down Migration**: Drop `ai_usage_log`.
- No other migrations required as existing schemas cover the required fields (e.g., `importance` and `category` on `Task`).

## 5. Constraints and Boundaries
- `AiUsageLog` is strictly write-mostly, with periodic read for the 24-hour token budget query.
- Goal creation via `POST /goals/from-roadmap` must execute within a single transaction boundary, saving the Goal and its Milestones atomically. Any failure rolls back the entire hierarchy.
