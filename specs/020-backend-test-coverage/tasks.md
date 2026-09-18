# Implementation Tasks: Blooming Backend Test Coverage

**Feature**: [020-backend-test-coverage](./plan.md)

This task list follows the strict requirements defined in the plan, focusing on establishing isolated PostgreSQL test infrastructure and writing granular tests for critical behaviors.

---

## Phase 1 — Repository and safety baseline

- [x] T001 Inspect and record the current backend dependency state and pytest configuration in `backend/requirements.txt`
- [x] T002 Identify selected PostgreSQL strategy (testcontainers) from `specs/020-backend-test-coverage/plan.md`
- [x] T003 Confirm schema SQL execution order by listing `database/migrations/*.sql`
- [x] T004 Record normal development database identity from `backend/app/core/config.py`
- [x] T005 Define a hard safety check function in `backend/tests/conftest.py` that rejects `TEST_DATABASE_URL` matching the dev DB
- [x] T006 Confirm the working tree state using `git status --short` to ensure unrelated user changes are preserved

## Phase 2 — Test dependencies and configuration

- [x] T007 Add `pytest`, `pytest-asyncio`, `httpx`, and `testcontainers[postgres]` to `backend/requirements.txt`
- [x] T008 Configure `pytest.ini` in `backend/pytest.ini` with `asyncio_mode = auto` and test paths
- [x] T009 Add custom `unit` and `integration` markers to `backend/pytest.ini`
- [x] T010 Add environment variable documentation for the test DB to `backend/tests/README.md`

## Phase 3 — Safe PostgreSQL infrastructure

- [x] T011 [US1] Create session-scoped `test_db_engine` fixture in `backend/tests/conftest.py` that starts testcontainers Postgres
- [x] T012 [P] [US1] Create `safe_db_url` helper in `backend/tests/conftest.py` to reject unsafe databases before engine start
- [x] T013 [US1] Add schema initialization in `backend/tests/conftest.py` executing `database/migrations/*.sql` sequentially on `blooming_template`
- [x] T014 [US1] Implement per-test isolation strategy using `CREATE DATABASE ... TEMPLATE blooming_template` in `backend/tests/conftest.py`
- [x] T015 [US1] Ensure reliable teardown and session closure in `backend/tests/conftest.py`
- [x] T016 [US1] Write test demonstrating development database is not touched in `backend/tests/infrastructure/test_safety.py`

## Phase 4 — Shared fixtures and factories

- [x] T017 Create function-scoped async session fixture `db_session` in `backend/tests/conftest.py`
- [x] T018 Create FastAPI app dependency override for `get_db_session` in `backend/tests/conftest.py`
- [x] T019 Create `async_client` fixture in `backend/tests/conftest.py`
- [x] T020 [P] Create deterministic user and auth token factory in `backend/tests/fixtures/users.py`
- [x] T021 [P] Create user settings factory with timezone logic in `backend/tests/fixtures/users.py`
- [x] T022 [P] Create task and dependency factories in `backend/tests/fixtures/tasks.py`
- [x] T023 [P] Create Daily Plan and availability window factories in `backend/tests/fixtures/planning.py`
- [x] T024 [P] Create goal and milestone factories in `backend/tests/fixtures/goals.py`
- [x] T025 [P] Create reminder factory in `backend/tests/fixtures/reminders.py`
- [x] T026 [P] Create garden state, plant unlocks, and event factories in `backend/tests/fixtures/garden.py`
- [x] T027 [P] Create focus session factory in `backend/tests/fixtures/focus.py`
- [x] T028 Add cross-test fixture leakage validation test in `backend/tests/infrastructure/test_fixtures.py`

## Phase 5 — Scheduler unit tests

