# Feature Specification: Widget Environment Rendering

**Feature Branch**: `feature/widget-weather`

**Created**: 2026-09-18

**Status**: Completed

**Input**: User description: "Implement the Blooming Widget Environment Rendering System using the environmental assets..."

## User Scenarios & Testing

### User Story 1 - Time-of-Day Background Rendering (Priority: P1)

Users see the widget background visually correspond to the actual time of day in their configured timezone.

**Why this priority**: Time-of-day forms the foundational base layer for the entire widget scene.

**Independent Test**: Can be tested by overriding the system time and observing the widget's sky background.

**Acceptance Scenarios**:

1. **Given** it is 9:00 AM local time, **When** the widget renders, **Then** it displays the `morning.png` sky asset.
2. **Given** the time crosses a deterministic threshold (e.g., 20:00), **When** the widget updates, **Then** it seamlessly transitions to the `night.png` asset.

---

### User Story 2 - Seasonal Vegetation Rendering (Priority: P1)

Users see seasonal vegetation (bushes/trees) that correspond to the current month.

**Why this priority**: The season adds the required foreground layer to complete the static environment.

**Independent Test**: Can be tested by overriding the system date to different months.

**Acceptance Scenarios**:

1. **Given** it is May (Spring), **When** the widget renders, **Then** it displays the `spring.png` vegetation asset.

---

### User Story 3 - Static Weather Ambience (Priority: P2)

Users see static overlays applied to the environment when weather conditions warrant them (Cloudy, Overcast, Storms).

**Why this priority**: Enhances the visual immersion of the widget environment.

**Independent Test**: Can be tested by forcing the `weather` prop in the component tree.

**Acceptance Scenarios**:

1. **Given** weather is CLOUDY, **When** the widget renders, **Then** the `cloudy.png` overlay is rendered above the season layer.
2. **Given** weather is CLEAR or unavailable, **When** the widget renders, **Then** no weather overlay is rendered.

---

### User Story 4 - Procedural Rain Animation (Priority: P3)

Users see an animated procedural pixel rain effect when the weather condition includes rain or thunderstorms.

**Why this priority**: Provides the primary animated environmental interaction, bringing the scene to life.

**Independent Test**: Can be fully tested by verifying the CSS keyframes and DOM streak counts when RAIN or THUNDERSTORM is active.

**Acceptance Scenarios**:

1. **Given** weather is RAIN, **When** the widget renders, **Then** 30 procedurally placed rain streaks fall across the full scene.
2. **Given** weather is THUNDERSTORM, **When** the widget renders, **Then** a denser rain effect (60 streaks) is rendered along with the storm overlay.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST structure runtime assets cleanly in `frontend/src/lib/assets/widget/environment/`.
- **FR-002**: The widget MUST dynamically render independent layers for Daytime, Season, Weather, Rain, Plant, Character, and UI.
- **FR-003**: The environment MUST use the user's configured timezone for daytime evaluation.
- **FR-004**: The system MUST provide deterministic frontend helpers for daytime and season logic.
- **FR-005**: Rain MUST be rendered procedurally using CSS animations without heavy WebGL or `requestAnimationFrame` loops.
- **FR-006**: When weather data is missing or loading, the system MUST fallback safely to `CLEAR` without breaking the base environment.
- **FR-007**: The environment MUST remain purely visual and not interfere with backend productivity, task scheduling, or rewards.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Frontend typechecks and builds pass with 0 errors.
- **SC-002**: All environmental layers render independently without requiring pre-composed combinatorial images.
- **SC-003**: Rain animation is strictly CSS-based and covers the entire scene dynamically without hardcoded pixel distances (e.g., using `container-type`).
- **SC-004**: The widget environment functions perfectly on Windows and Linux (MVP platforms) without performance degradation.

## Assumptions

- We assume no existing centralized clock/Tauri time system exists in the frontend, so a lightweight `clockStore.ts` is implemented to prevent scattered intervals.
- The environment targets Windows and Linux platforms for the MVP.
- The Settings page saves the rain animation preference in user settings, which the widget reads.
- Weather is fetched through the authenticated backend using the saved weather location. Disabled, missing, or unavailable weather falls back to `CLEAR`.
