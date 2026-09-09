# Tasks: SPEC-001 Deterministic Quick Planning Engine

## Delivery goal

Implement a pure Python scheduler in two evidence-producing increments. No completion date or completed status is claimed.

## Increment A — domain preparation and ordering

| ID | Task | Dependency | Completion check | Status |
|---|---|---|---|---|
| T-001 | Create immutable request/result, Task classification/deadline/fixed-start, PlanBlock, and interval domain types | Project initialization | Types compile and protect invalid construction | To Do |
| T-002 | Validate windows, fields, limits, IDs, `minimumBlockDuration <= focusDuration`, and fixed-start classification | T-001 | BR-021 tests pass, including the complete-shorter-Task exception | To Do |
| T-003 | Validate dependency references/cycles and implement stable ordering by core group, deadline, priority, and input order | T-001, T-002 | BR-024, BR-025, BR-027, and BR-035 tests pass | To Do |
| T-004 | Preserve fixed events as output blocks; clip/merge copies and derive half-open free intervals | T-001 | BR-022, BR-023, and BR-037 tests pass | To Do |
| T-005 | Validate and reserve locked fixed-Task Focus sequences | T-001–T-004 | BR-036 conflict, deadline, window, and lock tests pass | To Do |
| T-006 | Calculate expected Focus blocks, exact full-demand breaks, buffer, demand, and feasibility | T-001, T-004, T-005 | BR-030–BR-032 tests pass | To Do |
| T-007 | Run Increment A checks and update affected documentation | T-001–T-006 | All Increment A acceptance tests pass | To Do |

## Increment B — placement and verification

| ID | Task | Dependency | Completion check | Status |
|---|---|---|---|---|
| T-008 | Implement deadline-aware core-first flexible-Task consideration | Increment A | BR-026, BR-027, and BR-035 tests pass | To Do |
| T-009 | Implement non-splittable earliest-fit placement | T-003–T-005, T-008 | BR-028 tests pass | To Do |
| T-010 | Implement splittable placement and deterministic remainder rebalance | T-003–T-006, T-008 | BR-029 and duration-conservation tests pass | To Do |
| T-011 | Place explicit Breaks using the exact full-demand/emission policy | T-006, T-010 | BR-030 tests cover final-block, fixed-event, and unscheduled-work cases | To Do |
| T-012 | Map capacity, fragmentation, dependency, deadline, and fixed-Task reasons with exact remaining minutes | T-009–T-011 | BR-003, BR-033, BR-035, and BR-036 tests pass | To Do |
| T-013 | Merge generated blocks and unchanged fixed events into one ordered timeline | T-004, T-009–T-012 | BR-037 and frontend-contract tests pass | To Do |
| T-014 | Implement final invariant verifier | T-009–T-013 | Window, overlap, duration, dependency, deadline, lock, break, and fixed-event checks pass | To Do |
| T-015 | Add repeatability and supported-maximum performance tests | T-014 | BR-034 and NFR-PERF-001 evidence is recorded | To Do |
| T-016 | Run Increment B checks and update affected documentation | T-008–T-015 | Full scheduler suite passes | To Do |

## Scope control

- This feature increment does not implement REST/UI, persistence, Mr. Bloom, FocusRun, re-planning, goals/reminders, or plant behavior; those remain required product-MVP work.
- Do not add learned estimates, preferred-time scoring, randomization, solver libraries, calendar integration, or AI scheduling authority.
- A new edge case must be expressed as a test and resolved with the smallest rule-consistent behavior.

## Related backlog

| Work | Backlog ID |
|---|---|
| Preview API and structured planning UI | `PB-003` |
| Overload recovery controls | `PB-004` |
| Save and retrieve Daily Plans | `PB-005` |
| Mr. Bloom conversational interpretation | `PB-006` |
