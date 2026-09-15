# Feature Specification: Statistics Screen

**Feature Branch**: `010-statistics-screen`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "Implement the Blooming Statistics screen to match the design reference at `design-assets/app/references/statistic.png`. The screen displays study progress summaries, a study calendar, a daily study time chart, and a plan history table. It integrates into the shared application shell with a new sidebar navigation item."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — View Study Progress Summary (Priority: P1)

A user opens the Statistics page to see an at-a-glance summary of their study activity over a selected date range. They see three summary cards showing total study time, number of study days, and plan completion counts. This gives them immediate insight into their recent productivity without drilling into details.

**Why this priority**: The summary cards are the first content the user encounters and provide the highest-value overview. Without them the page has no anchoring data.

**Independent Test**: Can be tested by navigating to `/statistics` and verifying that all three summary cards render with correct labels, icons, and formatted values.

**Acceptance Scenarios**:

1. **Given** the user is on any page, **When** they click the Statistics navigation item in the sidebar, **Then** the Statistics page loads and displays a `STATISTICS` heading, a subtitle `Your progress, one day at a time.`, and three summary cards.
2. **Given** the Statistics page is open, **When** the user reads the summary cards, **Then** the Study Time card shows a clock icon and `24h 30m`, the Study Days card shows a calendar icon and `10 days`, and the Plans card shows a document icon and `8 complete / 3 unfinished`.
3. **Given** the Statistics page is open, **When** the user views the upper-right area, **Then** a date-range selector shows the text `Jun 1 - 14, 2026` with a calendar icon and dropdown chevron.

---

### User Story 2 — Review Study Calendar (Priority: P1)

A user checks which days they studied during a given month. They see a calendar grid for June 2026 with green cells marking studied days and neutral gray cells for days with no record. They can navigate to previous or next months.

**Why this priority**: The study calendar is a core visual feature of the Statistics page that provides day-level detail — the most granular insight on the screen.

**Independent Test**: Can be tested by verifying the calendar renders June 2026 with correct day states and that month navigation buttons change the visible month.

**Acceptance Scenarios**:

1. **Given** the Statistics page is open, **When** the user views the Study Calendar panel, **Then** the panel title reads `STUDY CALENDAR`, the month label reads `June 2026`, weekday headings are `Mon` through `Sun`, and a 7-column day grid displays days 1–30.
2. **Given** June 2026 is displayed, **When** the user examines the calendar grid, **Then** days 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, and 14 are styled as "studied" (green) and all other days are styled as "no record" (neutral gray). A legend below the grid labels both states.
3. **Given** June 2026 is displayed, **When** the user clicks the next-month button, **Then** the calendar advances to July 2026 and the grid updates. The panel does not resize.
4. **Given** the user has navigated to a month other than June 2026, **When** they click the previous-month button, **Then** the calendar returns to the prior month.

---

### User Story 3 — Review Daily Study Time Chart (Priority: P1)

A user views a bar chart showing daily study hours for the week of June 8–14. Each day has a labeled bar showing hours studied. Zero-hour days show a minimal neutral baseline indicator rather than an empty space.

**Why this priority**: The bar chart is the complementary time-series visualization beside the calendar and is required for the reference layout to be complete.

**Independent Test**: Can be tested by verifying seven bars render with correct height proportions, value labels, weekday labels, and the zero-hour treatment.

**Acceptance Scenarios**:

1. **Given** the Statistics page is open, **When** the user views the Daily Study Time panel, **Then** the panel title reads `DAILY STUDY TIME`, the subtitle reads `Jun 8 - 14`, and seven vertical bars are displayed.
2. **Given** the chart is visible, **When** the user reads the data, **Then** bar values are: Mon `2h`, Tue `3h`, Wed `0h`, Thu `2.5h`, Fri `4h`, Sat `0h`, Sun `3h`. Each value label appears above its bar and each weekday label appears below the baseline.
3. **Given** the chart displays Wednesday and Saturday with `0h`, **When** the user examines those columns, **Then** they show a small neutral baseline marker at the bottom of the chart area rather than an invisible gap.
4. **Given** a screen reader or keyboard user accesses the chart, **When** they navigate the chart area, **Then** every data point has an accessible text label (e.g., `aria-label` describing the day and value).

