# Implementation Tasks: Weather Environment Reliability

## Phase 1: Setup and repository verification

- [x] T001 Verify existing backend `FastAPI` structure and test commands in `backend/`
- [x] T002 Verify existing frontend `SvelteKit` structure, tests, and build commands in `frontend/`
- [x] T003 Confirm canonical SQL installer and disposable database workflow
- [x] T004 Record verified path and command differences in `plan.md` (if any exist)

## Phase 2: Foundational contracts and shared types

- [x] T005 Create backend enums for `WeatherCondition`, `WeatherStatus`, and `SceneSeason` in `backend/app/models/enums.py`
- [x] T006 Create typed backend Pydantic models for `WeatherResponse` and `PlaceCandidate` in `backend/app/schemas/weather.py`
- [x] T007 Create frontend typescript interfaces matching backend enums and responses in `frontend/src/lib/types/weather.ts`
- [x] T008 Add coordinate validation rules (rounding to 2 decimals) and schema validation tests in `backend/tests/unit/test_weather_schemas.py`

## Phase 3: Canonical SQL schema and settings persistence

- [x] T009 Update `database/migrations/01_users_and_auth.sql` with `weather_location_name`, `weather_lat`, `weather_lon`, and `scene_season` to the user settings table
- [x] T010 Update `UserSettings` SQLAlchemy model in `backend/app/db/models/users.py` with new fields and default `AUTO` season
- [x] T011 Update settings Pydantic serialization/validation schemas in `backend/app/schemas/user_settings.py` to handle the new fields
- [x] T012 Add unit tests for database coordinate limits and rounding precision in `backend/tests/unit/test_user_settings.py`
- [x] T013 Add unit tests verifying `scene_season` enum bounds in `backend/tests/unit/test_user_settings.py`

## Phase 4: Backend weather-provider foundation

- [x] T014 Implement place search provider function calling Open-Meteo geocoding in `backend/app/services/weather_service.py`
- [x] T015 Implement weather forecast provider function in `backend/app/services/weather_service.py`
- [x] T016 Add coordinate rounding to exactly two decimal places before forwarding to provider in `backend/app/services/weather_service.py`
- [x] T017 Map WMO codes to the five visual `WeatherCondition` values, defaulting unknowns to UNAVAILABLE
- [x] T018 Implement robust error handling to convert provider timeouts and 429s into internal domain errors in `backend/app/services/weather_service.py`
- [x] T019 Add focused service tests for WMO mapping and rounding in `backend/tests/unit/test_weather_service.py`

## Phase 5: Bounded caching and stale fallback

- [x] T020 Implement a bounded 24-hour place-search `TTLCache` in `backend/app/services/weather_service.py`
- [x] T021 Implement a bounded 15-minute forecast `TTLCache` indexed by 2-decimal coordinates in `backend/app/services/weather_service.py`
- [x] T022 Implement stale fallback logic: catch fetch errors, check for successful fetches within 2 hours, and return `STALE` status
- [x] T023 Add cache eviction and 15-minute TTL expiration tests in `backend/tests/unit/test_weather_cache.py`
- [x] T024 Add tests verifying 2-hour stale cutoff and UNAVAILABLE returns on provider failure in `backend/tests/unit/test_weather_cache.py`

## Phase 6: Backend place-search and weather APIs

- [x] T025 [US1] Create authenticated `GET /api/weather/search` route returning max 5 candidates in `backend/app/api/routes/weather.py`
- [x] T026 [US1] Create authenticated `GET /api/weather/current` route implementing DISABLED, UNAVAILABLE, OK, and STALE logic in `backend/app/api/routes/weather.py`
- [x] T027 [US1] Ensure weather endpoint avoids runtime geocoding of legacy text locations in `backend/app/api/routes/weather.py`
- [x] T028 [US1] Add route tests for search locale, empty queries, and typed weather responses in `backend/tests/api/test_weather_routes.py`

## Phase 7: Frontend place selection and privacy controls

- [x] T029 [US1] Implement debounced text input and candidate dropdown in `frontend/src/lib/features/settings/components/molecules/WeatherLocationPicker.svelte`
- [x] T030 [US1] Implement exact location selection (preventing free-text overrides) in `frontend/src/lib/features/settings/components/molecules/WeatherLocationPicker.svelte`
- [x] T031 [US2] Add "Use device location" button that requests geolocation only upon explicit click
- [x] T032 [US2] Implement rounding of geolocation coordinates to two decimal places immediately within the success callback in `frontend/src/lib/shared/deviceLocation.ts`
- [x] T033 [US2] Add frontend test proving precise coordinates do not leave the geolocation handler in `frontend/src/lib/shared/deviceLocation.test.ts`

## Phase 8: Shared environment store/service

