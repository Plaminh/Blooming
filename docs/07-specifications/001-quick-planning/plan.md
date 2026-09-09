# Technical Plan: SPEC-001 Deterministic Quick Planning Engine

## Approach

Implement the scheduler as pure Java domain code. One immutable request produces feasibility, one ordered `PlanBlock[]`, warnings, and exact unscheduled work. Domain code has no HTTP, database, UI, clock, LLM, or filesystem dependency.

## Delivery increments

| Increment | Work | Exit evidence |
|---|---|---|
| A | Models, input/dependency validation, fixed-event normalization, fixed-Task reservation, free intervals, feasibility, and stable ordering | Validation, interval, fixed-Task, deadline-order, and feasibility tests pass. |
| B | Flexible placement, splitting, precise breaks, unscheduled reasons, unified output, invariant verification, repeatability, and performance | All SPEC-001 cases and common invariant assertions pass. |

## Components

| Package | Responsibility |
|---|---|
| `planning/domain/model` | Immutable Task, fixed event, preference, interval, PlanBlock, feasibility, warning, and unscheduled-work values. |
| `planning/domain/validation` | BR-021/BR-024 validation, deadline/fixed-start consistency, and fixed-Task conflict reporting. |
| `planning/domain/time` | Half-open interval operations, occupied-union calculation, free intervals, and ordered timeline merge. |
| `planning/domain/feasibility` | Expected Focus blocks, required breaks, buffer, demand, and feasibility status. |
| `planning/domain/scheduling` | Fixed-Task reservation, stable ordering, deadline-aware flexible placement, splitting, and Break placement. |
| `planning/domain/verification` | Window, overlap, unchanged fixed event, duration, dependency, deadline, lock, break, and ordering invariants. |

## Input validation

- `minimumBlockDuration` is 1–`focusDuration`, independent of Task estimate.
- A complete Task shorter than the minimum remains valid and may form one complete shorter block.
- A fixed Task must have `fixedStart`; a flexible Task must not use a fixed start to bypass automatic placement.
- A deadline is optional but, when present, must permit every returned block to finish at or before it.
- Fixed events are non-Task commitments with valid start/end and remain unchanged in output.

## Interval and fixed-block preparation

1. Validate fixed events, clip copies to the available window, sort, and merge the occupied union for capacity.
2. Create an unchanged `FIXED_EVENT` PlanBlock for every input fixed event.
3. Build fixed-Task Focus block sequences beginning at `fixedStart`, including required Breaks between its consecutive Focus blocks while work continues.
4. Validate fixed-Task blocks against the window, deadline, fixed events, other locked blocks, and overlap. Return a stable fixed-Task reason instead of moving them.
5. Derive free intervals around valid fixed events and locked fixed-Task blocks.

## Ordering

Use a stable topological ready queue with this comparator:

1. Core before optional.
2. Earlier deadline before later deadline; any deadline before no deadline.
3. Priority `HIGH`, `MEDIUM`, `LOW`.
4. Original input position.

A dependent Task becomes ready only after prerequisites are fully scheduled. Fixed Tasks remain locked; the comparator orders flexible Tasks and determines deterministic consideration of otherwise eligible work.

## Focus blocks and deadlines

- Non-splittable work occupies one continuous interval or remains wholly unscheduled.
- Splittable work uses blocks no longer than `focusDuration` and normally no shorter than `minimumBlockDuration`.
- If the complete Task estimate is shorter than `minimumBlockDuration`, emit one complete shorter block when it otherwise fits.
- Rebalance a too-small final remainder when possible; otherwise return it with `MINIMUM_BLOCK_NOT_MET`.
- Never place a Task block whose end exceeds its deadline. Return the exact remainder with `DEADLINE_EXCEEDED`.

## Break and feasibility algorithm

```text
expectedFocusBlockCount = number of Focus blocks needed for the full request
requiredBreakCount = max(0, expectedFocusBlockCount - 1)
requiredBreakMinutes = requiredBreakCount * breakDuration
baseDemand = workloadMinutes + requiredBreakMinutes
bufferMinutes = ceil(baseDemand * bufferPercentage / 100)
demandMinutes = baseDemand + bufferMinutes
```

For placement, emit one explicit `BREAK` between consecutive scheduled `FOCUS` blocks while work continues. Emit no Break after the final Focus block. Fixed events neither become nor replace Breaks. Breaks attributable to work that remains unscheduled stay in full-request feasibility but are not emitted.

## Output and verification

Merge generated `FOCUS`/`BREAK` blocks and unchanged `FIXED_EVENT` blocks, then sort by start, end, stable type/order key, and sequence. The verifier checks:

1. One ordered PlanBlock timeline and valid positive durations.
2. Available-window containment for generated/locked blocks and no overlap between those blocks or a fixed event; overlapping/partly external fixed events remain unchanged.
3. Byte-equivalent fixed-event fields from input to output.
4. Task duration conservation and dependency completion.
5. Deadline latest-finish and fixed-Task lock invariants.
6. Break count/position rules and absence of a final Break.
7. Stable warnings, reasons, and deterministic output.

The frontend consumes this timeline directly and must not reconstruct fixed events separately.

## Error and reason handling

Invalid request structure returns typed validation errors before scheduling. Placement returns exact remaining minutes using `INSUFFICIENT_CAPACITY`, `NO_CONTIGUOUS_INTERVAL`, `DEPENDENCY_UNSCHEDULED`, `MINIMUM_BLOCK_NOT_MET`, `DEADLINE_EXCEEDED`, `FIXED_TASK_CONFLICT`, or `FIXED_TASK_OUTSIDE_WINDOW`. Internal invariant failure returns no partial successful result.

## Testing and rollout

- Unit and table-driven tests cover validation, intervals, ordering, deadlines, fixed Tasks, splitting, breaks, and reasons.
- Property tests assert unified-timeline invariants for generated valid inputs.
- Repeatability runs the same immutable request at least 100 times.
- Performance uses the supported 50-Task/50-fixed-event fixture.
- API and UI mapping follow under `PB-003`; no database migration or production rollout belongs to these scheduler increments.