---

### User Story 4 — Browse and Filter Plan History (Priority: P2)

A user reviews a table of past plans, seeing the date, plan name, task completion ratio, and status (Completed or Unfinished) for each entry. They can filter by status and paginate through multiple pages of results.

**Why this priority**: Plan History adds depth but depends on the page shell and navigation being functional. It can be tested independently once the page renders.

**Independent Test**: Can be tested by verifying the table renders reference rows, filter buttons toggle visibility, and pagination controls move between pages.

**Acceptance Scenarios**:

1. **Given** the Statistics page is open, **When** the user views the Plan History panel, **Then** the panel title reads `PLAN HISTORY`, filter buttons `All`, `Completed`, and `Unfinished` are visible, and a table with columns `DATE`, `PLAN`, `TASKS`, and `STATUS` is displayed.
2. **Given** the `All` filter is active (default), **When** the user reads the table, **Then** four rows are displayed: Jun 14 / Learn machine learning / 3 / 3 / Completed, Jun 12 / Build backend API / 2 / 3 / Unfinished, Jun 11 / Study databases / 3 / 3 / Completed, Jun 9 / Refine Blooming UI / 1 / 3 / Unfinished. Each row has a navigation chevron.
3. **Given** the `All` filter is active, **When** the user clicks `Completed`, **Then** the `Completed` button shows the active (light-blue) state, the `All` button returns to its default state, and only rows with `Completed` status are visible.
4. **Given** page 1 of 3 is displayed, **When** the user clicks the next-page button, **Then** the table updates to page 2, the page indicator reads `2 / 3`, and the previous-page button becomes enabled.
5. **Given** page 1 is displayed, **When** the user examines the previous-page button, **Then** it is disabled. **Given** the last page is displayed, **When** the user examines the next-page button, **Then** it is disabled.
6. **Given** the table footer is visible, **When** the user reads it, **Then** it displays `Showing 4 of 11 plans`.

---

### User Story 5 — Navigate to Statistics via Shared Sidebar (Priority: P1)

A user on any main application page sees a `STATISTICS` entry with a bar-chart icon in the sidebar, positioned between `MR. BLOOM` and `SETTINGS`. Clicking it navigates to the Statistics page and shows the active (light-blue background) state.

**Why this priority**: Sidebar integration is foundational — without it the page is unreachable through normal navigation.

**Independent Test**: Can be tested from any existing page (Today, Goals, Mr. Bloom, Settings) by clicking the Statistics sidebar item and verifying navigation and active state.

**Acceptance Scenarios**:

1. **Given** the user is on any main application page (Today, Goals, Mr. Bloom, or Settings), **When** they view the sidebar, **Then** the navigation order is: TODAY, GOALS, MR. BLOOM, STATISTICS, SETTINGS. The STATISTICS item shows a bar-chart icon.
2. **Given** the user is on any page, **When** they click the STATISTICS sidebar item, **Then** the application navigates to `/statistics` and the STATISTICS item displays the active light-blue background (`--color-active-bg`).
3. **Given** the user is on the Statistics page, **When** they click another sidebar item, **Then** navigation proceeds normally and the active state moves to the clicked item.
4. **Given** a keyboard user focuses the sidebar, **When** they tab to the STATISTICS item and press Enter, **Then** navigation to `/statistics` occurs. The item displays a visible focus ring.

---

### User Story 6 — Change Date Range (Priority: P3)

A user changes the visible reporting date range using the dropdown selector in the upper-right corner. The summary cards, calendar, and chart update to reflect the selected range.

**Why this priority**: Date-range selection requires integration with local typed data; the default range is sufficient for the MVP visual match. This story ensures the control is interactive.

