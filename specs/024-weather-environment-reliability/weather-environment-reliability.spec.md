# Weather Environment Reliability, Privacy, and Scene Consistency

## User Scenarios & Testing

### User Story 1 - Selecting a Specific Location (Priority: P1)
As a user setting up my widget, I want to search for and select a specific location by name, so that I can see relevant weather without exposing my precise device coordinates.
**Why this priority**: Correct location persistence is the foundation for all weather functionality.
**Independent Test**: Search for "London" in Settings, select a candidate, and verify that human-readable name, latitude, and longitude are saved to settings and used for subsequent weather refreshes.
**Acceptance Scenarios**:
1. **Given** the user is in the onboarding or settings weather section
   **When** they type a valid place name and select a candidate from the dropdown
   **Then** the human-readable name is displayed, and its approximate coordinates are persisted securely.
2. **Given** the user types a free-text location but does not select a candidate
   **When** they attempt to save settings
   **Then** the application prompts them to explicitly select a valid location from the list, or rejects the input.
3. **Given** the user's previously saved place
   **When** a routine weather refresh occurs
   **Then** the forecast API is called directly using the saved coordinates without a redundant geocoding request.

### User Story 2 - Using Approximate Device Location (Priority: P1)
As a privacy-conscious user, I want to optionally use my device's location for weather, so that I get local weather while ensuring my exact coordinates are not tracked or stored.
**Why this priority**: Balancing convenience with privacy is a strict product requirement.
**Independent Test**: Click "Use device location" in settings and verify that the coordinates stored and sent to the backend/provider are rounded to at most two decimal places.
**Acceptance Scenarios**:
1. **Given** the user has not granted location permissions
   **When** they click "Use device location"
   **Then** the browser requests permission, and upon grant, approximate coordinates (rounded to 2 decimals) are saved.
2. **Given** the user clicks "Use device location"
   **When** the location is successfully acquired
   **Then** a generic label like "Approximate location" is displayed as the location name instead of raw coordinates.
3. **Given** the device location cannot be acquired (denied or timeout)
   **When** the user attempts to use device location
   **Then** a clear error message is shown and the previously saved location (or none) remains active.

### User Story 3 - Resilient Weather Display (Priority: P2)
As a user, I want the widget to gracefully handle temporary weather provider outages, so that my ambient scene doesn't abruptly switch to clear skies when it is actually raining.
**Why this priority**: Prevents jarring visual transitions and preserves the ambient experience during temporary API failures.
**Independent Test**: Simulate a provider outage, wait past the 15-minute refresh interval, and verify the scene retains its last known weather state (up to 2 hours) with a `STALE` status.
**Acceptance Scenarios**:
1. **Given** a successful initial weather fetch (e.g., RAIN)
   **When** the next scheduled refresh fails (timeout, 5xx, or rate limit)
   **Then** the scene continues to show RAIN and marks the status as `STALE`.
2. **Given** the last successful fetch was more than two hours ago
   **When** the weather refresh continues to fail
   **Then** the status changes to `UNAVAILABLE` and the widget falls back to a safe default (CLEAR) without displaying a heavy error UI.
3. **Given** the backend receives an unknown weather code from the provider
   **When** parsing the response
   **Then** it does not incorrectly report success; it handles it as an error to retain the previous state.

### User Story 4 - Consistent Scene Across Views (Priority: P2)
As a user, I want the weather and time-of-day to be identical whether I am looking at the standalone widget or the in-app Garden panel, so that the ambient experience feels cohesive.
**Why this priority**: Eliminates conflicting visual states that break immersion.
**Independent Test**: Load the app with RAIN weather; both the widget and the Garden Panel should render rain, driven by a single shared environment state.
**Acceptance Scenarios**:
1. **Given** the weather updates to THUNDERSTORM
   **When** the user views the Garden Panel
   **Then** the Garden Panel immediately reflects the THUNDERSTORM state instead of permanently showing CLEAR.
2. **Given** the user changes their timezone in the system settings
   **When** the app is launched
   **Then** the single timezone helper updates the frontend state, and both the widget and Garden Panel update their daylight/night cycle concurrently.

### User Story 5 - Configurable Scene Season (Priority: P3)
As a user, I want to manually override the season of my widget scene, so that I can enjoy a winter or summer aesthetic regardless of my physical location or hemisphere.
**Why this priority**: Allows personalization of the ambient scene without affecting core gameplay.
**Independent Test**: Change the season setting from AUTO to WINTER in settings, and verify the widget immediately displays winter vegetation.
**Acceptance Scenarios**:
1. **Given** the user's season setting is `AUTO`
   **When** the widget renders
   **Then** it uses the saved approximate latitude to correctly determine the current season for their hemisphere.
2. **Given** the user overrides the season to `AUTUMN`
   **When** the widget renders
   **Then** autumn vegetation is displayed, overriding the physical hemisphere calculation.

### User Story 6 - Respectful Rain Animation (Priority: P2)
As an accessibility-conscious user, I want the rain animation to pause or simplify when appropriate, so that it doesn't cause motion sensitivity or waste device resources.
**Why this priority**: Accessibility and performance are critical for a background ambient feature.
**Independent Test**: Enable `prefers-reduced-motion` in the OS and verify the rain animation does not render or is replaced by a static equivalent.
**Acceptance Scenarios**:
1. **Given** the user enables "Reduce Motion" at the OS level
   **When** the weather condition is RAIN or THUNDERSTORM
   **Then** the rain animation is paused or hidden.
