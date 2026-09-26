# REST API Usage & Maintenance Contract: Today Endpoints

**Feature**: `028-today-execution-dashboard`  
**Date**: 2026-09-26  

---

## 1. Active Endpoints Retained in Today Execution Flow

### 1.1 `GET /today`
- **Method**: `GET`
- **Query Params**: `date` (`YYYY-MM-DD`, optional, defaults to current user local date)
- **Response**: `TodayResponse | TodayNoPlanResponse`
- **Status in Execution-Only Today**: **Active & Essential**. Used to render the timeline, task blocks, breaks, and carried-over tasks.

### 1.2 `GET /today/draft`
- **Method**: `GET`
- **Query Params**: `date` (`YYYY-MM-DD`, required)
- **Response**: `TodayDraft`
- **Status in Execution-Only Today**: **Active & Essential**. Used to fetch a lossless, completely populated draft for plan adjustment with Mr. Bloom.

### 1.3 `PATCH /today/tasks/{task_id}/status`
- **Method**: `PATCH`
- **Body**: `{ "status": "COMPLETED" | "SKIPPED" | "ACTIVE" | "PENDING" }`
- **Response**: `TaskResponse`
- **Status in Execution-Only Today**: **Active & Essential**.
- **Behavior**:
  - Sets `task.status = "COMPLETED"`.
  - Sets `task.completed_at = now()`.
  - Calls `award_resources(..., leaves=LEAVES_PER_TASK)` to credit 1 Leaf.
  - Updates associated `PlanBlock.status`.
  - Idempotent: Subsequent calls for already completed tasks do not grant duplicate Leaves.

### 1.4 `POST /today/replan`
- **Method**: `POST`
- **Query Params**: `target_date` (`YYYY-MM-DD`, optional, defaults to current user local date)
- **Body**: None
- **Response**: `TodayResponse | TodayNoPlanResponse`
- **Status in Execution-Only Today**: **Active & Essential**.
- **Behavior**:
  - Invokes deterministic scheduler for the remaining unfinished tasks from current time forward.
  - Creates a new `PlanRevision` in PostgreSQL.
  - Preserves plan history.

### 1.4 `POST /focus/start`
- **Method**: `POST`
- **Body**: `{ "task_id": UUID, "planned_focus_seconds": number, "planned_break_seconds": number }`
- **Response**: Focus session run details
- **Status in Execution-Only Today**: **Active & Essential**. Initiates execution timer.

---

## 2. Endpoints Under Dependency Audit & Deprecation Policy

### 2.1 `PATCH /today/tasks/{task_id}`
- **Purpose**: Direct metadata mutation (`title`, `estimated_duration_minutes`, `description`, `category`).
- **Audit Findings**:
  - Used in frontend: Previously only called by `handleSaveTask` in `today/+page.svelte`.
  - Used in backend: Defined in `routes/today.py`, delegating to `today_service.update_task_from_today`.
  - Used in Mr. Bloom / Widget: **None**. (Mr. Bloom updates drafts via patch operations; Widget updates focus status).
- **Maintenance Policy**:
  - The Today UI removes the call to this endpoint.
  - The endpoint is **RETAINED** in backend for now to prevent breaking any auxiliary scripts, fixtures, or third-party tests.
  - Formal removal can be evaluated in a later deprecation cycle after automated testing confirms zero dependencies.

### 2.2 `DELETE /today/tasks/{task_id}`
- **Audit Findings**:
  - **Does not exist** in `routes/today.py`.
  - Task deletion was never exposed on the `/today` router.
- **Maintenance Policy**:
  - No action needed. No deletion endpoint will be added to Today.