- [x] T029 [P] [US3] Add unit test for valid flexible scheduling in `backend/tests/unit/test_scheduler.py`
- [x] T030 [P] [US3] Add unit test for deterministic results on identical inputs in `backend/tests/unit/test_scheduler.py`
- [x] T031 [P] [US3] Add unit test detecting direct cycles in `backend/tests/unit/test_scheduler.py`
- [x] T032 [P] [US3] Add unit test detecting multi-task cycles in `backend/tests/unit/test_scheduler.py`
- [x] T033 [P] [US3] Add unit test marking missing dependencies unscheduled in `backend/tests/unit/test_scheduler.py`
- [x] T034 [P] [US3] Add unit test for cascading dependency failures in `backend/tests/unit/test_scheduler.py`
- [x] T035 [P] [US3] Add unit test rejecting invalid fixed intervals in `backend/tests/unit/test_scheduler.py`
- [x] T036 [P] [US3] Add unit test detecting fixed-task overlaps in `backend/tests/unit/test_scheduler.py`
- [x] T037 [P] [US3] Add unit test handling fixed tasks outside availability in `backend/tests/unit/test_scheduler.py`
- [x] T038 [P] [US3] Add unit test verifying prerequisite scheduling order in `backend/tests/unit/test_scheduler.py`
- [x] T039 [P] [US3] Add unit test for satisfied external dependencies in `backend/tests/unit/test_scheduler.py`
- [x] T040 [P] [US3] Add unit test for splitting splittable tasks in `backend/tests/unit/test_scheduler.py`
- [x] T041 [P] [US3] Add unit test for minimum split duration in `backend/tests/unit/test_scheduler.py`
- [x] T042 [P] [US3] Add unit test for non-splittable tasks with insufficient slots in `backend/tests/unit/test_scheduler.py`
- [x] T043 [P] [US3] Add unit test verifying deadlines in `backend/tests/unit/test_scheduler.py`
- [x] T044 [P] [US3] Add unit test handling empty/invalid windows in `backend/tests/unit/test_scheduler.py`
- [x] T045 [P] [US3] Add unit test for stable and non-duplicated reason codes in `backend/tests/unit/test_scheduler.py`
- [x] T046 [US3] Run independent scheduler test execution using `pytest backend/tests/unit/test_scheduler.py`

## Phase 6 — Daily Plan integration tests

- [ ] T047 [P] [US2] Add test ensuring one active plan per user/date in `backend/tests/services/test_planning_service.py`
- [ ] T048 [P] [US2] Add test allowing same date for different users in `backend/tests/services/test_planning_service.py`
- [ ] T049 [P] [US2] Add test allowing different dates for one user in `backend/tests/services/test_planning_service.py`
- [ ] T050 [P] [US2] Add test verifying PostgreSQL rejects duplicate active plans in `backend/tests/services/test_planning_service.py`
- [ ] T051 [P] [US2] Add test for `replace_existing=False` rejection in `backend/tests/services/test_planning_service.py`
- [ ] T052 [P] [US2] Add test for `replace_existing=True` archiving old plan in `backend/tests/services/test_planning_service.py`
- [ ] T053 [P] [US2] Add test ensuring old `plan_date` is preserved on replacement in `backend/tests/services/test_planning_service.py`
- [ ] T054 [P] [US2] Add test ensuring replacement is the only active plan in `backend/tests/services/test_planning_service.py`
- [ ] T055 [P] [US2] Add test verifying no `IntegrityError` is thrown during replacement in `backend/tests/services/test_planning_service.py`
- [ ] T056 [P] [US2] Add test verifying multiple archived/completed plans allowed in `backend/tests/services/test_planning_service.py`
- [ ] T057 [P] [US2] Add test ensuring historical blocks remain available in `backend/tests/services/test_planning_service.py`
- [ ] T058 [P] [US2] Add test ensuring cross-user access is rejected in `backend/tests/services/test_planning_service.py`
- [ ] T059 [US2] Add test proving actual partial unique index enforcement instead of mock in `backend/tests/services/test_planning_service.py`

## Phase 7 — Reminder integration tests

