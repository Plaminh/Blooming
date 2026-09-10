# SPEC-001: Deterministic Quick Planning Engine

| Field | Value |
|---|---|
| Status | Ready |
| Related requirements/use cases | FR-PLAN-001, FR-PLAN-003, FR-PLAN-004, UC-PLAN-01, UC-PLAN-02 |
| Delivery | Scheduler Increment A and Increment B; no calendar deadline claimed |

## User outcome

The feature accepts a complete structured planning request and returns an honest deterministic preview: exact feasibility, one ordered `PlanBlock[]` timeline containing generated `FOCUS`/`BREAK` blocks and unchanged `FIXED_EVENT` blocks, warnings, and exact unscheduled work.

This increment is domain and API-contract work. The product surface is a Windows/Linux desktop application; the scheduler itself does not depend on UI, weather, or widget presentation.

Increment A covers domain models, validation, interval normalization, feasibility, fixed-Task reservation, and dependency-aware ordering. Increment B covers flexible placement, splitting, breaks, reasons, invariant verification, repeatability, and performance. HTTP/UI integration follows under `PB-003`.

## Scope

Included:

- Validate windows, Tasks, preferences, fixed events, references, dependencies, deadlines, and fixed starts.
- Preserve fixed events as non-Task commitments in output while using clipped/merged copies for capacity calculation.
- Validate and lock fixed Tasks at their fixed start; place flexible Tasks automatically.
- Order dependency-ready Tasks by core/optional group, deadline, priority, and input order.
- Split eligible Tasks and conserve scheduled plus unscheduled duration.
- Calculate exact breaks, buffer, demand, and `COMFORTABLE`/`TIGHT`/`OVERLOADED` status.
- Return stable unscheduled reasons and verify every output invariant.

Excluded from this scheduler increment: HTTP/UI, persistence, Mr. Bloom, FocusRun execution, re-planning, goals/reminders, plant behavior, preferred-time scoring, calendar integration, and solver optimization. These exclusions do not remove required product-MVP work.

## Inputs

| Item | Required data and validation |
|---|---|
| Planning context | Local date, IANA timezone, and one valid available window. |
| Task | Unique ID, title, estimate, priority, optional deadline, core/optional classification, fixed/flexible classification, fixed start when fixed, splitting flag, and direct dependencies. |
| Fixed event | Unique ID, title, start, and end; it is a non-Task commitment. |
| Preferences | `focusDuration` 15–180, `minimumBlockDuration` 1–`focusDuration`, `breakDuration` 0–60, and buffer percentage 0–50. |
| Limits | At most 50 Tasks and 50 fixed events; estimates are 1–1440 minutes. |

A Task shorter than `minimumBlockDuration` may run as one complete shorter `FOCUS` block. A fixed Task requires a fixed start. A flexible Task does not.

## Outputs

| Item | Guarantee |
|---|---|
| Feasibility | Full-request totals and status. Required breaks equal `max(0, expectedFocusBlockCount - 1)`; breaks attributable to unscheduled work count here. |
| Timeline | One ordered `PlanBlock[]` containing `FOCUS`, `BREAK`, and unchanged `FIXED_EVENT` blocks. The frontend must not reconstruct fixed events separately. |
| Unscheduled work | Task ID, exact remaining minutes, stable reason, and safe explanation. |
| Warnings | Stable codes for overload, dependency, deadline, fixed-Task, or fragmentation conditions. |

Reason codes include `INSUFFICIENT_CAPACITY`, `NO_CONTIGUOUS_INTERVAL`, `DEPENDENCY_UNSCHEDULED`, `MINIMUM_BLOCK_NOT_MET`, `DEADLINE_EXCEEDED`, `FIXED_TASK_CONFLICT`, and `FIXED_TASK_OUTSIDE_WINDOW`.

## Deterministic behavior

