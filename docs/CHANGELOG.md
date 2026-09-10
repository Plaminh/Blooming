# Changelog

All notable user-visible and architectural changes to Blooming will be recorded here.

## [Unreleased]

### Added

- Initial product, requirements, architecture, and test documentation.
- Implementation-ready specification for the deterministic Quick Planning Engine.
- Frozen product concept `02-product/Blooming-Concept-Updated.md` as the documentation source of truth.

### Changed

- Scheduler delivery was split into two evidence-producing increments; no fixed two-day completion promise is made.
- Project documentation was aligned to the frozen concept: Windows/Linux desktop (Tauri 2, Svelte, FastAPI, PostgreSQL), WidgetState independent from WidgetContext, PlantType over one GardenState, presentation-only weather, and FastAPI-plus-Tauri reminders without OS toasts.

### Fixed

- Nothing yet.

### Security

- Established the rule that personal planning content and secrets must not appear in logs or source control.
