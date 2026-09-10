# Use-Case Specification: UC-PLAN-01 Create Daily Plan

| Field | Value |
|---|---|
| Primary actor | User |
| Supporting actors or systems | None for structured input |
| Goal | Receive a realistic, reviewable daily timeline from tasks and time constraints |
| Priority/status | Must — Ready for implementation |

## Description and trigger

The user wants to organize a specific period of one day. The use case begins when the user opens Today and chooses to enter structured planning information.

## Preconditions

- Blooming's planning interface and API are available.
- The user knows the intended available start and end time.
- The user is authenticated; preview is not persisted until accepted.

## Main success flow

1. The user selects the planning date, timezone, available start, and available end.
2. The user adds one or more tasks with title and estimated duration.
3. The user optionally sets priority, deadline, core/optional and fixed/flexible classifications, fixed start time for a fixed Task, splitting settings, dependencies, non-Task fixed events, focus duration, minimum block duration, break duration, and buffer percentage.
4. The user submits the planning request.
5. The system validates field values, references, intervals, limits, and the dependency graph.
6. The system normalizes fixed events, validates and reserves locked fixed-Task `FOCUS` PlanBlocks, and derives ordered free intervals.
7. The system calculates workload, breaks, buffer, demand, and feasibility status.
8. The system orders dependency-ready flexible Tasks by core/optional group, deadline, priority, and input order; places them without exceeding deadlines; and returns one ordered `PlanBlock[]` timeline containing `FOCUS`, `BREAK`, and unchanged `FIXED_EVENT` blocks.
9. The system verifies scheduling invariants and records any unscheduled work and warnings.
10. The system returns the preview without persisting a daily plan.
11. The interface displays feasibility, the timeline, warnings, and unscheduled tasks.
12. The user reviews the result and may later save, edit, or revise it.

## Alternative flows

### AF-01: No tasks

1. At step 2, the user submits an empty task list.
2. The system returns a Comfortable feasibility result with zero workload and an empty timeline.
3. The interface shows an empty-state message rather than an error.

### AF-02: Task can be split

1. At step 8, a splittable task is longer than the focus preference or a free interval.
2. The system creates valid blocks that respect `focusDuration` and `minimumBlockDuration`; a complete Task shorter than the minimum may run as one shorter block.
3. Breaks are inserted according to BR-030 while work remains, never after the final Focus block and never replaced by a fixed event.

### AF-03: Non-splittable task cannot fit

1. At step 8, total capacity may be sufficient but no continuous free interval fits the task.
2. The system leaves the whole task unscheduled with reason `NO_CONTIGUOUS_INTERVAL`.
3. Other eligible tasks may still be scheduled.

### AF-04: Partial valid plan

1. At step 8, only part of the requested work fits without violating rules.
2. The system returns the valid scheduled portion and exact remaining minutes.
3. The interface clearly identifies the result as partial and offers revision.

### AF-05: Overnight window

1. The selected end timestamp is on the following local date.
2. The system treats the timestamp interval as one planning window and evaluates boundaries in the supplied timezone.

### AF-06: Deadline-constrained Task

1. A Task cannot finish by its deadline without violating a higher-order constraint.
2. The system leaves the exact remainder unscheduled with `DEADLINE_EXCEEDED`; no Task block ends after the deadline.

### AF-07: Fixed and flexible Tasks

1. A fixed Task supplies a fixed start time; the system starts its first Focus block at that time and validates and locks the complete Focus/Break sequence.
2. A flexible Task supplies no fixed start and is placed automatically around locked blocks and fixed events.
3. A fixed Task conflict or out-of-window start returns `FIXED_TASK_CONFLICT` or `FIXED_TASK_OUTSIDE_WINDOW` without moving the fixed Task.

## Error flows

### EF-01: Invalid field or time interval

1. Validation at step 5 finds a blank title, non-positive duration, `minimumBlockDuration` outside 1–`focusDuration`, inconsistent fixed/flexible start data, duplicate ID, invalid interval, or exceeded list limit.
2. The system returns `VALIDATION_ERROR` with field-level details.
3. The system does not invoke scheduling or persist data.

### EF-02: Invalid dependency graph

1. Validation finds a missing dependency or a cycle.
2. The system returns `INVALID_DEPENDENCY` or `DEPENDENCY_CYCLE` and identifies involved task IDs.
3. The user corrects the task relationship and resubmits.

### EF-03: Internal invariant failure

1. The generated result violates a scheduler invariant.
2. The system discards the invalid preview, records a correlation ID without personal task text, and returns `SCHEDULING_ERROR`.
3. The interface offers retry and manual correction; no false timeline is displayed.

## Postconditions

- Success: a non-persisted preview exists in the response and satisfies all returned-plan invariants.
- Minimum guarantee on failure: no daily plan is stored and no invalid timeline is presented as successful.

## Business and quality rules

- BR-001–BR-005 and BR-021–BR-037: plan integrity, validation, capacity, scheduling, deadlines, fixed/flexible Tasks, and deterministic output behavior.
- NFR-PERF-001: scheduler p95 target.
- NFR-REL-001–002: invariants and repeatability.
- NFR-TIME-001–002: offset and timezone correctness.
- NFR-USE-002: actionable errors and overload messages.

## Acceptance criteria

- Given valid Tasks and a free window, when the user requests a preview, then every generated/locked Focus or Break block is within the window and does not overlap another generated/locked block or fixed event.
- Given a fixed event that overlaps the window, when a plan is generated, then it appears unchanged as a `FIXED_EVENT` in the single ordered timeline and no generated Focus/Break block overlaps it.
- Given identical normalized input, when preview is requested repeatedly, then the ordered scheduling result is identical.
- Given a splittable task, when fragmentation requires splitting, then scheduled plus unscheduled minutes equals the original estimate.
- Given a non-splittable task without a sufficient continuous interval, when preview runs, then the entire task is returned unscheduled.
- Given invalid input or a dependency cycle, when submitted, then the system returns an actionable error and no preview.
- Given no tasks, when submitted, then the system returns a valid empty Comfortable result.
- Given deadline-ready Tasks in the same core/optional group, when scheduling runs, then earlier deadlines precede later/no deadlines before priority and input-order ties.
- Given valid fixed and flexible Tasks, when scheduling runs, then fixed Task blocks remain locked at the requested start and flexible work is placed automatically.
- Given the expected number of Focus blocks, when feasibility and placement run, then full-demand breaks use `max(0, expectedFocusBlockCount - 1)` and only breaks between consecutive scheduled Focus blocks are emitted.

## Prototype, spec, and tests

- UI: `../../05-ui-ux/ui-ux-design.md`
- Feature spec: `../../07-specifications/001-quick-planning/spec.md`
- Tests: `../../07-specifications/001-quick-planning/tests.md` and `../../08-testing/test-cases-quick-planning.md`