**Independent Test**: Can be tested by opening the date-range dropdown, selecting a different range, and verifying the displayed values update.

**Acceptance Scenarios**:

1. **Given** the Statistics page displays `Jun 1 - 14, 2026`, **When** the user clicks the date-range selector, **Then** a dropdown or picker presents available date-range options.
2. **Given** the date-range dropdown is open, **When** the user selects a different range, **Then** the selector updates its displayed text and the summary card values, calendar, and chart reflect the new range using typed local data.

---

### Edge Cases

- What happens when a month has no studied days? All calendar cells display the "no record" neutral styling; the legend still shows both states.
- What happens when the study time for all days in the chart is zero? All bars show the minimal neutral baseline marker; no bar extends upward; value labels all read `0h`.
- What happens when only one page of plan history exists? The pagination controls are visible but both previous and next buttons are disabled. The page indicator reads `1 / 1`.
- What happens when the plan history is empty after applying a filter? The table body shows an empty state message (e.g., `No plans found`); pagination is hidden or all controls are disabled.
- What happens when the window is smaller than 1280 × 800? The authoritative composition remains designed for 1280 × 800. The layout may clip or show a scrollbar but must not break, rearrange, or collapse.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST render a Statistics page at the `/statistics` route accessible via sidebar navigation.
- **FR-002**: The system MUST add a `STATISTICS` navigation item with a bar-chart icon to the shared sidebar, positioned between `MR. BLOOM` and `SETTINGS`, on all main application pages.
- **FR-003**: The `STATISTICS` sidebar item MUST display the active light-blue background (`--color-active-bg`) when the user is on the Statistics page, and MUST show the default state on all other pages.
- **FR-004**: The system MUST render a bar-chart icon for the Statistics navigation item using the existing `AppIcon` component with a new `statistics` variant. The icon MUST use simple ascending vertical bars, `currentColor`, and match the existing icon sizing system.
- **FR-005**: The Statistics page MUST display a heading `STATISTICS` and subtitle `Your progress, one day at a time.` in the upper section.
- **FR-006**: The Statistics page MUST display a date-range selector in the upper-right area showing `Jun 1 - 14, 2026` with a calendar icon and dropdown chevron.
- **FR-007**: The date-range selector MUST open to allow the user to change the visible reporting range. When a new range is selected, the summary cards, calendar, and chart MUST update using typed local data.
- **FR-008**: The system MUST render three summary cards in a single horizontal row:
  - Study Time: clock icon, label `STUDY TIME`, value `24h 30m`
  - Study Days: calendar icon, label `STUDY DAYS`, value `10 days`
  - Plans: document icon, label `PLANS`, value `8 complete / 3 unfinished`
