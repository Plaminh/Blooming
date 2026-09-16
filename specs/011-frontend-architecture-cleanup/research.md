# Research: Frontend Architecture Cleanup

## 1. SvelteKit Route Groups and Persistent Layouts

**Decision**: Move main application routes into a `(app)` route group.
**Rationale**: By moving `today`, `goals`, `mr-bloom`, `settings`, `statistics`, and `garden-selection` into `src/routes/(app)/`, we can create a `src/routes/(app)/+layout.svelte`. This layout will instantiate `DesktopAppShell` and `AppSidebar` exactly once. The inner `{@render children()}` will render the specific page content. This ensures the sidebar and shell don't remount during navigation, satisfying FR-005 and SC-002. Standalone routes (`auth`, `onboarding-preview`, `widget`, `widget-preview`) will remain at the root level outside `(app)`, ensuring they don't receive the main app shell (FR-006).

**Alternatives considered**:
- Putting the app shell in the root `src/routes/+layout.svelte` and conditionally rendering it based on the `$page.url.pathname`. This is an anti-pattern in SvelteKit because it leads to "unreadable conditional components" and doesn't cleanly separate concerns. Route groups are the idiomatic approach.

## 2. Shared Garden Panel State

**Decision**: Lift the shared Garden panel UI into `src/routes/(app)/+layout.svelte` using a structural CSS Grid overlay technique. `DesktopAppShell`'s main content area was updated to a CSS Grid (`grid-template-areas: "layer"`), allowing both the page content (`.page-layer`) and a persistent overlay layer (`.garden-layer`) to stack perfectly. The `.garden-layer` uses CSS grid columns and rows that structurally mirror the `today` and `goals` pages to seamlessly drop the Garden panel into the exact visual slot on the right rail.
**Rationale**: The spec requires the Garden panel not to remount between Today and Goals (FR-007). This CSS grid structural overlap avoids complex Svelte stores, `snippet` passing through layout levels, and brittle absolute positioning, keeping the Svelte tree clean while preserving visual integration.
**Alternatives considered**: DOM relocation (teleport), which is fragile and discouraged by the spec. Nested route groups (`(app)/(with-garden)`), which complicate navigation. Snippet passing via stores, which adds unnecessary reactivity overhead.

## 3. UI Consistency & Atomic Design

**Decision**: Audit `src/lib/shared/components/atoms/AppIcon.svelte` to implement the required vector glyphs. Create unified `TextInput.svelte` and `StatusBadge.svelte` in `src/lib/shared/components/atoms/` and deprecate local copies in `mr-bloom`, `settings`, and `statistics`. Audit `theme.css` for semantic token usage.
**Rationale**: Follows atomic design principles and reduces code duplication (FR-001, FR-003, FR-011).

## 4. Testing Strategy

**Decision**: Use Vitest + `@testing-library/svelte` for component and behavior-focused tests (FR-014). Provide manual verification instructions for layout remounts, as DOM persistence across route changes is sometimes tricky to assert reliably in JSDOM-based component tests without full E2E frameworks (like Playwright, which is out of scope).
**Rationale**: Adheres to the prompt's instruction to not introduce a new E2E framework solely for this cleanup.