- [ ] T060 [P] [US4] Add test verifying local date in a normal timezone in `backend/tests/services/test_reminders_service.py`
- [ ] T061 [P] [US4] Add test for positive and negative UTC offsets around midnight in `backend/tests/services/test_reminders_service.py`
- [ ] T062 [P] [US4] Add test for missing timezone fallback in `backend/tests/services/test_reminders_service.py`
- [ ] T063 [P] [US4] Add test for invalid timezone fallback in `backend/tests/services/test_reminders_service.py`
- [ ] T064 [P] [US4] Add test ensuring draft creation uses existing CRUD path in `backend/tests/services/test_reminders_service.py`
- [ ] T065 [P] [US4] Add test for expected task and 30-minute block creation in `backend/tests/services/test_reminders_service.py`
- [ ] T066 [P] [US4] Add test for existing draft behavior in `backend/tests/services/test_reminders_service.py`
- [ ] T067 [P] [US4] Add test for existing confirmed plan behavior in `backend/tests/services/test_reminders_service.py`
- [ ] T068 [P] [US4] Add test for existing active plan behavior in `backend/tests/services/test_reminders_service.py`
- [ ] T069 [P] [US4] Add test verifying no duplicate plan/task/block is created in `backend/tests/services/test_reminders_service.py`
- [ ] T070 [P] [US4] Add test ensuring reminder marks as COMPLETED in `backend/tests/services/test_reminders_service.py`
- [ ] T071 [P] [US4] Add test ensuring no generic 500 error is returned in `backend/tests/services/test_reminders_service.py`
- [ ] T072 [P] [US4] Add test rejecting cross-user access in `backend/tests/services/test_reminders_service.py`
- [ ] T073 [P] [US4] Add test verifying transaction atomicity during `CREATE_PLAN` in `backend/tests/services/test_reminders_service.py`

## Phase 8 — Garden integration tests

- [ ] T074 [P] [US5] Add test for Water award execution in `backend/tests/services/test_garden_service.py`
- [ ] T075 [P] [US5] Add test for Leaves award execution in `backend/tests/services/test_garden_service.py`
- [ ] T076 [P] [US5] Add test ensuring same idempotency key applied twice avoids duplicate award in `backend/tests/services/test_garden_service.py`
- [ ] T077 [P] [US5] Add test allowing multiple awards for different idempotency keys in `backend/tests/services/test_garden_service.py`
- [ ] T078 [P] [US5] Add test verifying reward event and balance atomicity in `backend/tests/services/test_garden_service.py`
- [ ] T079 [P] [US5] Add test verifying invalid reward behavior (no corruption) in `backend/tests/services/test_garden_service.py`
- [ ] T080 [P] [US5] Add test ensuring balances never become negative in `backend/tests/services/test_garden_service.py`
- [ ] T081 [P] [US5] Add test verifying watering timestamp update in `backend/tests/services/test_garden_service.py`
- [ ] T082 [P] [US5] Add test for vitality restoration logic in `backend/tests/services/test_garden_service.py`
- [ ] T083 [P] [US5] Add test ensuring plant growth and unlocks are preserved correctly in `backend/tests/services/test_garden_service.py`

## Phase 9 — Focus service tests

- [ ] T084 [P] [US6] Add test starting a focus session in `backend/tests/services/test_focus_service.py`
- [ ] T085 [P] [US6] Add test rejecting a second active-session conflict in `backend/tests/services/test_focus_service.py`
- [ ] T086 [P] [US6] Add test pausing a focus session in `backend/tests/services/test_focus_service.py`
- [ ] T087 [P] [US6] Add test resuming a paused focus session in `backend/tests/services/test_focus_service.py`
- [ ] T088 [P] [US6] Add test finishing a session with supported outcomes (`DONE`, etc.) in `backend/tests/services/test_focus_service.py`
- [ ] T089 [P] [US6] Add test verifying actual duration calculation in `backend/tests/services/test_focus_service.py`
- [ ] T090 [P] [US6] Add test verifying paused duration calculation in `backend/tests/services/test_focus_service.py`
- [ ] T091 [P] [US6] Add test ensuring Water is awarded exactly once on finish in `backend/tests/services/test_focus_service.py`
- [ ] T092 [P] [US6] Add test ensuring repeated finish requests do not duplicate reward in `backend/tests/services/test_focus_service.py`
- [ ] T093 [P] [US6] Add test verifying optional replan behavior is only invoked when requested in `backend/tests/services/test_focus_service.py`
- [ ] T094 [P] [US6] Add test verifying transaction rollback behavior in `backend/tests/services/test_focus_service.py`
- [ ] T095 [P] [US6] Add test rejecting cross-user access to focus sessions in `backend/tests/services/test_focus_service.py`
- [ ] T096 [P] [US6] Add test for missing-session semantic errors instead of 500s in `backend/tests/services/test_focus_service.py`

## Phase 10 — API route tests