- [x] T034 [US4] Create `EnvironmentStore` managing condition, status, timezone, and season in `frontend/src/lib/shared/stores/environmentStore.ts`
- [x] T035 [US4] Implement 15-minute polling loop and 5-minute debounced focus refresh in `frontend/src/lib/shared/stores/environmentStore.ts`
- [x] T036 [US4] Implement deduplication of concurrent/out-of-order weather API responses in `frontend/src/lib/shared/stores/environmentStore.ts`
- [x] T037 [US4] Add store unit tests using fake timers in `frontend/src/lib/shared/stores/environmentStore.test.ts`

## Phase 9: Widget and GardenPanel integration

- [x] T038 [US4] Update widget background to consume `EnvironmentStore` instead of local polling in `frontend/src/lib/features/companion-widget/components/molecules/WidgetSceneBackground.svelte`
- [x] T039 [US4] Update `GardenPanel` to consume `EnvironmentStore` and remove implicit CLEAR fallback in `frontend/src/lib/shared/components/organisms/GardenPanel.svelte`
- [x] T040 [US4] Add component integration test proving widget and garden share the same state in `frontend/src/lib/shared/components/organisms/GardenPanel.test.ts`

## Phase 10: Timezone consistency

- [x] T041 [US4] Implement single `Intl` device-timezone helper in `frontend/src/lib/shared/deviceLocation.ts`
- [x] T042 [US4] Sync detected timezone with backend settings on authenticated startup without repeated writes in `frontend/src/lib/shared/stores/environmentStore.ts`
- [x] T043 [US4] Replace existing scattered `Intl` calls in statistics and app routes with the single timezone helper

## Phase 11: Season resolution

- [x] T044 [US5] Implement deterministic season resolution function mapping month and latitude to hemisphere seasons in `frontend/src/lib/shared/utils/season.ts`
- [x] T045 [US5] Update settings UI to expose `scene_season` manual override while leaving onboarding defaulted to `AUTO`
- [x] T046 [US5] Add unit tests for zero latitude, missing latitude, and explicit overrides in `frontend/src/lib/shared/utils/season.test.ts`

## Phase 12: Rain performance and accessibility

- [x] T047 [US6] Update `RainLayer` to pause animation when `prefers-reduced-motion` is active in `frontend/src/lib/features/companion-widget/components/atoms/RainLayer.svelte`
- [x] T048 [US6] Update `RainLayer` to pause rendering when `document.hidden` or widget is hidden in `frontend/src/lib/features/companion-widget/components/atoms/RainLayer.svelte`
- [x] T049 [US6] Add component test for accessibility and visibility cleanup conditions in `frontend/src/lib/features/companion-widget/components/atoms/RainLayer.test.ts`

## Phase 13: Deterministic widget preview

- [x] T050 [US3] Extend `/widget-preview` route to parse `time`, `season`, and `weather` query parameters in `frontend/src/routes/widget-preview/+page.svelte`
- [x] T051 [US3] Pass preview overrides down to `WidgetSceneBackground` without mutating real environment store
- [x] T052 [US3] Add preview parameter combination tests (e.g. NIGHT x RAIN x WINTER) in `frontend/src/routes/widget-preview/sceneQuery.test.ts`

## Phase 14: Status UI and failure behavior

- [x] T053 [US7] Update widget and garden panels to render transient `STALE` status indications unobtrusively
- [x] T054 [US7] Ensure active rain/cloud scenes do not flash to `CLEAR` during frontend refresh failure
- [x] T055 [US7] Implement visual fallback to `CLEAR` only when `status` is strictly `UNAVAILABLE` or `DISABLED`

## Phase 15: Final integration and regression validation

- [x] T056 Initialize disposable PostgreSQL database with `database/install.sql` and run Pytest infrastructure schema verification
- [x] T057 Run backend linter, formatter, and type checker
- [x] T058 Run full backend test suite (`pytest`)
- [x] T059 Run frontend linter, formatter, and type checker
- [x] T060 Run full frontend component and integration test suite
- [x] T061 Build production frontend bundle
- [x] T062 Search for remaining direct `Intl` timezone calls and runtime geocoding
- [ ] T063 Run Tauri build validation

## Dependencies

- Phase 2 (Contracts) MUST precede Phase 6 (APIs) and Phase 7 (Frontend Selection).
- Phase 3 (Canonical SQL schema) MUST precede Phase 4 (Provider Foundation) and Phase 6 (APIs).
- Phase 8 (Environment Store) MUST precede Phase 9 (Widget Integration).
- Phase 11 (Season Resolution) and Phase 10 (Timezone) MUST precede Phase 13 (Deterministic Preview).
- Phase 15 (Validation) MUST be executed last.

*Parallel Execution*:
Tasks within Phase 15 (Validation) can be executed in parallel where runners allow, but they must all succeed before the feature is marked complete. Phase 4 and Phase 7 can be started in parallel once Phase 2 is complete.

