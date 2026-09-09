# Test Cases: Deterministic Quick Planning

## 1. Coverage summary

| Feature/use case | Requirements/rules | Planned tests |
|---|---|---:|
| SPEC-001 / UC-PLAN-01 | FR-PLAN-001, FR-PLAN-003, FR-PLAN-004; BR-001–BR-005, BR-021–BR-037 | 25 |
| UC-PLAN-02 overload portion | FR-PLAN-004; BR-003, BR-005, BR-026–BR-033, BR-035–BR-037 | Included in TC-PLAN-005, TC-PLAN-008, TC-PLAN-011, TC-PLAN-022, TC-PLAN-024, TC-PLAN-025 |

Unless overridden, fixtures use `Asia/Ho_Chi_Minh`, start-inclusive/end-exclusive intervals, zero buffer, zero break duration, no fixed events, and valid unique IDs.

## 2. Correctness and boundary cases

### TC-PLAN-001: Empty task list

| Field | Value |
|---|---|
| Type/priority | Domain unit — Critical |
| Input | 09:00–10:00 window; no tasks/events |
| Expected | `COMFORTABLE`; available 60, workload/break/buffer/demand 0; no generated `FOCUS`/`BREAK` blocks, warnings, or unscheduled work |
| Trace | FR-PLAN-003, FR-PLAN-004, BR-032 |

### TC-PLAN-002: Invalid zero or reversed window

| Field | Value |
|---|---|
| Type/priority | Validation unit — Critical |
| Input | Case A: start equals end; Case B: start after end |
| Expected | Reject with `INVALID_TIME_WINDOW`; scheduling is not invoked |
| Trace | FR-PLAN-001, BR-021 |

### TC-PLAN-003: Task exactly fills the window

| Field | Value |
|---|---|
| Type/priority | Domain unit — Critical |
| Input | 09:00–09:50; one non-splittable 50-minute core Task; focus 50, break 0, buffer 0 |
| Expected | `TIGHT`; one `FOCUS` PlanBlock 09:00–09:50; no unscheduled work; all invariants pass |
| Trace | FR-PLAN-003, FR-PLAN-004, BR-001, BR-003, BR-028, BR-032 |

### TC-PLAN-004: Clip and merge fixed events

| Field | Value |
|---|---|
| Type/priority | Interval unit — Critical |
| Input | Window 09:00–12:00; events 08:30–09:30, 09:20–10:00, 11:30–12:30 |
| Expected | Occupied union 90 minutes; available 90; free interval exactly 10:00–11:30; no double counting; all three original events remain unchanged as ordered `FIXED_EVENT` blocks even though two overlap and two extend partly outside the window |
| Trace | FR-PLAN-003, BR-022, BR-023 |

### TC-PLAN-005: Overload preserves exact unscheduled work

| Field | Value |
|---|---|
| Type/priority | Domain unit — Critical |
| Input | 09:00–11:00; core 90-minute non-splittable Task followed by optional 60-minute non-splittable Task; no breaks/buffer |
| Expected | `OVERLOADED`; core Task 09:00–10:30; optional Task unscheduled with 60 remaining minutes; demand 150 and available 120 |
| Trace | FR-PLAN-003, FR-PLAN-004, BR-003, BR-005, BR-026, BR-028, BR-032, BR-033 |

### TC-PLAN-006: Break and buffer calculation

| Field | Value |
|---|---|
| Type/priority | Capacity and placement unit — Critical |
| Input | 09:00–14:00; one 120-minute splittable task; focus 50, minimum 20, break 10, buffer 10% |
| Expected | Focus blocks total 120; two explicit 10-minute `BREAK` blocks; base 140; buffer 14; demand 154; `COMFORTABLE`; no buffer PlanBlock |
| Trace | FR-PLAN-003, FR-PLAN-004, BR-029–BR-032 |

### TC-PLAN-007: Splittable task across a fixed event

| Field | Value |
|---|---|
| Type/priority | Placement unit — Critical |
| Input | Window 09:00–12:00; fixed event 10:00–11:00; 100-minute splittable task; focus 50, minimum 30, break 0 |
| Expected | `FOCUS` PlanBlocks 09:00–09:50 and 11:00–11:50; duration conserved; no overlap |
| Trace | FR-PLAN-003, BR-001–BR-003, BR-022, BR-023, BR-029 |

### TC-PLAN-008: Non-splittable task in fragmented capacity

