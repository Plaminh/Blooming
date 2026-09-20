# API Contract: Goal Integration

## `POST /api/v1/goals/from-roadmap`

Atomically saves a goal and its associated milestones based on a `RoadmapDraft`. This guarantees that if milestone creation fails, the goal creation rolls back, preventing orphaned incomplete goals.

### Request Body (`RoadmapSave`)

```json
{
  "session_id": "optional-uuid-here",
  "draft": {
    "type": "roadmap",
    "goalTitle": "Learn Python",
    "goalDescription": "Master the basics of Python.",
    "targetDate": "2026-10-20",
    "milestones": [
      {
        "id": "m1",
        "title": "Finish syntax tutorial",
        "targetDate": "2026-09-25",
        "expectedOutcome": "Can write loops and functions"
      },
      {
        "id": "m2",
        "title": "Build a CLI app",
        "targetDate": "2026-10-20",
        "expectedOutcome": "Functional app handling arguments"
      }
    ]
  }
}
```

### Success Response

```json
{
  "id": "new-goal-uuid",
  "title": "Learn Python",
  "status": "IN_PROGRESS",
  "target_date": "2026-10-20",
  "milestones": [
    // ... complete milestone DB objects
  ]
}
```

### Expected Errors
- `400 Bad Request`: If milestones target dates are invalid (e.g. past the goal's target date or out of chronological order).
- `500 Internal Server Error`: If atomic save fails.

### Side Effects
- Invokes `reminders_service.sync_milestone_reminder` for each successfully inserted milestone.
- If `session_id` is provided, updates the `PlanningSession.status` to `COMPLETED`.