- [ ] T097 [P] [US7] Add API test for missing authentication rejection in `backend/tests/api/test_focus_routes.py` and `backend/tests/api/test_reminder_routes.py`
- [ ] T098 [P] [US7] Add API happy path execution in `backend/tests/api/test_focus_routes.py` and `backend/tests/api/test_reminder_routes.py`
- [ ] T099 [P] [US7] Add API test ensuring cross-user ownership rejection in `backend/tests/api/test_focus_routes.py` and `backend/tests/api/test_reminder_routes.py`
- [ ] T100 [P] [US7] Add API test verifying not found responses in `backend/tests/api/test_focus_routes.py` and `backend/tests/api/test_reminder_routes.py`
- [ ] T101 [P] [US7] Add API test verifying conflict responses in `backend/tests/api/test_focus_routes.py` and `backend/tests/api/test_reminder_routes.py`
- [ ] T102 [P] [US7] Add API test verifying validation formatting in `backend/tests/api/test_focus_routes.py` and `backend/tests/api/test_reminder_routes.py`
- [ ] T103 [P] [US7] Add API test verifying no internal-detail leakage in `backend/tests/api/test_focus_routes.py` and `backend/tests/api/test_reminder_routes.py`
- [ ] T104 [P] [US7] Add test ensuring database override works correctly in `backend/tests/api/test_focus_routes.py` and `backend/tests/api/test_reminder_routes.py`

## Phase 11 — Documentation and commands

- [x] T105 Add unit-test, integration-test, and full-suite commands to `backend/tests/README.md`
- [x] T106 Document required environment variables and container prerequisites in `backend/tests/README.md`
- [x] T107 Add CI usage steps and safe test-database cleanup documentation in `backend/tests/README.md`
- [x] T108 Add troubleshooting section for unavailable Docker/PostgreSQL in `backend/tests/README.md`
- [x] T109 Add clear warning about normal development database isolation in `backend/tests/README.md`

## Phase 12 — Final verification

- [x] T110 Run scheduler unit tests independently using `pytest backend/tests/unit/test_scheduler.py`
- [ ] T111 Run planning tests independently using `pytest backend/tests/services/test_planning_service.py`
- [ ] T112 Run reminder tests independently using `pytest backend/tests/services/test_reminders_service.py`
- [ ] T113 Run garden tests independently using `pytest backend/tests/services/test_garden_service.py`
- [ ] T114 Run focus service tests independently using `pytest backend/tests/services/test_focus_service.py`
- [ ] T115 Run API tests independently using `pytest backend/tests/api/`
- [ ] T116 Run full backend suite using `pytest backend/tests/`
- [ ] T117 Run full backend suite a second time to ensure idempotency
- [ ] T118 Run `ruff check backend/tests/` and formatting checks
- [ ] T119 Run existing import/type checks in backend
- [x] T120 Run `git diff --check` to verify no whitespace errors
- [x] T121 Run `git status --short` to verify working tree cleanly reflects only intended files
- [x] T122 Verify no frontend/Tauri files changed, no Alembic revision was created, and no development database was modified
- [ ] T123 Verify no test was silently skipped and no assertion weakened

## Dependencies & Execution Order

- **Phase Dependency Order**: 
  Safety baseline (Phase 1) → Configuration (Phase 2) → Infrastructure (Phase 3) → Fixtures (Phase 4) → Service/API Tests (Phases 6-10) → Final Verification (Phase 12)
- **Parallelizable Tasks**:
  - Scheduler Unit Tests (Phase 5) can run in parallel with PostgreSQL infrastructure setup (Phase 3 & 4) because they do not require a database.
  - Within each test phase (Phases 5-10), tests marked with `[P]` can be implemented in parallel once the fixtures (Phase 4) are completed.
- **Minimum Viable Milestone**:
  - Completing Phases 1-4 and Phase 6 (Daily Plan integration tests) demonstrates that the core database isolation and schema initialization works.
- **Recommended Sequence**:
  - Complete the Safety baseline (Phase 1, 2, 3).
  - Implement Fixtures (Phase 4).
  - Parallelize Phase 5 and Phase 6.
  - Complete the rest of the testing phases (7-10) sequentially or in parallel.
  - Final Verification (Phase 11 & 12).

