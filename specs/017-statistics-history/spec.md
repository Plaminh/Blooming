# Feature Specification: Statistics and Plan History

**Feature Branch**: `[017-statistics-history]`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Create Spec 017 — Statistics and Plan History for Blooming. Aggregate the user’s focus time and study days..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Statistics Summary (Priority: P1)

Users can view a high-level summary of their productivity for a selected period, including total focus time, distinct study days, completed plans, and unfinished plans.

**Why this priority**: Core value of the statistics feature, giving users immediate feedback on their overall progress and consistency.

**Independent Test**: Can be fully tested by selecting different predefined reporting periods and verifying the displayed summary totals against known persisted records.

**Acceptance Scenarios**:

1. **Given** a user with several completed focus sessions across multiple days, **When** they view the current week's statistics summary, **Then** the total valid focus time and number of distinct study days are accurately calculated and displayed.
2. **Given** multiple focus sessions occurring on the same local calendar date, **When** the summary is viewed, **Then** those sessions count as a single study day.
3. **Given** a focus session containing paused time, **When** total focus time is calculated, **Then** the paused time is excluded.
4. **Given** running, paused, abandoned, invalid, or incomplete focus sessions, **When** total focus time is calculated, **Then** they are excluded from completed focus totals.
5. **Given** a user with no historical data in the selected period, **When** they view the statistics summary, **Then** the summary displays valid zero values (e.g., 0 hours, 0 days, 0 plans).

---

### User Story 2 - View Daily Heatmap/Chart Data (Priority: P1)

Users can view their daily focus/activity values through a heatmap or chart for the selected reporting period to identify trends.

**Why this priority**: Visualizing daily habits is essential for the user to understand their consistency over time.

**Independent Test**: Can be tested by verifying the daily data array matches the selected reporting period's boundaries and actual persisted activity, including days with zero activity.

**Acceptance Scenarios**:

1. **Given** a selected reporting period containing days with no activity, **When** the daily chart data is loaded, **Then** it includes chronologically ordered entries with zero-activity for those dates.
2. **Given** focus sessions crossing or close to the local midnight boundary, **When** daily aggregation occurs, **Then** they are handled consistently according to the local timezone and not double-counted.
3. **Given** a user's daily data request, **When** the data is aggregated, **Then** it never includes records belonging to another user.
4. **Given** identical repeated requests for unchanged data, **When** the daily chart data is loaded, **Then** consistent results are returned every time.

---

### User Story 3 - Compare Completed and Unfinished Plans (Priority: P2)

Users can compare the number of completed plans versus unfinished plans within a selected period to understand their planning effectiveness.

**Why this priority**: Helps users realize if they are over-planning or successfully completing what they set out to do.

**Independent Test**: Can be tested by creating various plans with different statuses and verifying they are correctly classified and counted once.

**Acceptance Scenarios**:

1. **Given** a mix of completed, draft, cancelled, and unfinished plans, **When** plan completion statistics are calculated, **Then** completed and unfinished plans are counted correctly and mutually exclusively.
2. **Given** historical plans modified through re-planning, **When** statistics are calculated, **Then** they do not result in duplicate statistical counts.
3. **Given** plans with mixed task outcomes, **When** the plan is classified for statistics, **Then** the persisted plan status (or existing product completion rule) is used rather than guessing from the UI state.

---

### User Story 4 - Browse Paginated Plan History (Priority: P2)

Users can browse a paginated history of their plans, seeing details like plan identifier, title, date, status, completion summary, and last update time.

**Why this priority**: Users need to review past days to reflect on what was done and what was missed.

**Independent Test**: Can be tested by verifying that navigation through pages returns correct records with a stable page size, without missing or duplicated items for unchanged data.

**Acceptance Scenarios**:

1. **Given** more than one page of historical plans, **When** a user navigates between the first, middle, and final Plan History pages, **Then** the ordering is deterministic (newest first by default) with no duplicates or omissions.
2. **Given** a request for a page beyond the final page, **When** the request is made, **Then** an empty list is returned gracefully.
3. **Given** multiple records sharing the identical date or ordering timestamp, **When** paginating through them, **Then** the sorting remains deterministic.

---

### User Story 5 - Filter Plan History (Priority: P3)

Users can apply basic filters (such as status and date range) to their Plan History to find specific past plans.

**Why this priority**: Important for users with a large history, though less critical than basic viewing and pagination.

**Independent Test**: Can be tested by applying combined filters and verifying the returned subset matches all filter criteria.

**Acceptance Scenarios**:

