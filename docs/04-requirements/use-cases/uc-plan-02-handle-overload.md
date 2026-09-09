# Use-Case Specification: UC-PLAN-02 Handle Overloaded Plan

| Field | Value |
|---|---|
| Primary actor | User |
| Supporting actors or systems | None |
| Goal | Understand why work cannot fit and revise the request without losing control |
| Priority/status | Must — Product flow defined; implementation not yet claimed complete |

## Description and trigger

This use case extends Quick Plan when calculated demand exceeds available capacity or when fragmentation, a deadline, or a fixed-Task conflict prevents all requested work from being placed.

## Preconditions

- The user submitted a structurally valid planning request.
- Capacity calculation or scheduling produced unscheduled work.
- The system retained the original request locally in the interface for revision.

## Main success flow

1. The system displays the feasibility status, available minutes, workload, breaks, buffer, and demand.
2. The system displays every unscheduled Task or remaining duration with a reason, including deadline and fixed-Task conflicts where applicable.
3. The system identifies optional work after core work and does not pretend the request fits.
4. The user chooses one or more recovery actions: remove an optional task, reduce scope/duration, keep only the core outcome, move work to another day, select the highest priority, or explicitly adjust plan inputs.
5. The system updates the structured request and shows exactly what changed.
6. The user requests a revised preview.
7. The system validates and schedules the revised request using UC-PLAN-01.
8. The interface displays the revised feasibility and timeline.
9. The user accepts the result or makes another explicit revision.

## Alternative flows

### AF-01: Keep an overloaded partial plan

1. The user decides not to remove or shorten work.
2. The system allows the user to retain the partial preview for review.
3. Unscheduled work and overload warnings remain visible and are not converted into `FOCUS` PlanBlocks.

### AF-02: Fragmentation without total overload

1. Demand is within total available capacity, but a non-splittable task cannot fit any free interval.
2. The system explains `NO_CONTIGUOUS_INTERVAL` rather than reporting a false capacity shortage.
3. The user may permit splitting, change event/window timing, or defer the task.

### AF-03: Optional work is deferred before core work

1. The user chooses an automatic “fit core work first” action.
2. The system retains core Tasks and marks optional Tasks for deferral in deterministic priority order.
3. The user reviews the proposed removal before regeneration.

## Error flows

### EF-01: Revision creates invalid input

1. The user sets an invalid duration, interval, preference, or dependency.
2. The system returns field-level validation and preserves the last valid preview.

### EF-02: Revised request remains overloaded

1. Scheduling still produces overload or unscheduled work.
2. The system displays the new calculation and remaining gap.
3. The user may revise again or keep the partial plan.

## Postconditions

- Success: the user receives a revised valid preview with transparent feasibility and any remaining unscheduled work.
- Minimum guarantee on failure: the last valid preview and original task durations remain recoverable; no duration is silently discarded.

## Business and quality rules

- BR-003: scheduled plus unscheduled minutes preserve Task duration.
- BR-005: overload is explicit and offers feasible alternatives.
- BR-026–BR-033: core-first ordering, placement, splitting, breaks/buffer, feasibility, and fragmentation behavior.
- BR-035–BR-037: deadline, fixed/flexible Task, and unified PlanBlock-timeline behavior.
- NFR-USE-002: explanation includes the affected work and a recovery action.

## Acceptance criteria

- Given demand greater than capacity, when preview completes, then status is Overloaded and exact unscheduled work is displayed.
- Given optional and core Tasks, when capacity is insufficient, then optional Tasks are considered after core Tasks.
- Given fragmented capacity, when a non-splittable task cannot fit, then the reason distinguishes fragmentation from total-capacity overload.
- Given a Task cannot finish by its deadline or a fixed Task conflicts, then the exact remainder and stable deadline/fixed-Task reason are displayed without moving locked work.
- Given a valid user revision, when preview is regenerated, then calculations and timeline reflect only explicit changes.
- Given an invalid revision, when submitted, then the last valid preview is preserved.

## Prototype, spec, and tests

- UI: `../../05-ui-ux/ui-ux-design.md`
- Quick planning spec: `../../07-specifications/001-quick-planning/spec.md`
- Dedicated overload feature specification: planned before overload-control implementation; no sprint number is assumed.
- Tests: Quick Planning overload cases are listed in `../../08-testing/test-cases-quick-planning.md`.
