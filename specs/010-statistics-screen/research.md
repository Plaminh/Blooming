# Research: Statistics Screen

**Feature**: Statistics Screen | **Date**: 2026-09-15

## Research Tasks

### 1. Calendar Grid Computation

**Decision**: Use `new Date(year, month, 1).getDay()` to determine the first weekday of the month, adjusted for Monday-start week (JS `getDay()` returns 0=Sunday, so Monday-start offset = `(getDay() + 6) % 7`). Use `new Date(year, month + 1, 0).getDate()` for days-in-month.

**Rationale**: Pure JavaScript date arithmetic is sufficient. No date library needed for simple month grid rendering. This approach correctly handles all months and leap years.

**Alternatives considered**: 
- `date-fns` or `dayjs` library — rejected as overkill for displaying a single month grid.
- Hardcoded month data — rejected as it violates FR-013 (calendar dates must be generated from typed data).

### 2. CSS-Only Bar Chart Implementation

**Decision**: Use CSS flexbox with `align-items: flex-end` for the chart container. Each bar column uses a percentage height relative to the tallest bar. The tallest bar occupies ~80% of the container height; others scale proportionally. Value labels positioned with `position: relative` above each bar. Zero-value days show a 2px baseline marker.

**Rationale**: FR-015 explicitly prohibits third-party charting libraries. A CSS flexbox approach is the simplest implementation that matches the reference. The chart has exactly 7 fixed data points, making CSS a natural fit.

**Alternatives considered**:
- SVG `<rect>` elements — viable but more complex for a simple 7-bar chart.
- Canvas API — rejected as overkill and harder to make accessible.
- Chart.js or similar library — explicitly prohibited by FR-015.

### 3. Plan History Pagination Strategy

**Decision**: Client-side pagination using array slicing. Given a filtered array, compute `totalPages = Math.ceil(filtered.length / itemsPerPage)`. Display rows `[(page-1)*itemsPerPage, page*itemsPerPage)`. Store `currentPage` and `activeFilter` in component-local `$state`. Reset page to 1 on filter change.

**Rationale**: All data is local mock data. Client-side pagination is the simplest approach. The spec requires "Showing 4 of 11 plans" and "1 / 3" page indicator, confirming `itemsPerPage = 4` and `totalItems = 11`.

**Alternatives considered**:
- Server-side pagination — not applicable (no backend).
- Infinite scroll — does not match reference (explicit pagination controls shown).

### 4. Date Range Selector Dropdown

**Decision**: Simple HTML-styled dropdown using a `<button>` toggle and absolutely-positioned `<ul>` menu. Click outside closes the dropdown. Predefined mock date range options.

**Rationale**: No shared Select/Dropdown component exists in the project. The spec assumes "a simple local implementation" (Assumptions section). The dropdown only needs to present a few predefined options.

**Alternatives considered**:
- Native `<select>` element — styling limitations would not match the reference's custom styled selector.
- Shared dropdown component — would violate FR-027 (must not create duplicate shared components) and the principle of not creating speculative abstractions.

### 5. Sidebar Item Positioning

**Decision**: Add the STATISTICS `SidebarNavigationItem` in `AppSidebar.svelte` between the MR. BLOOM and SETTINGS items. Update `DesktopAppShell.svelte` to accept `'STATISTICS'` in its `activeRoute` union. Update `SidebarNavigationItem.svelte` to accept `'statistics'` in its `icon` union.

**Rationale**: The spec (FR-002) and design reference both show STATISTICS positioned between MR. BLOOM and SETTINGS. The existing pattern of hardcoded items in `AppSidebar.svelte` should be maintained for consistency.

**Alternatives considered**:
- Data-driven sidebar configuration — rejected as over-engineering for a simple addition.

### 6. Statistics Icon Design

**Decision**: Three ascending vertical bars (simple bar-chart icon) using `currentColor` fill, rendered in the same 24×24 viewBox as existing icons. Bars at approximately x=5 (shortest), x=10 (medium), x=15 (tallest), all resting on a common baseline.

**Rationale**: The design reference shows a bar-chart icon for the Statistics sidebar item. The spec (FR-004) requires "simple ascending vertical bars" using `currentColor`. This matches the existing `AppIcon` pattern.

**Alternatives considered**:
- Using an existing icon (e.g., `document`) — would not communicate "statistics".
- Importing an external icon asset — unnecessary when a simple SVG path suffices.

### 7. State Management Approach

**Decision**: No Svelte store. Use component-local `$state()` and `$derived()` runes. The page component holds `selectedRange` state. Organisms hold their own local state (`currentMonth` in calendar, `activeFilter` and `currentPage` in plan history). Mock data is imported as constants.

**Rationale**: The Statistics page is read-only with simple local interactions (month navigation, filtering, pagination). There is no cross-component state that requires a shared store. Constitution Principle 5 forbids speculative stores.

**Alternatives considered**:
- Writable Svelte store in `stores/statisticsStore.ts` — rejected; no shared state justifies a store. Component-local state is simpler and more maintainable.
- Context API — unnecessary for parent-to-child data flow that props handle.

### 8. Accessibility Implementation

**Decision**: Semantic HTML structure: `<h1>` for "STATISTICS", `<h2>` for panel titles. `<table>` with `<thead>` and `<th>` for plan history. All buttons have `aria-label`. Bar chart data points have `aria-label` (e.g., "Monday: 2 hours"). Calendar navigation buttons have `aria-label`. Status indicators use icon shape + text label (not color alone). All interactive elements focusable and activatable via keyboard.

**Rationale**: FR-029 through FR-038 define comprehensive accessibility requirements. The existing codebase uses `aria-current="page"` on active sidebar items (see `SidebarNavigationItem.svelte`) and `aria-label` on icon buttons.

**Alternatives considered**: None — accessibility requirements are non-negotiable.

## Resolved Clarifications

All technical unknowns from the Technical Context have been resolved through codebase analysis:

| Unknown | Resolution |
|---------|-----------|
| Calendar grid computation | JS Date arithmetic, Monday-start adjustment |
| Bar chart approach | CSS flexbox with percentage heights |
| Pagination strategy | Client-side array slicing |
| Date range dropdown | Custom button+menu (no shared component exists) |
| Sidebar integration | Direct modification of 4 shared components |
| Icon for statistics | New SVG path in AppIcon (3 ascending bars) |
| State management | Component-local `$state`/`$derived`, no store |
| Accessibility | Semantic HTML + ARIA attributes following existing patterns |
