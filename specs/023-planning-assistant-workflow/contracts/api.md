# API Contracts

## `POST /assistant/chat`
*Context-aware assistant interaction.*
**Request Body**:
```json
{
  "message": "Move my coding task to tomorrow",
  "history": [],
  "session_id": "uuid-here",
  "current_draft": {
    "type": "today",
    "planDate": "2026-09-19",
    "timezone": "UTC",
    "windows": [{"start": "09:00", "end": "17:00"}],
    "tasks": [
      {
        "id": "draft-task-1",
        "title": "Coding Task",
        "durationMin": 60,
        "priority": "HIGH",
        "deadline": null,
        "schedulingType": "FLEXIBLE",
        "fixedStart": null,
        "fixedEnd": null,
        "dependencies": [],
        "splittable": false
      }
    ]
  }
}
```
**Response**:
```json
{
  "reply": "I've moved the coding task. Anything else?",
  "intent": "edit_draft",
  "missing_fields": [],
  "draft": {
    "type": "today",
    ...
  }
}
```

## `POST /today/preview`
*Run deterministic scheduler over a draft without saving to the DB.*
**Request Body**:
```json
{
  "draft": {
    "type": "today",
    "planDate": "2026-09-19",
    "timezone": "UTC",
    "windows": [{"start": "09:00", "end": "17:00"}],
    "tasks": [ ... ]
  }
}
```
**Response**:
```json
{
  "status": "PREVIEW",
  "plan_date": "2026-09-19",
  "timezone": "UTC",
  "preview_token": "abc123sha256hash...",
  "blocks": [
    {
      "id": "uuid-here",
      "block_type": "TASK",
      "planned_start_at": "2026-09-19T09:00:00Z",
      "planned_end_at": "2026-09-19T10:00:00Z",
      "title": "Coding Task",
      "task_id": "temp-uuid",
      "draft_task_id": "draft-task-1",
      "position": 0,
      "status": "PLANNED",
      "is_locked": false
    }
  ],
  "unscheduled_tasks": [],
  "reality_check": "COMFORTABLE",
  "reasons": []
}
```

## `POST /today/save`
*Atomically persist a Today draft as a DailyPlan and Tasks.*
**Request Body**:
```json
{
  "session_id": "uuid-here",
  "preview_token": "abc123sha256hash...",
  "draft": { ... }
}
```
**Response**: Returns the fully saved TodayResponse.