- **FR-009**: Each summary card MUST use the shared cream background (`--color-bg-primary`), match the reference border treatment, and fit on one row without wrapping.
- **FR-010**: The system MUST render a Study Calendar panel titled `STUDY CALENDAR` containing month navigation (previous/next buttons), a centered month label, weekday headings (Mon–Sun), and a 7-column day grid.
- **FR-011**: The calendar MUST display June 2026 by default, with days 1–9, 11, 12, and 14 styled as "studied" (green fill) and all other days styled as "no record" (neutral gray). A legend below the grid MUST label both states.
- **FR-012**: The calendar previous and next month buttons MUST change the visible month. The panel MUST NOT resize during navigation. Buttons MUST use the existing compact icon-button pattern and MUST have accessible labels (`aria-label`) for "Previous month" and "Next month".
- **FR-013**: Calendar dates MUST be generated from typed data, not repeated copied markup. The grid MUST calculate correct first-weekday offset and number of days for any displayed month.
- **FR-014**: The system MUST render a Daily Study Time panel titled `DAILY STUDY TIME` with subtitle `Jun 8 - 14`, displaying a seven-day vertical bar chart with the following data: Mon 2h, Tue 3h, Wed 0h, Thu 2.5h, Fri 4h, Sat 0h, Sun 3h.
- **FR-015**: The bar chart MUST display green bars with value labels above each bar and weekday labels below the baseline. Zero-value days MUST show a small neutral baseline marker visible in the reference. The chart MUST NOT use a third-party charting library.
- **FR-016**: The bar chart MUST be implemented with semantic markup and CSS using the existing color and typography tokens. Chart data MUST be typed and data-driven.
- **FR-017**: The system MUST render a Plan History panel titled `PLAN HISTORY` with filter buttons (`All`, `Completed`, `Unfinished`), a data table, and pagination controls.
- **FR-018**: The Plan History table MUST have columns `DATE`, `PLAN`, `TASKS`, `STATUS`, and a row navigation chevron. The default filter `All` MUST display four rows matching the reference data.
- **FR-019**: Only one filter button MUST be active at a time. The active filter MUST display the light-blue selected state (`--color-active-bg`). Clicking a filter MUST update the visible plan rows.
- **FR-020**: Pagination MUST display `Showing 4 of 11 plans`, previous/next page buttons, and a page indicator `1 / 3`. Previous MUST be disabled on page 1. Next MUST be disabled on the last page.
- **FR-021**: Plan status MUST be displayed using the existing status treatment: `Completed` with a green filled circle-check icon, `Unfinished` with a neutral circle-empty icon.
- **FR-022**: Row chevrons MUST be interactive and keyboard accessible. If the plan-details destination is unfinished, navigation MUST remain local using typed data.
- **FR-023**: All content MUST fit within the 1280 × 800 canvas without unintended body-level scrolling. The layout MUST preserve the existing shared title-bar height (36px) and sidebar width (160px).
- **FR-024**: The page MUST NOT import, reference, or use the design reference image (`statistic.png`) in runtime code.
- **FR-025**: The page MUST use the existing shared cream/beige content surface tokens. The page MUST NOT introduce a Statistics-specific theme or hardcoded replacement palette.
- **FR-026**: The page route MUST NOT be a single monolithic Svelte component. Statistics-specific organisms (summary row, calendar panel, chart panel, history panel) MUST be separate components.
- **FR-027**: The page MUST NOT create duplicate shared components. No new generic Card, Button, Select, Badge, Sidebar, TitleBar, Pagination, or Icon component may be introduced. Reuse existing feature patterns or extend via typed props/variants.
- **FR-028**: Existing Today, Goals, Mr. Bloom, and Settings pages MUST remain functional after the Statistics sidebar addition.

### Accessibility Requirements

- **FR-029**: The page MUST use semantic headings (`h1` for STATISTICS, `h2` for panel titles).
- **FR-030**: The Plan History table MUST use proper table markup with `<th>` elements associated to their columns.
- **FR-031**: All interactive elements (filter buttons, pagination buttons, month navigation buttons, row chevrons, date-range selector) MUST have accessible labels.
- **FR-032**: The `STATISTICS` sidebar item MUST include `aria-current="page"` when on the Statistics page.
- **FR-033**: All filter buttons, pagination controls, and navigation buttons MUST be keyboard accessible (focusable, activatable via Enter/Space).
- **FR-034**: All interactive elements MUST display visible focus states using the existing focus-ring token (`--color-focus-ring`).
- **FR-035**: The bar chart MUST provide text alternatives for every data point (e.g., `aria-label="Monday: 2 hours"`).
- **FR-036**: Status indicators MUST NOT rely on color alone; each MUST include a distinct icon shape (filled circle-check vs. open circle) and text label.
- **FR-037**: The page MUST maintain sufficient color contrast per WCAG 2.1 AA using the existing design token palette.
- **FR-038**: Animations, if any, MUST respect `prefers-reduced-motion`.

### Key Entities

