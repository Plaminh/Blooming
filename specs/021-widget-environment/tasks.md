# Implementation Tasks: Widget Environment Rendering

## Phase 1: Inspection, Preparation & Asset Migration
- [x] 1. **Inspect current assets**: Enumerate files inside `/daytime`, `/season`, and `/weather`. Classify each file (runtime, design/reference, or unused). Record an old-path -> target-path mapping.
- [x] 2. **Find usages**: Search the entire repository for references to every current environmental asset. [P]
- [x] 3. **Create target structure**: Create the `frontend/src/lib/assets/widget/environment/daytime/`, `season/`, and `weather/` directories.
- [x] 4. **Move daytime assets**: Move runtime time-of-day assets into `environment/daytime/`.
- [x] 5. **Move season assets**: Move runtime seasonal vegetation/environment layers into `environment/season/`.
- [x] 6. **Move weather assets**: Move static weather overlays/effects into `environment/weather/`. Rename assets if needed (e.g. `thunder-storm.png` -> `storm-overlay.png`).

## Phase 2: Environment Rendering & Logic
- [x] 7. **Environment Types**: Create strict frontend types for Daytime, Season, and Weather. Map the migrated assets to these types in a centralized file using Vite static imports.
- [x] 8. **Time Context**: Create a centralized frontend time context (`clockStore`) to avoid duplicated `setInterval` calls in components.
- [x] 9. **RainLayer Component**: Implement procedural CSS rain using deterministic configuration (streaks vary in duration, length, delay, and position).
- [x] 10. **Rain Density**: Implement density differentiation between `RAIN` (30 streaks) and `THUNDERSTORM` (60 streaks).
- [x] 11. **Rain Travel**: Fix rain fall distance to be container-relative using CSS Container Queries (`cqh`/`cqw`) rather than fixed pixels, and ensure crisp rendering without blurry rotations.
- [x] 12. **Widget Composition**: Wire the Time, Season, Weather, and Rain layers into `WidgetSceneBackground.svelte` with appropriate stacking order and fallback behaviors (`CLEAR` weather default).

## Phase 3: Runtime Weather Integration
- [x] 13. **Weather Provider**: Geocode the saved location with Open-Meteo, fetch current weather, and normalize WMO codes to widget conditions.
- [x] 14. **Weather Cache**: Cache conditions for 15 minutes and coordinates for one day; serialize requests per location without blocking other locations.
- [x] 15. **Authenticated API**: Expose `/me/weather` using the signed-in user's weather settings and a safe `CLEAR` fallback.
- [x] 16. **Settings Persistence**: Add the weather animation preference to the user settings schema and database migration.
- [x] 17. **Onboarding and Settings**: Save weather location during onboarding and expose weather location, enablement, and animation controls in Settings.
- [x] 18. **Configured Timezone**: Format the shared clock's current instant in the user's saved timezone for daytime and season selection.
- [x] 19. **Widget Runtime**: Load weather and settings in the widget, refresh weather every 15 minutes, apply saved settings immediately through a desktop event, and pass the condition and animation setting to the scene.
- [x] 20. **Backend Tests**: Cover WMO normalization, provider caching and failure fallback, and authenticated route behavior.

## Phase 4: Validation & Cleanup
- [x] 21. **Dead Asset Cleanup**: Remove old unused fields like `skySrc` and `bushesSrc` from `atlas.ts`. Remove old root directories `/daytime`, `/season`, and `/weather`.
- [x] 22. **Test Strengthening**: Assert environmental asset mapping, weather fallback, rain density, timezone conversion, and settings wiring.
- [x] 23. **Repository Cleanup**: Search for stale references to old root paths and ensure unrelated assets were not moved accidentally. [P]
- [x] 24. **Final Verification**: Run backend weather tests, frontend tests, Svelte checks, and frontend build.