1. **Given** a populated Plan History, **When** a user applies combined status and date filters, **Then** only plans matching both criteria are returned, and the results start from the first page.
2. **Given** filters that do not match any existing records, **When** applied, **Then** a clear empty/no-results state is displayed.
3. **Given** invalid date ranges or unsupported filter values, **When** submitted, **Then** they are rejected clearly and gracefully.
4. **Given** two different users, **When** one applies filters to their Plan History, **Then** it must maintain complete isolation and never return another user's records.

### Edge Cases

- Sessions with zero actual duration (should not contribute to focus time).
- Sessions with missing actual duration.
- Sessions with malformed or inconsistent timestamps.
- Very long valid focus sessions (e.g., user forgot to stop the timer).
- Timezone changes between the time a session was recorded and when it is viewed.
- Daylight-saving transitions where applicable.
- Empty plans (no tasks).
- Future plans (should not contribute to historical statistics).
- Cancelled, archived, or deleted plans (must be handled based on existing visibility rules).
- Requests for non-positive page or page-size values in pagination.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST aggregate total valid focus time from persisted, finished focus sessions with a valid actual duration within the selected period.
- **FR-002**: The system MUST calculate the number of distinct study days, defining a study day as a local date containing at least one qualifying focus session.
- **FR-003**: The system MUST aggregate the number of completed and unfinished plans according to existing product terminology, ensuring completed plans are mutually exclusive from unfinished ones.
- **FR-004**: The system MUST provide chronologically ordered daily focus/activity data suitable for a heatmap or chart, including zero-activity dates for continuous series where required, localized to the user's timezone.
- **FR-005**: The system MUST support predefined reporting periods (e.g., current week, current month, recent fixed-day range) whose boundaries respect the user's local timezone.
- **FR-006**: The system MUST provide paginated Plan History, returning a stable page size, deterministic ordering (newest first by default), and pagination metadata (e.g., total count).
- **FR-007**: The system MUST expose user-facing identifying details for each Plan History item (e.g., title, date, status, completion summary) relying strictly on existing product concepts.
- **FR-008**: The system MUST support combined basic filters (plan status, date range) for the Plan History, applying pagination after filters and resetting to the first page when filters change.
- **FR-009**: The system MUST strictly scope all statistics and history data to the authenticated user and prevent cross-user data leakage.
- **FR-010**: The system MUST explicitly classify draft, cancelled, archived, deleted, or future plans according to the existing domain rules and exclude future plans from completed statistics.
- **FR-011**: The system MUST NOT modify historical focus sessions, tasks, or plans merely to generate statistics.

### Key Entities

- **Focus Session**: Represents a period of time the user focused on a task. Used to derive actual focus time and study days. (Existing entity)
- **Plan**: Represents a daily or long-term collection of tasks. Used to derive plan completion statistics and Plan History records. (Existing entity)
- **User**: The authenticated owner of the plans and sessions. Used to scope all data access. (Existing entity)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Summary totals for focus time, study days, and plan completion match exactly the qualifying persisted records for the selected period without duplicate counting.
- **SC-002**: Daily chart/heatmap values reconcile with the reported total focus time for the corresponding period.
- **SC-003**: Plan History pagination produces no duplicates or omissions for unchanged data across all pages.
- **SC-004**: Combined filters accurately return only matching plans, with an empty state displayed when no matches exist.
- **SC-005**: The entire Statistics screen renders exclusively using real, persisted application data, without reliance on mock, fixture, or hardcoded data in the completed feature.
- **SC-006**: Test coverage ensures data belonging to another user never appears in a user's statistics or history.

## Assumptions

- Predefined reporting periods and their boundary calculations will align with standard calendar boundaries (e.g., week starting on Sunday/Monday based on locale/settings) or existing UI patterns.
- Existing domain rules clearly define what constitutes a "completed" versus "unfinished" plan, as well as the visibility of deleted/archived records.
- The system already captures focus sessions with timestamps and actual durations that can be confidently tied to a local date.
- The UI will handle the presentation of zero-states and empty datasets provided by the backend.

## Out of Scope

- AI-generated productivity insights, predictions, or recommendations.
- Comparisons with other users, leaderboards, or social statistics.
- Real-time streaming dashboards.
- Exporting data to CSV, PDF, or spreadsheets.
- Custom chart builders or arbitrary analytics queries.
- Mobile-specific behavior.
- Redesigning the existing Statistics page (beyond plugging in real data).
- Modifying historical data to improve or "clean up" reported statistics.