- **StatisticsDateRange**: Represents the selected reporting period with start and end dates, formatted for display (e.g., `Jun 1 - 14, 2026`).
- **SummaryMetrics**: Contains total study time (hours, minutes), study day count, completed plan count, and unfinished plan count for the active date range.
- **CalendarDayState**: Represents a single calendar day with its date and study status (studied or no-record).
- **CalendarMonth**: Contains the year, month number, and an array of `CalendarDayState` entries.
- **DailyStudyEntry**: Represents a single day's study duration (day label, hours value) for the bar chart.
- **PlanHistoryEntry**: Contains plan date, plan name, completed task count, total task count, and completion status (Completed or Unfinished).
- **HistoryFilter**: Enumeration of `All`, `Completed`, `Unfinished` — controls which plan rows are visible.
- **PaginationState**: Contains current page number, total page count, items per page, and total item count.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The Statistics screen visually matches the reference image `statistic.png` at the fixed 1280 × 800 canvas, verifiable by side-by-side comparison of layout, spacing, colors, typography, icons, borders, and component proportions.
- **SC-002**: The STATISTICS sidebar item is visually present between MR. BLOOM and SETTINGS on all five main application pages (Today, Goals, Mr. Bloom, Statistics, Settings), verifiable by navigating to each page and inspecting the sidebar.
- **SC-003**: All three summary cards display their reference icons, labels, and values within a single horizontal row, verifiable by visual inspection.
- **SC-004**: The Study Calendar renders the correct June 2026 day states and month navigation works, verifiable by clicking previous/next and observing the month label and grid update.
- **SC-005**: The Daily Study Time bar chart renders all seven days with correct proportions, value labels, and zero-day neutral markers, verifiable by visual comparison to the reference.
- **SC-006**: Plan History displays the reference rows, and filtering/pagination controls work correctly, verifiable by clicking each filter and navigating through pages.
- **SC-007**: All content fits within 1280 × 800 without unintended scrolling, verifiable by running the application at 1280 × 800 and confirming no scrollbar appears on the main content area.
- **SC-008**: No duplicate shared components are introduced, verifiable by repository search for new generic Card, Button, Badge, Select, Sidebar, TitleBar, Pagination, or Icon components.
- **SC-009**: Keyboard navigation works for all interactive elements (sidebar item, filters, pagination, month buttons, date-range selector, row chevrons), verifiable by tab-navigating through the page.
- **SC-010**: Existing pages (Today, Goals, Mr. Bloom, Settings) remain functional after the sidebar update, verifiable by navigating to each page and confirming no regressions.
- **SC-011**: All type-checking, linting, accessibility, and build checks pass, verifiable by running the project's standard validation commands.

## Assumptions

- The design reference `design-assets/app/references/statistic.png` is the authoritative visual target. Minor sub-pixel variations are acceptable; structural deviations are not.
- Backend statistics endpoints are not yet available. All data displayed on the Statistics page will use typed local view-model/mock data until real backend integration is implemented in a future specification.
- The existing `AppIcon` component will be extended with a `statistics` variant (simple ascending bar-chart SVG path). No new icon component is created.
- The existing `SidebarNavigationItem` component accepts the necessary props to render the Statistics entry without modification to its API.
- Feature-specific atoms and molecules (e.g., in `features/today/`, `features/goals/`, `features/mr-bloom/`) are not intended for cross-feature reuse. Statistics will create its own feature-specific components where no genuine shared equivalent exists.
- The plan-details destination (row chevron navigation target) does not exist yet. Row chevrons will be interactive but navigation will be handled locally with no-op or typed placeholder behavior.
- The shared application shell (`+layout.svelte`), `DesktopTitleBar`, and `AppSidebar` are the only shared components that require modification (sidebar entry addition and icon variant addition).
- The date-range selector dropdown behavior may use a simple local implementation since no shared Select/Dropdown component exists at the shared level.
- The calendar "studied" days for June 2026 are: 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14 — as observed in the reference image.
- No mobile, responsive, or alternate-resolution layouts are required. The Statistics page targets exactly 1280 × 800.
