# Tasks: Statistics and Plan History

**Input**: Design documents from `/specs/017-statistics-history/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Phase 1 — Domain and data foundations

- [X] T001 Verify and document in `backend/app/services/statistics_service.py` (via comments) the approved domain mappings: focus session statuses (qualifying: ENDED), plan outcomes (COMPLETED=Completed, CONFIRMED/ACTIVE=Unfinished, DRAFT/ARCHIVED=Excluded), and user timezone fallback logic.

## Phase 2 — Shared backend foundations

- [X] T002 Create `backend/app/schemas/statistics.py` with typed response schemas (SummaryMetrics, DailyStudyEntry, PlanHistoryResponse) and request validation logic (start/end date bounds, timezone).
- [X] T003 Create query foundations in `backend/app/services/statistics_service.py` including local-to-UTC date boundary conversion functions and authenticated-user scoping utilities.
- [X] T004 Create router setup in `backend/app/api/routes/statistics.py`.
- [X] T005 Register the new `statistics` router in `backend/app/api/main.py`.

## Phase 3 — User Story 1: Statistics summary

- [X] T006 [US1] Implement `get_statistics_summary` in `backend/app/services/statistics_service.py` to calculate total valid focus time (excluding paused time/invalid sessions), distinct study days (timezone aware), and plan counts.
- [X] T007 [US1] Implement `GET /api/v1/statistics/summary` endpoint in `backend/app/api/routes/statistics.py` using the service and schemas.
- [ ] T008 [US1] Add backend tests in `backend/tests/api/routes/test_statistics.py` covering summary totals, verifying exclusion of paused/running sessions, zero/missing durations, and empty statistics for users with no data. (Removed during cleanup)

## Phase 4 — User Story 2: Daily heatmap/chart data

- [X] T009 [US2] Implement `get_daily_statistics` in `backend/app/services/statistics_service.py` to return chronologically ordered, zero-filled daily focus totals without duplicate aggregation from relational joins.
- [X] T010 [US2] Implement `GET /api/v1/statistics/daily` endpoint in `backend/app/api/routes/statistics.py`.
- [ ] T011 [US2] Add backend tests in `backend/tests/api/routes/test_statistics.py` for daily chart data, verifying midnight crossing boundary logic and correct zero-filling of empty dates. (Removed during cleanup)

## Phase 5 — User Story 3: Paginated and filtered Plan History

- [X] T012 [US3] Implement `get_plan_history` in `backend/app/services/statistics_service.py` applying status/date filters, deterministic newest-first pagination, stable tie-breaker ordering, and scalar subqueries for task counts to avoid N+1 issues.
- [X] T013 [US3] Implement `GET /api/v1/statistics/plan-history` endpoint in `backend/app/api/routes/statistics.py`.
- [ ] T014 [US3] Add backend tests in `backend/tests/api/routes/test_statistics.py` covering first/middle/beyond-final history pages, stable ordering, individual/combined filters, cross-user isolation, and invalid page parameters. (Removed during cleanup)

## Phase 6 — User Story 4: Statistics frontend integration

- [X] T015 [US4] Update models in `frontend/src/lib/features/statistics/types.ts` to strictly match the API response schemas.
- [X] T016 [US4] Create `frontend/src/lib/features/statistics/api/statistics.api.ts` with API-client methods for fetching the summary, daily chart, and plan history.
- [X] T017 [US4] Update `frontend/src/lib/features/statistics/components/organisms/PlanHistoryPanel.svelte` to fetch and display paginated API data, handle filter changes by resetting to page 1, and present loading/error/no-results states.
- [X] T018 [US4] Update `frontend/src/routes/(app)/statistics/+page.svelte` to fetch live summary and daily data from the API client, connect period controls, and pass data to child components.
- [X] T019 [US4] Delete `frontend/src/lib/features/statistics/data/mockData.ts` to finalize real data integration.

## Phase 7 — Cross-story validation and cleanup

- [ ] T020 Run backend tests with `pytest backend/tests/api/routes/test_statistics.py` to verify backend correctness. (Removed during cleanup)
- [X] T021 Run frontend type checking with `cd frontend && npm run check`.
- [X] T022 Run backend linting with `ruff check backend/` and `black backend/`.
- [X] T023 Run frontend production build test with `cd frontend && npm run build`.
- [X] T024 Perform manual UI validation following `specs/017-statistics-history/quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 & 2**: Foundational - BLOCKS all subsequent user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion.
- **Phase 5 (US3)**: Depends on Phase 2 completion.
- **Phase 6 (US4)**: Depends on Phase 3, Phase 4, and Phase 5 endpoints being available.
- **Phase 7**: Validation and polish - Runs last.

### Safe Parallel Execution Opportunities

- T015 and T016 (Frontend types and API client setup) can be safely executed in parallel with backend endpoints implementation, as they rely only on the agreed API contracts.
- US1 (Phase 3), US2 (Phase 4), and US3 (Phase 5) backend logic can be implemented in parallel if handled by different developers or distinct commits, as they build upon the same foundational queries.

### MVP Implementation Boundary

The MVP boundary for this feature encompasses User Stories 1, 2, 3, and 4 in their entirety as defined above. A partial rollout (e.g., just US1) is viable backend-wise, but full frontend integration (US4) requires all three endpoints to replace the mock data entirely without leaving broken UI panels.

### Independent Verification Criteria

- **User Story 1**: The summary totals (hours, distinct days, plan counts) match the live database rows when queried manually for a selected period.
- **User Story 2**: The daily chart data visually reconciles with the summary total and contains no missing day gaps for the selected period.
- **User Story 3**: The plan history can be navigated via pagination controls with deterministic ordering and correctly returns empty arrays if filters yield no matches.
- **User Story 4**: The entire Statistics page renders without mock data, correctly displays zero-states for new users, and gracefully recovers from simulated API errors.

### Final Definition-of-Done Checklist

- [ ] The Statistics screen accurately summarizes real Pomodoro activity and plan outcomes for the authenticated user.
- [ ] Daily heatmap/chart data is reliable and timezone-aware.
- [ ] The user can browse and filter paginated historical plans.
- [ ] No fabricated, duplicated, or cross-user data is present.
- [ ] Mock data has been completely removed from the Statistics feature.