| Field | Value |
|---|---|
| Type/priority | Placement unit — Critical |
| Input | Window 09:00–12:00; fixed event 10:00–11:00; one 90-minute non-splittable task; total free time 120 |
| Expected | No `FOCUS` PlanBlock; full 90 minutes unscheduled with `NO_CONTIGUOUS_INTERVAL`; capacity and fragmentation explanation remain distinct |
| Trace | FR-PLAN-003, FR-PLAN-004, BR-028, BR-033 |

### TC-PLAN-009: Dependency overrides input order

| Field | Value |
|---|---|
| Type/priority | Ordering unit — Critical |
| Input | Dependent B appears first; B depends on prerequisite A; both 30 minutes; 09:00–10:00 |
| Expected | A scheduled 09:00–09:30; B scheduled 09:30–10:00 |
| Trace | FR-PLAN-003, BR-024, BR-025, BR-027 |

### TC-PLAN-010: Dependency cycle is rejected

| Field | Value |
|---|---|
| Type/priority | Validation unit — Critical |
| Input | A depends on B; B depends on A |
| Expected | Reject with `DEPENDENCY_CYCLE`; response identifies A and B; no successful PlanBlock timeline returned |
| Trace | FR-PLAN-001, BR-024 |

### TC-PLAN-011: Core Task precedes higher-priority optional Task

| Field | Value |
|---|---|
| Type/priority | Ordering/overload unit — Critical |
| Input | 60-minute window; optional High Task 60 appears first; core Low Task 60 appears second |
| Expected | Core Low Task is scheduled; optional High Task remains unscheduled for 60 minutes |
| Trace | FR-PLAN-003, FR-PLAN-004, BR-026, BR-027, BR-033 |

### TC-PLAN-012: Rebalance a small final remainder

| Field | Value |
|---|---|
| Type/priority | Chunking unit — High |
| Input | 100-minute splittable Task; `focusDuration` 60; `minimumBlockDuration` 30; enough continuous time; `breakDuration` 0 |
| Expected | Deterministic valid chunks of 60 and 40 minutes; no chunk below 30; total exactly 100 |
| Trace | FR-PLAN-003, BR-003, BR-029 |

### TC-PLAN-013: Buffer is capacity, not a PlanBlock

| Field | Value |
|---|---|
| Type/priority | Capacity unit — High |
| Input | One 50-minute task; focus 50; buffer 20%; enough window |
| Expected | Buffer 10 minutes, demand 60; exactly one 50-minute `FOCUS` PlanBlock and no Buffer PlanBlock |
| Trace | FR-PLAN-003, FR-PLAN-004, BR-031, BR-032 |

### TC-PLAN-014: Deterministic repeatability

| Field | Value |
|---|---|
| Type/priority | Repeatability — Critical |
| Input | A fixture with equal-priority tasks, dependencies, fixed events, splitting, and breaks |
| Steps | Normalize one immutable request; call scheduler 100 times |
| Expected | Every ordered feasibility/PlanBlock/unscheduled/warning result is exactly equal |
| Trace | FR-PLAN-003, BR-025, BR-027, BR-034, NFR-REL-002 |

### TC-PLAN-015: Missing dependency reference

| Field | Value |
|---|---|
| Type/priority | Validation unit — Critical |
| Input | Task A depends on unknown ID `missing` |
| Expected | Reject with `INVALID_DEPENDENCY` identifying A and `missing`; no scheduling |
| Trace | FR-PLAN-001, BR-024 |

### TC-PLAN-016: Supported list limit

| Field | Value |
|---|---|
| Type/priority | Validation boundary — High |
| Input | Case A: 50 valid tasks; Case B: 51 valid tasks |
| Expected | Case A is accepted; Case B returns a limit validation error before scheduling |
| Trace | FR-PLAN-001, BR-021 |

### TC-PLAN-017: Maximum-input performance

| Field | Value |
|---|---|
| Type/priority | Performance — High |
| Input | 50 tasks, 50 fixed events, valid acyclic dependencies, mixed splitting/priority |
| Steps | Warm up consistently; record at least 100 scheduler executions on the reference environment |
| Expected | p95 at most 500 ms; all executions also pass invariant assertions |
| Trace | BR-021, NFR-PERF-001, NFR-REL-001 |

### TC-PLAN-018: Window crosses local midnight

| Field | Value |
|---|---|
| Type/priority | Time boundary — Critical |
| Input | Planning date 9 Sep, timezone `Asia/Ho_Chi_Minh`, window 23:30 on 9 Sep to 01:00 on 10 Sep; 60-minute task |
| Expected | Request is valid; generated PlanBlock stays inside the absolute interval; local date/time serialization retains explicit offsets and plan timezone |
| Trace | FR-PLAN-001, FR-PLAN-003, BR-001, BR-023, NFR-TIME-001, NFR-TIME-002 |