2. **Given** the application tab is hidden or the widget is in a hidden state
   **When** the scene is active
   **Then** the rain animation pauses rendering to preserve performance.
3. **Given** the user disables weather animations in settings
   **When** the weather condition is RAIN
   **Then** the rain animation is not shown, though the overcast/cloudy visual state may remain.


## Edge Cases

- **Legacy Users without Coordinates**: Existing users may only have a free-text string in their settings. The backend will treat these as "location requires confirmation" (status UNAVAILABLE) and the frontend will display a prompt to re-select their location rather than attempting to geocode an unvalidated string at runtime.
- **Hemisphere Detection Fallback**: If the latitude is strictly unavailable (e.g., location disabled) and the season is set to AUTO, the system defaults to Northern Hemisphere month mapping.
- **Debounced Search Input**: Rapid typing in the location search must debounce API requests to avoid rate limits on the Open-Meteo geocoding service.
- **Out-of-Order Refresh Responses**: If multiple weather refreshes are triggered (e.g., focus event shortly after a scheduled interval), the frontend must deduplicate requests or ignore older responses that arrive late.


## Requirements

### Functional Requirements

1.  **FR-001**: The application MUST expose an authenticated place search API that accepts a text query, returns up to 5 Open-Meteo geocoding candidates (name, approx lat/long), and handles provider failures explicitly.
2.  **FR-002**: The frontend MUST require explicit selection of a search candidate; free-text strings MUST NOT be saved as valid locations.
3.  **FR-003**: The "Use device location" feature MUST round retrieved coordinates to a maximum of two decimal places before persisting or transmitting them.
4.  **FR-004**: The backend MUST store the selected location as a human-readable name and fixed-precision approximate coordinates in the canonical SQL user settings schema.
5.  **FR-005**: The weather API MUST return a typed response containing `condition` (CLEAR, CLOUDY, OVERCAST, RAIN, THUNDERSTORM), `status` (OK, STALE, UNAVAILABLE, DISABLED), and `updated_at`.
6.  **FR-006**: The weather forecast fetch MUST use the cached, rounded coordinates and MUST NOT perform runtime geocoding.
7.  **FR-007**: The backend MUST cache forecast responses for 15 minutes and place-search responses for 24 hours, using bounded TTL caches with defined eviction behavior.
8.  **FR-008**: The backend MUST return a `STALE` status with the last known condition if a provider request fails but a successful result was cached within the last two hours.
9.  **FR-009**: The frontend MUST implement a single shared environment store that manages weather condition, timezone, season, and animation state for both the standalone widget and the Garden Panel.
10. **FR-010**: The frontend MUST synchronize the device's timezone with the persisted timezone on startup if they differ, using a single timezone helper source.
11. **FR-011**: The frontend MUST support a configurable season setting (AUTO, SPRING, SUMMER, AUTUMN, WINTER) that overrides hemisphere-based calculations when manually set.
12. **FR-012**: The rain animation MUST pause or not render when the document is hidden, the widget is hidden, weather animation is disabled, or `prefers-reduced-motion` is active.
13. **FR-013**: The `/widget-preview` route MUST support query parameters to override and deterministically preview time, season, and weather combinations (e.g., `?time=NIGHT&season=WINTER&weather=RAIN`).
14. **FR-014**: The feature MUST NOT impact gameplay, rewards, streaks, or the scheduler, remaining strictly an ambient visual effect.

### Key Entities

- **User Settings**: Extended to include `weather_location_name` (string), `weather_lat` (NUMERIC(5, 2)), `weather_lon` (NUMERIC(6, 2)), and `scene_season` (AUTO, SPRING, SUMMER, AUTUMN, WINTER).
- **Weather Status**: The typed state of the current weather fetch (`condition`, `status`, `updated_at`).
- **Environment Store**: The frontend state primitive holding the unified daytime, season, and weather condition for all scene renderings.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of newly saved weather locations store coordinates rounded to two decimal places or fewer.
- **SC-002**: Weather refresh operations perform 0 geocoding requests (only forecast requests) once a location is saved.
- **SC-003**: The widget and Garden Panel reflect identical time-of-day and weather states 100% of the time during active sessions.
- **SC-004**: During a simulated 30-minute provider outage, active widgets maintain their last known weather state without falling back to CLEAR until the 2-hour staleness threshold is reached.
- **SC-005**: All defined critical preview combinations (e.g., NIGHT × OVERCAST, WINTER × RAIN) render correctly via `/widget-preview` without requiring live API data.

## Assumptions

- Open-Meteo remains the single weather provider; no secondary fallback provider is required for this feature.
- Bounded TTL caching can be implemented via `cachetools` or standard standard library `lru_cache` with custom expiration wrappers, conforming to backend conventions.
- Legacy settings fields (like the existing unstructured `weather_location` text field) remain in the canonical SQL schema; existing databases need a separate additive update.
- "Approximate location" implies rounding to 2 decimal places, which corresponds to ~1.1km accuracy, providing sufficient localization for weather while protecting exact street addresses.
