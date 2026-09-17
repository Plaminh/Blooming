# API Contracts: Statistics

## GET /api/v1/statistics/summary

**Query Parameters:**
- `start_date` (ISO 8601 string, inclusive, YYYY-MM-DD)
- `end_date` (ISO 8601 string, inclusive, YYYY-MM-DD)
- `timezone` (string, e.g., 'America/New_York')

**Response:** `200 OK`
```json
{
  "study_time_hours": 12,
  "study_time_minutes": 30,
  "study_day_count": 5,
  "completed_plan_count": 4,
  "unfinished_plan_count": 1
}
```

## GET /api/v1/statistics/daily

**Query Parameters:**
- `start_date` (ISO 8601 string, inclusive)
- `end_date` (ISO 8601 string, inclusive)
- `timezone` (string)

**Response:** `200 OK`
```json
[
  {"day_label": "Mon", "hours": 2.5, "date": "2026-09-14"},
  {"day_label": "Tue", "hours": 0.0, "date": "2026-09-15"}
]
```
Note: Dates with 0 activity must be filled out for the continuous range.

## GET /api/v1/statistics/plan-history

**Query Parameters:**
- `start_date` (ISO 8601 string, inclusive)
- `end_date` (ISO 8601 string, inclusive)
- `status` (string: "All", "Completed", "Unfinished")
- `page` (integer, default 1, min 1)
- `page_size` (integer, default 4, min 1, max 50)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "date_label": "2026-09-17",
      "plan_name": "Daily Plan",
      "completed_tasks": 3,
      "total_tasks": 5,
      "status": "Completed"
    }
  ],
  "total_items": 12,
  "total_pages": 3,
  "current_page": 1,
  "items_per_page": 4
}
```