### TC-PLAN-019: Minimum block validates against focus duration

| Field | Value |
|---|---|
| Type/priority | Validation boundary — Critical |
| Input | Case A: focus 50, minimum block 50; Case B: focus 50, minimum block 51; Task estimate 120 |
| Expected | Case A is valid; Case B is rejected before scheduling even though the Task estimate exceeds 51 |
| Trace | FR-PLAN-001, BR-021 |

### TC-PLAN-020: Complete Task shorter than minimum block

| Field | Value |
|---|---|
| Type/priority | Chunking boundary — Critical |
| Input | Focus 50, minimum block 20; one complete 10-minute flexible Task; sufficient time |
| Expected | One 10-minute `FOCUS` PlanBlock is returned; it is not rejected with `MINIMUM_BLOCK_NOT_MET` |
| Trace | FR-PLAN-003, BR-029 |

### TC-PLAN-021: Unified timeline preserves fixed events

| Field | Value |
|---|---|
| Type/priority | Output contract — Critical |
| Input | Window 09:00–12:00; fixed event with exact ID/title/timestamps 10:00–10:30; flexible Tasks around it |
| Expected | One ordered `PlanBlock[]` contains `FOCUS`, any required `BREAK`, and one byte-equivalent `FIXED_EVENT`; the frontend needs no separate event merge |
| Trace | FR-PLAN-003, BR-002, BR-022, BR-037 |

### TC-PLAN-022: Deadline order and latest finish

| Field | Value |
|---|---|
| Type/priority | Ordering and placement — Critical |
| Input | Dependency-ready core Tasks: Low priority due 10:00, High priority due 11:00, High priority with no deadline; constrained window |
| Expected | Earlier deadline is considered first, then later deadline, then no deadline; no block ends after its Task deadline and exact blocked remainder is `DEADLINE_EXCEEDED` |
| Trace | FR-PLAN-001, FR-PLAN-003, BR-027, BR-033, BR-035 |

### TC-PLAN-023: Fixed and flexible Task placement

| Field | Value |
|---|---|
| Type/priority | Placement — Critical |
| Input | Fixed core Task at 10:00 and flexible core Task in a 09:00–12:00 window |
| Expected | Fixed Task produces a locked `FOCUS` sequence beginning at 10:00; flexible Task is placed automatically around locked blocks |
| Trace | FR-PLAN-001, FR-PLAN-003, BR-036 |

### TC-PLAN-024: Fixed Task conflict and re-plan preservation

| Field | Value |
|---|---|
| Type/priority | Conflict/recovery — Critical |
| Input | Case A: fixed Task overlaps a fixed event; Case B: fixed Task starts outside the window; Case C: re-plan with a valid future fixed-Task block |
| Expected | A returns `FIXED_TASK_CONFLICT`; B returns `FIXED_TASK_OUTSIDE_WINDOW`; C preserves the locked fixed-Task block unchanged while adjusting only flexible future work |
| Trace | FR-PLAN-003, FR-REPLAN-001, BR-008, BR-033, BR-036, NFR-REL-005 |

### TC-PLAN-025: Exact break demand and emission policy

| Field | Value |
|---|---|
| Type/priority | Feasibility and placement — Critical |
| Input | Full request needs four expected Focus blocks, but only two Focus blocks schedule; a fixed event lies between them; break duration 10 |
| Expected | Full demand counts three breaks; output emits exactly one distinct 10-minute `BREAK` between the two scheduled Focus blocks while work continues, emits none after the final Focus block, and does not treat the fixed event as a Break |
| Trace | FR-PLAN-003, FR-PLAN-004, BR-030–BR-032, BR-037 |

## 3. Common postconditions

For every successful case:

- PlanBlocks are sorted and use positive durations.
- Window and overlap invariants pass for generated/locked blocks; fixed events are unchanged output blocks and may overlap one another or extend partly beyond the window.
- Task duration is conserved.
- Deadline, fixed-Task lock, Break placement, duration, and Task-reference invariants pass.
- Unscheduled reason codes are stable.
- Input objects remain unchanged.

For every rejected case:

- No partial successful result is exposed.
- No persistence or external side effect occurs.
- The error identifies a stable code and recoverable details without logging full task content.

## 4. Review checklist

- [x] Main, alternative, error, and recovery flows are represented.
- [x] Boundary values and overnight time behavior are included.
- [x] Expected results are specific and observable.
- [x] Every case traces to a requirement, rule, risk, or specification.
- [ ] Replace planned test identifiers with executable test method links after implementation.
- [ ] Record actual results in a separate test execution report; do not edit expected results to match faulty code.
