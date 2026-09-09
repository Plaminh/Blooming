# Feature Tests: SPEC-001 Deterministic Quick Planning Engine

## Coverage map

| Rules or criterion | Planned tests |
|---|---|
| BR-001–BR-003, containment/non-overlap/duration conservation | TC-PLAN-003, TC-PLAN-005, TC-PLAN-007, TC-PLAN-008, TC-PLAN-011, TC-PLAN-012 |
| BR-005, BR-032–BR-033, Reality Check/reasons | TC-PLAN-001, TC-PLAN-003, TC-PLAN-005, TC-PLAN-006, TC-PLAN-008, TC-PLAN-022, TC-PLAN-024 |
| BR-021, ranges and minimum-block validation | TC-PLAN-002, TC-PLAN-016, TC-PLAN-017, TC-PLAN-019 |
| BR-022–BR-023, fixed-event normalization and intervals | TC-PLAN-004, TC-PLAN-007, TC-PLAN-018, TC-PLAN-021 |
| BR-024–BR-027, dependencies/core/deadline/stable order | TC-PLAN-009, TC-PLAN-010, TC-PLAN-011, TC-PLAN-014, TC-PLAN-015, TC-PLAN-022 |
| BR-028–BR-029, splitting and complete-shorter-Task behavior | TC-PLAN-007, TC-PLAN-008, TC-PLAN-012, TC-PLAN-020 |
| BR-030–BR-031, precise breaks and buffer | TC-PLAN-006, TC-PLAN-013, TC-PLAN-025 |
| BR-034, repeatability | TC-PLAN-014 |
| BR-035, deadline latest finish | TC-PLAN-022 |
| BR-036, fixed/flexible Tasks | TC-PLAN-023, TC-PLAN-024 |
| BR-037, unified PlanBlock output | TC-PLAN-021, TC-PLAN-025 |
| NFR-PERF-001 | TC-PLAN-017 |
| NFR-TIME-002 | TC-PLAN-018 |

Detailed data and expected results are in `../../08-testing/test-cases-quick-planning.md`.

## Test layers

| Layer | Scope |
|---|---|
| Value/domain unit | Input ranges, interval math, feasibility, ordering, deadlines, fixed Tasks, splitting, breaks, placement, and reasons. |
| Invariant/property | Window, overlap, unchanged fixed events, duration, dependency, deadline, lock, and Break invariants. |
| Repeatability/performance | Identical output across repeated calls and the supported maximum fixture. |
| API/UI | Planned under `PB-003`; validates direct consumption of the unified PlanBlock timeline. |

## Common invariant assertion

Every successful scheduler test verifies:

1. One `PlanBlock[]` is ordered by time and stable sequence.
2. Every generated/locked PlanBlock has positive duration, lies in the available window, and does not overlap another generated/locked block or fixed event; unchanged fixed events may overlap one another or extend partly beyond the window.
3. Every fixed event appears exactly once and unchanged as `FIXED_EVENT`; no frontend reconstruction is needed.
4. Scheduled plus unscheduled focus minutes equal each Task estimate.
5. Dependencies finish before dependents and no Task block ends after its deadline.
6. Fixed-Task Focus blocks remain locked at their validated time; flexible Tasks are scheduler-placed.
7. `minimumBlockDuration` is bounded by `focusDuration`; a complete shorter Task is allowed under BR-029.
8. Full-demand Break count is `max(0, expectedFocusBlockCount - 1)`. Emitted Breaks occur only between consecutive scheduled Focus blocks while work continues, never after the final Focus block, and never by retyping a fixed event.
9. Breaks attributable to unscheduled work affect feasibility but do not appear in the timeline.
10. Buffer minutes affect feasibility but do not appear as a PlanBlock.

## Planned boundary coverage

- Empty Tasks, invalid/reversed/overnight windows, and maximum list sizes.
- Exact feasibility thresholds and deterministic repeatability.
- Fixed events outside, partially inside, adjacent, overlapping, and preserved in output.
- Dependency chains, missing references, cycles, core/optional, deadline, priority, and input-order ties.
- Non-splittable Tasks, split remainders, minimum/focus validation, and complete-shorter-Task exception.
- Deadline latest finish and `DEADLINE_EXCEEDED`.
- Fixed Task success, conflict, out-of-window, and re-plan preservation.
- Break count, final Focus, fixed-event non-substitution, and unscheduled-work feasibility behavior.

## Exit criteria

- All planned TC-PLAN-001–TC-PLAN-025 correctness cases pass across Increment A and Increment B.
- Repeatability TC-PLAN-014 passes for 100 executions.
- TC-PLAN-017 records a performance measurement.
- No invariant failure becomes a partial success.
- Code, rules, API contract, and test expectations agree before the scheduler increment is reported complete.
