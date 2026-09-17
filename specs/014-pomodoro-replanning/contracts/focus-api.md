# API Contracts: Pomodoro

## Endpoints

### 1. Start Session
**POST** `/api/v1/focus/start`

**Request Body**:
```json
{
  "task_id": "uuid (optional)",
  "plan_block_id": "uuid (optional)",
  "quick_task_title": "string (optional)",
  "planned_focus_seconds": 1500,
  "planned_break_seconds": 300
}
```

**Response**: `200 OK`
```json
{
  "id": "uuid",
  "status": "FOCUSING",
  "planned_focus_seconds": 1500,
  "planned_break_seconds": 300,
  "started_at": "ISO-8601",
  "expected_end_at": "ISO-8601",
  "total_paused_seconds": 0
}
```
*Errors: 400 Bad Request if an active session already exists.*

### 2. Pause Session
**POST** `/api/v1/focus/pause`

**Response**: `200 OK`
```json
{
  "id": "uuid",
  "status": "PAUSED",
  "paused_at": "ISO-8601",
  "total_paused_seconds": 0
}
```

### 3. Resume Session
**POST** `/api/v1/focus/resume`

**Response**: `200 OK`
```json
{
  "id": "uuid",
  "status": "FOCUSING",
  "total_paused_seconds": 45,
  "expected_end_at": "ISO-8601 (shifted)"
}
```

### 4. Finish Session
**POST** `/api/v1/focus/finish`

**Request Body**:
```json
{
  "outcome": "DONE", // or NEED_MORE_TIME, SKIP, FINISHED_EARLY
  "actual_duration_seconds": 1450,
  "should_replan": true
}
```

**Response**: `200 OK`
```json
{
  "id": "uuid",
  "status": "ENDED",
  "outcome": "DONE",
  "actual_duration_seconds": 1450,
  "ended_at": "ISO-8601"
}
```

### 5. Get Active Session
**GET** `/api/v1/focus/active`

**Response**: `200 OK` (Same schema as Start Session).
*Errors: 404 Not Found if no active session exists.*
