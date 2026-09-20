# Phase 0 Data Model Changes

## Canonical Schema Migration

To resolve potential circular dependencies between the `assistant` and `today` modules, the shared draft models will be moved to a dedicated module `backend/app/schemas/drafts.py`.

### New Module: `drafts.py`
Will contain the following canonical schemas (migrated from `assistant.py`):
- `MilestoneDraft`
- `RoadmapDraft`
- `AvailabilityWindowDraft`
- `TaskDraft`
- `TodayDraft`

### Updated Imports
- **`backend/app/schemas/assistant.py`**: Will import the above schemas from `drafts.py`.
- **`backend/app/schemas/today.py`**: Will import `TodayDraft` from `drafts.py` instead of `assistant.py`.

This preserves the exact public JSON contract while organizing the backend architecture to prevent circular reference errors.
