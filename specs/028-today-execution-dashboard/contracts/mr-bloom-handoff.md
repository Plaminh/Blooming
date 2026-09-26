# Contract: Today to Mr. Bloom Context Handoff

**Feature**: `028-today-execution-dashboard`  
**Date**: 2026-09-26  

---

## 1. URL Navigation Specification

When navigating from Today to Mr. Bloom to adjust a plan or task:

- **Target Route**: `/mr-bloom`
- **Query Parameters**:
  - `date`: ISO date string (`YYYY-MM-DD`). Indicates the plan date being adjusted.
  - `taskId`: (Optional) UUID string of the task selected in Today for adjustment.

### Example URLs
```text
/mr-bloom?date=2026-09-26
/mr-bloom?date=2026-09-26&taskId=550e8400-e29b-41d4-a716-446655440000
```

---

## 2. Mr. Bloom Workspace Initialization Contract

Upon mounting `/mr-bloom` with `date` parameter:

```typescript
interface PlanAdjustmentHandoff {
  date: string;
  taskId?: string;
}
```

### Flow Sequence
1. Check `mrBloomStore.activeDraft`:
   - If `activeDraft` already exists and matches `planDate === date`, retain it.
   - If no draft exists or `activeDraft.planDate !== date`:
     - Fetch persisted plan directly as a lossless draft via `api.get('/today/draft?date=' + date)`.
     - Set `activeDraft` to the fetched `TodayDraft`, `preview` to `null`, `previewMode` to `'today'`.
     - Set `needsReplace` to `false` so saving will trigger the standard explicit confirmation.
2. If `taskId` is provided, highlight or scroll to that task in `TodayDraftPreview`.
3. In Mr. Bloom, user edits (drag/drop, duration adjust, chat instruction) update `TodayDraft` and require fresh scheduler timeline generation before save.
4. Saving posts to `/today/save` with `replace_existing: false` to prompt user if a plan exists, then `replace_existing: true` upon confirmation, navigating back to `/today?date=` + date.
