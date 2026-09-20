# API Contract: Assistant Service

## `POST /api/v1/assistant/chat`

Handles all chat interactions, routing them via deterministic rules or LLM cascades based on the input text and context.

### Request Body (`ChatRequest`)

```json
{
  "message": "lên kế hoạch cho tôi 1 tiếng đọc sách và 30 phút nấu ăn",
  "session_id": "optional-uuid-here",
  "current_draft": null // or a TodayDraft / RoadmapDraft object
}
```

### Success Response (`ChatResponse`)

```json
{
  "reply": "Mình đã xếp lịch đọc sách và nấu ăn cho bạn. Bạn xem ổn chưa nhé?",
  "session_id": "auto-generated-or-provided-uuid",
  "intent": "PLAN_DAY",
  "tier": "PARSER",
  "degraded": null,
  "draft": {
    "type": "today",
    "planDate": "2026-09-20",
    "timezone": "Asia/Ho_Chi_Minh",
    "windows": [],
    "tasks": [
      {
        "id": "d1",
        "title": "đọc sách",
        "durationMin": 60,
        "priority": "MEDIUM",
        "importance": "CORE",
        "category": "Learning",
        "estimateSource": "USER",
        "breakAfterMin": 5,
        "schedulingType": "FLEXIBLE",
        "dependencies": [],
        "splittable": false
      },
      {
        "id": "d2",
        "title": "nấu ăn",
        "durationMin": 30,
        "priority": "MEDIUM",
        "importance": "CORE",
        "category": "Personal",
        "estimateSource": "USER",
        "breakAfterMin": 5,
        "schedulingType": "FLEXIBLE",
        "dependencies": [],
        "splittable": false
      }
    ]
  },
  "preview": {
    "timezone": "Asia/Ho_Chi_Minh",
    "blocks": [
        // Scheduled blocks
    ],
    "reality_check": "COMFORTABLE",
    "unscheduled_tasks": [],
    "reasons": {},
    "preview_token": "hmac-signed-token"
  },
  "assumptions": [
    {
      "id": "a-win",
      "kind": "WINDOW",
      "text": "Giả định bạn rảnh 14:00 - 22:00",
      "task_id": null
    }
  ],
  "suggestions": [
    {
      "label": "Lưu kế hoạch",
      "action": "SAVE"
    }
  ],
  "question": null
}
```

### Expected Errors
- `429 Too Many Requests`: `{"detail": "Bạn nhắn hơi nhanh, đợi một chút nhé."}`
- Note: Upstream provider timeouts and budget exhaustion do NOT throw 500/503. They return HTTP 200 with `degraded` set to `LEAN` or `RULES_ONLY`.

---

## `POST /api/v1/assistant/apply-patch`

Applies specific structured edits to an uncommitted draft.

### Request Body

```json
{
  "draft": { /* TodayDraft or RoadmapDraft */ },
  "ops": [
    {
      "op": "update_task",
      "task_id": "d1",
      "duration_min": 45
    }
  ]
}
```

### Success Response

```json
{
  "draft": { /* Updated Draft */ },
  "preview": { /* Updated Scheduler Preview */ }
}
```

---

## `POST /api/v1/assistant/actions/{name}`

Executes whitelisted, explicitly user-triggered intent actions (e.g. `SKIP_OPTIONAL_TODAY`).

### Request Body

```json
{
    // Depends on the action. Mostly empty.
}
```