1. Validate BR-021 and BR-024 input constraints.
2. Convert each fixed event unchanged into a `FIXED_EVENT` PlanBlock; clip/merge copies for occupied capacity.
3. Validate and reserve fixed Tasks as locked `FOCUS` PlanBlock sequences beginning at their fixed start. Reject conflicts without moving them.
4. Derive free intervals around fixed events and locked fixed-Task blocks.
5. Build a stable topological order. Among dependency-ready Tasks in the same core/optional group, earlier deadlines precede later/no deadlines, followed by priority and input order.
6. Derive the expected Focus block count. Calculate full-demand breaks as `max(0, expectedFocusBlockCount - 1)`, then buffer and feasibility.
7. Place flexible Tasks from earliest valid interval without ending any Task block after its deadline.
8. Keep a non-splittable Task whole. Split eligible Tasks at `focusDuration`, respecting `minimumBlockDuration` except for a complete shorter Task; rebalance or return an exact remainder.
9. While work continues, place one explicit `BREAK` between consecutive scheduled `FOCUS` blocks. Do not place a break after the final Focus block. A fixed event neither becomes nor replaces a Break. Do not emit breaks attributable to unscheduled work.
10. Merge generated blocks with unchanged `FIXED_EVENT` blocks, sort the single timeline, verify invariants, and return an immutable result.

## Invariants and acceptance criteria

- [ ] Every generated/locked Focus or Break block lies inside the available window and does not overlap another generated/locked block or fixed event; unchanged fixed events may overlap one another or extend partly beyond the window.
- [ ] Every input fixed event appears unchanged as a `FIXED_EVENT` in the ordered timeline.
- [ ] Scheduled plus unscheduled focus minutes equal every Task estimate.
- [ ] Dependencies finish before dependent work starts.
- [ ] Core Tasks precede optional Tasks when dependency-ready.
- [ ] Earlier deadlines precede later/no deadlines within the same core/optional group; priority and input order break remaining ties.
- [ ] No Task block ends after its deadline; an exact blocked remainder uses `DEADLINE_EXCEEDED`.
- [ ] Fixed Tasks remain locked at their fixed start and are conflict-validated; flexible Tasks are placed automatically; fixed events remain distinct.
- [ ] Non-splittable Tasks remain whole; split blocks obey the focus/minimum rules and the complete-shorter-Task exception.
- [ ] Break demand and emitted Breaks follow BR-030 exactly; buffer is counted but never emitted as a PlanBlock.
- [ ] `COMFORTABLE`, `TIGHT`, and `OVERLOADED` match BR-032.
- [ ] Identical normalized input returns identical ordered output.
- [ ] Invalid input or an invariant failure never returns a successful timeline.

## Rule and quality references

- BR-001–BR-005: PlanBlock integrity, duration conservation, scheduler inputs, and Reality Check.
- BR-021–BR-037: validation, intervals, ordering, splitting, breaks, buffer, feasibility, reasons, repeatability, deadlines, fixed/flexible Tasks, and unified output.
- NFR-PERF-001, NFR-REL-001, NFR-REL-002, NFR-TIME-001, NFR-TIME-002, NFR-MAINT-001, and NFR-TEST-001.

## Edge cases

| Case | Expected behavior |
|---|---|
| No Tasks | `COMFORTABLE`, zero demand, unchanged fixed-event blocks only. |
| Complete Task shorter than minimum | One complete shorter `FOCUS` block when otherwise valid. |
| Fixed events cover window | Events remain in output; positive work is unscheduled. |
| Fragmented non-splittable Task | Whole Task is unscheduled with `NO_CONTIGUOUS_INTERVAL`. |
| Fixed event between Focus blocks | Event stays distinct; a required Break must still occupy a separate valid interval. |
| Deadline prevents completion | No late block; exact remainder is `DEADLINE_EXCEEDED`. |
| Fixed Task conflict/outside window | Do not move it; use `FIXED_TASK_CONFLICT` or `FIXED_TASK_OUTSIDE_WINDOW`. |
| Break for unscheduled work | Count in full-demand feasibility; emit no PlanBlock for it. |
| Overnight window | Use absolute timestamps and the supplied timezone consistently. |

## UI, data, and API impact

- UI is outside this domain increment but must render the returned unified timeline directly.
- Domain data maps to `POST /api/v1/plans/preview` under `PB-003`; see `../../06-architecture/data-api-design.md`.
- This scheduler increment has no persistence side effect.
