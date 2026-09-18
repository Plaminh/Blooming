# Implementation Plan: Widget Environment Rendering

**Branch**: `feature/widget-weather` | **Date**: 2026-09-18 | **Spec**: [./spec.md](./spec.md)

**Input**: User inline requirements for asset structure refactoring and widget environment implementation

## Summary

The repository originally contained `daytime/`, `season/`, and `weather/` directories at the project root which hold environmental assets for the widget. This plan details the completed migration of those assets to the standard `frontend/src/lib/assets/widget/environment/` hierarchy, and the implementation of the `WidgetSceneBackground.svelte` component. The environment rendering system integrates a centralized time source to switch daytime and seasonal layers independently, renders static weather ambiences (safely falling back to CLEAR when weather data is unavailable), and supports a procedural CSS rain layer that traverses the widget dynamically based on weather intensity.

## Technical Context

**Language/Version**: TypeScript / SvelteKit / Vite (Frontend)

**Primary Dependencies**: SvelteKit static asset serving

**Storage**: File system (Static assets)

**Testing**: `npm run test` (Vitest), `npm run check` (TypeScript), Vite dev server rendering

**Target Platform**: Tauri Desktop Widget (Windows / Linux)

**Project Type**: SvelteKit Frontend Feature

**Performance Goals**: Procedural rain animation using purely CSS container queries (no WebGL or requestAnimationFrame).

**Constraints**: Asset layer composition logic must not be merged. Keep time/weather/season distinct. No full-screen rain spritesheets. Time source follows the user timezone saved in settings. Current weather is fetched by the backend from Open-Meteo using the saved location and a 15-minute cache.

**Scale/Scope**: Widget Scene Background component, environment logic model, clock store, procedural rain component, asset migration.

## Constitution Check

*GATE: Passed*

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite boundaries?
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully?
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

## Project Structure

### Documentation (this feature)

```text
specs/021-widget-environment/
├── plan.md              # This file
├── data-model.md        # Migration mapping and Environment types
├── quickstart.md        # Validation steps
└── contracts/           # N/A
```

### Source Code

```text
frontend/src/lib/
├── assets/widget/environment/
│   ├── daytime/
│   ├── season/
│   └── weather/
├── features/companion-widget/
│   ├── components/atoms/RainLayer.svelte
│   ├── components/molecules/WidgetSceneBackground.svelte
│   └── model/environment.ts
└── shared/stores/
    └── clockStore.ts
```

## Migration & Implementation Plan

### 1. Asset Migration
- Assets have been fully migrated to `frontend/src/lib/assets/widget/environment/`.
- `daytime`, `season`, and `weather` at the repository root were successfully deleted.
- Unused fields like `skySrc` and `bushesSrc` were scrubbed from `atlas.ts`.

### 2. Centralized Clock Store
- Implemented `clockStore.ts` utilizing `readable` to emit the current local time exactly once per minute.
- Prevents components like `WidgetSceneBackground` from manually declaring overlapping `setInterval` timers.
- Formats the current instant in the timezone saved in user settings.

### 3. Environment Modeling
- Strongly typed `Daytime`, `Season`, and `Weather` in `environment.ts`.
- Developed utility functions `getDaytimeFromHour` and `getSeasonFromMonth`.
- Replaced string paths with explicit Vite static imports (`import dawn from ...`) guaranteeing frontend availability.

### 4. Component Layering
- `WidgetSceneBackground.svelte` implements the independent stacking order:
  1. Time of Day Base Layer
  2. Seasonal Vegetation Layer
  3. Static Weather Ambience Overlay
  4. Procedural Rain Overlay
- Implements a fallback prop `weather="CLEAR"` which ensures safety and graceful loading states.

### 5. Procedural Rain Animation
- `RainLayer.svelte` implements CSS-based rain drops.
- Utilizes `container-type: size` for responsiveness across widget states.
- Utilizes negative animation delays to begin mid-animation seamlessly.
- Configurable intensity maps directly to weather condition (RAIN = 30 drops, THUNDERSTORM = 60 drops).

### 6. Validation/Build Steps & Risks
- **TS/Svelte checks**: Run `npm run check` in `frontend/`.
- **Build**: Run `npm run build` in `frontend/`.
- **Testing**: Run `npm run test` for specific DOM-level testing of configuration and weather bounds.
