# Feature Specification: Compact Desktop Companion Widget

**Feature Branch**: `feature/ui-ux`

**Created**: 2026-09-11

**Status**: Implemented — manual acceptance pending

**Input**: User description: "Create a feature specification for the first Blooming UI feature: a compact desktop companion widget. The specification must be based on the detailed visual description and the Figma-generated reference code..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Paused Timer State (Priority: P1)

Users need to see when their session is paused, with options to resume or end the session.

**Why this priority**: Essential core interaction for focus session management and user feedback.

**Independent Test**: Can be fully tested by previewing the "Paused timer" state fixture, ensuring timer text reads exactly "18:42", the companion animates through the four supplied sleeping frames (cyan sleep effects baked into those frames; no separate sleep overlay), the speech text is exactly "Paused. Take your time.", and the green "RESUME" (with play icon) and cream "END" (with stop icon) buttons appear in the correct order.

**Acceptance Scenarios**:

1. **Given** the widget is in the "Paused" state fixture, **Then** the visual layout displays one sleeping robot cat near the lower-left, cycles columns `0–3` in order, uses only the cyan sleep effects baked into those frames, and shows speech text exactly "Paused. Take your time."
2. **Given** the widget is in the "Paused" state fixture, **Then** the preview timer reads exactly "18:42".
3. **Given** the widget is in the "Paused" state fixture, **Then** the buttons are displayed in the lower-right, ordered correctly: green "RESUME" (with play icon), cream "END" (with stop icon).
4. **Given** the widget is in the "Paused" state fixture, **When** the user clicks "RESUME" or "END", **Then** the respective mock callback is invoked.

---

### User Story 2 - View Behind Schedule State (Priority: P1)

Users need to be alerted when they are behind schedule so they can adjust their plan or acknowledge the delay.

**Why this priority**: Core value proposition for realistic daily planning and recovery.

**Independent Test**: Can be fully tested by previewing the "Behind schedule" state fixture, ensuring the companion is awake with orange alert marks, the exact text "We are 35 minutes behind. Adjust the remaining plan?" is shown, no timer is displayed, and the green "REPLAN", cream "LATER", and cream "OPEN" buttons are ordered left to right.

**Acceptance Scenarios**:

1. **Given** the widget is in the "Behind schedule" state fixture, **Then** the visual layout displays an awake robot cat near the lower-left, orange alert marks above it, and speech text exactly "We are 35 minutes behind. Adjust the remaining plan?".
2. **Given** the widget is in the "Behind schedule" state fixture, **Then** no timer is displayed on the right.
3. **Given** the widget is in the "Behind schedule" state fixture, **Then** the buttons are ordered left to right: "REPLAN" (green), "LATER" (cream), and "OPEN" (cream).
4. **Given** the widget is in the "Behind schedule" state fixture, **When** the user clicks "REPLAN", "LATER", or "OPEN", **Then** the corresponding mock callback is invoked.

---

### User Story 3 - View Reminders State (Priority: P2)

Users need to see active reminders from their schedule directly on the widget.

**Why this priority**: Important for situational awareness, but secondary to core timer functions.

**Independent Test**: Can be fully tested by previewing the "Reminders" state fixture, verifying the awake companion, pink alert marks, the bell icon, the heading "2 REMINDERS", the exact preview items "Start Database" and "Review milestone", and the green "VIEW" and cream "DISMISS" buttons.

**Acceptance Scenarios**:

1. **Given** the widget is in the "Reminders" state fixture, **Then** it displays an awake robot cat near the lower-left and pink alert marks above it.
2. **Given** the widget is in the "Reminders" state fixture, **Then** it displays a reminder panel with a bell icon and a heading exactly "2 REMINDERS".
3. **Given** the widget is in the "Reminders" state fixture, **Then** it exactly displays two items: "Start Database" and "Review milestone".
4. **Given** the widget is in the "Reminders" state fixture, **Then** the buttons are ordered left to right: "VIEW" (green) and "DISMISS" (cream).
5. **Given** the widget is in the "Reminders" state fixture, **When** the user clicks "VIEW" or "DISMISS", **Then** the respective mock callback is invoked.

---

### User Story 4 - View Offline State (Priority: P2)

Users need to know when the system is offline so they understand why data might not be syncing.

**Why this priority**: Important informational state, but involves no immediate action.

**Independent Test**: Can be fully tested by previewing the "Offline" state fixture, ensuring the happy cat, the offline Wi-Fi symbol with a red '×', the text "Offline – changes will sync later.", the preview time "14:06", and the absence of action buttons.

**Acceptance Scenarios**:

1. **Given** the widget is in the "Offline" state fixture, **Then** it displays a happy robot cat near the lower-left, and an offline Wi-Fi symbol with a red `×`.
2. **Given** the widget is in the "Offline" state fixture, **Then** it displays speech text exactly "Offline – changes will sync later." and preview time exactly "14:06" (as a test fixture value, not a hard-coded production time).
3. **Given** the widget is in the "Offline" state fixture, **Then** it contains no action buttons.

### Edge Cases

- **Long reminder labels**: Remain on one line and use an ellipsis without expanding the reminder panel.
- **Varying reminder counts**: The initial preview fixture displays exactly two reminders. With one reminder, use the singular heading `1 REMINDER`. With more than two reminders, show the first two items and a compact `+N more` indicator without increasing widget height. The zero-reminder state is not selected as the active reminders presentation; deciding the fallback state belongs to future state-selection logic.
- **Missing optional text**: If optional timer/time text is absent, omit the timer text and preserve the remaining layout without showing fake data.
- **Large numerical values**: Delay values up to three digits must fit without overlapping surrounding content.
- **Missing artwork**: The supplied runtime PNG assets in VR-008 and VR-009 exist and MUST NOT be treated as missing. Custom SVG/CSS indicators and chrome icons are feature-local UI components, not missing raster assets. Missing or unmatched artwork MUST NOT be silently replaced by dimensional placeholders, emojis, generic animals, unrelated mascots, generic icon libraries, or flattened screenshots.
- **Unconnected callbacks**: An unconnected callback must not crash the preview.
- **Window resizing**: Slight resizing must preserve the widget composition, prevent scrollbars, and avoid clipping.
- **Long translated text**: Long translated speech text may wrap within the existing bubble but must be line-clamped before it changes the fixed widget height.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement one shared widget shell providing the outer border, dark teal title bar matching `removed reference artwork` (logo, `BLOOMING`, and window controls in the band above `y ≈ 64` on the `680 × 289` canvas), layered background scene (bright blue sky, city skyline, green foliage), logo, and "BLOOMING" title for all four states.
- **FR-002**: System MUST render custom window controls (minimize, maximize/restore, close) in the custom title bar, and the ability to drag the window via the title bar.
- **FR-003**: System MUST NOT render the native OS title bar in the final presentation.
- **FR-004**: System MUST implement state-specific content through typed props or a local presentation model (no application-wide state management or backend dependency).
- **FR-005**: System MUST provide a local preview mechanism (e.g., a dev surface/storybook) to view all four widget states using mock data. The UI MUST show only one active state at a time, avoiding separately duplicated widgets, and the development preview selector MUST NOT appear inside the production widget.
- **FR-006**: System MUST only use UI interactions (callbacks) and real text rendering, subject to the source-only rules in VR-015.
- **FR-007**: System MUST NOT implement real timers, focus-session persistence, AI replanning, reminder scheduling, connectivity detection, backend endpoints, databases, or data synchronization logic.
- **FR-008**: The supplied runtime PNG assets already exist and MUST be used. Custom SVG/CSS indicators and chrome icons are feature-local UI components, not missing user-supplied raster assets.

### Visual & Acceptance Requirements

- **VR-001**: The default design canvas MUST be exactly `680 × 289` to match `removed reference artwork`. Earlier “approximately `700 × 310`” sizing is superseded. Comparisons MUST preserve the `680:289` aspect ratio and MUST NOT stretch the widget to `700 × 310`.
- **VR-002**: The supplied leaf PNG logo, `BLOOMING` title, and three window controls MUST retain the exact same alignment in all four states. No leaf-balance pill is rendered. All four states MUST share the same background composition and title-bar structure.
- **VR-003**: The thick dark teal/navy outer border MUST remain visible.
- **VR-004**: The companion MUST remain anchored near the lower-left.
- **VR-005**: Speech bubbles MUST use a cream fill, dark outline, and a tail pointing toward the companion.
- **VR-006**: Action buttons MUST be aligned along the lower-right area and MUST preserve the exact state-specific order defined in the user stories. Green buttons are primary; cream buttons are secondary.
- **VR-007**: Text, buttons, title-bar controls, speech panels, and interactive elements MUST remain real UI elements.
- **VR-008**: The MVP widget MUST use these supplied runtime PNG assets:
  - `frontend/static/assets/widget/environment/daytime/morning.png`
  - `frontend/static/assets/widget/environment/season/spring.png`
  - `frontend/static/assets/mr-bloom/mr-bloom-spritesheet.png`
  - `frontend/static/assets/icons/leaf-icon.png`
  - `frontend/static/assets/plants/{monstera,sunflower,bonsai,jasmine,lavender}-spritesheet.png`
  `default-sky.png` and `background-bushes.png` are separate visual layers of the widget background. They MUST contain only sky, clouds, city skyline, foliage, plants, and ground. They MUST NOT contain the robot cat, title bar, logo, speech bubble, reminder panel, status indicators, timer, text, buttons, or window controls. The one-pixel source-dimension difference between the two background layers MUST NOT cause visible seams, clipping, drift, or misalignment in the rendered widget.
- **VR-009**: Mr. Bloom MUST NOT be recreated as SVG. The authoritative source is an irregular `1536 × 1152` sheet with eight 144px rows; the runtime asset MUST be normalized to `1152 × 1152`, `4 × 8`, with `288 × 144` cells. One reusable character component selects the mapped row and only the permitted per-state columns defined in `data-model.md`. The viewport MUST show exactly one complete cell, and reduced-motion users MUST see the first permitted frame. Mapping: `paused` row 7, `behindSchedule` row 6, `offline` row 3, `reminders` row 4.
- **VR-010**: Title bar, outer border, speech bubbles, reminder panel, buttons, timer, and textual content MUST be real Svelte/HTML/CSS UI.
- **VR-011**: The supplied `leaf-icon.png` MUST be used as the title-bar logo. Custom SVG or CSS MUST still be used where appropriate for the bell; play icon; stop icon; Wi-Fi/offline symbol and red `×`; orange schedule alert marks; pink reminder alert marks; and minimize, maximize/restore, and close controls. Paused uses the cyan sleep effects baked into its four supplied frames. There is no separate sleep overlay component. Emojis, generic mismatched icon libraries, unrelated substitute art, and flattened screenshots are NOT acceptable.
- **VR-012**: All runtime PNG and SVG artwork MUST retain transparency where present and crisp pixel-style edges without blurry interpolation.
- **VR-013**: The widget MUST NOT be redesigned as a generic dashboard or modern web card. It MUST NOT introduce glassmorphism, gradients, excessive shadows, unrelated rounded cards, or visual styling inconsistent with the supplied pixel-art reference.
- **VR-014**: Mr. Bloom may animate horizontally only through the selected state's permitted columns in `mr-bloom-spritesheet.png`. Plant sheets are lifecycle atlases, not animation loops: the widget shows exactly one species and one frame `0–15`. The active plant is presentation data only; reward calculation and garden growth stay out of scope.
- **VR-015**: `removed reference artwork` is a source-only visual reference (hybrid SVG, `680 × 289`, vector paths plus embedded rasters). It MUST NOT be moved into `frontend/static/`, bundled at runtime, edited, optimized, re-exported, or overwritten. Title bar, speech/reminder panel, text, buttons, status indicators, and window controls MUST be real Svelte HTML/CSS. Sky, bushes, and Mr. Bloom MUST still come from the runtime PNGs in VR-008.

### Accessibility Requirements

- **AR-001**: Buttons MUST be semantic elements.
- **AR-002**: The widget MUST support keyboard interaction for all core flows.
- **AR-003**: Keyboard focus MUST be visible on all interactive elements.
- **AR-004**: Window controls and icon-only status indicators MUST have accessible names.
- **AR-005**: Text MUST maintain sufficient contrast against backgrounds.
- **AR-006**: Decorative background artwork MUST be excluded from the accessibility tree.
- **AR-007**: Status information MUST NOT be communicated through color alone.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four fixtures can be selected and previewed locally without a backend.
- **SC-002**: At the target `680 × 289` viewport, no text, buttons, window controls, speech panels, companion artwork, or timer values overlap or clip.
- **SC-003**: No scrollbar appears at the target size or between 90% and 110% of the target width and height.
- **SC-004**: Each fixture contains every required state-specific text, pose, status indicator, button, and color treatment as explicitly detailed in the User Stories.
- **SC-005**: Visual acceptance is successfully performed using screenshots of all four fixtures at the VR-001 canvas, with the **reminders** screenshot compared side by side against the source-only reference. Screenshots are manual QA evidence and are not stored in the repository. Final visual acceptance cannot pass with missing or placeholder artwork.
- **SC-006**: All presentation buttons invoke the correct mock callback without throwing exceptions.
- **SC-007**: Minimize, maximize/restore, close, and title-bar dragging each perform their intended action without errors during Tauri verification on both supported desktop platforms: Windows and Linux. If automated verification on both operating systems is unavailable in the current environment, document the unverified platform explicitly rather than claiming it passed.
- **SC-008**: Keyboard focus, semantic-button, accessible-name, and contrast checks pass using standard automated accessibility tooling.
- **SC-009**: Only the selected `mr-bloom-spritesheet.png` cell is visible; no neighboring sprite cell leaks into the widget.
- **SC-010**: Both background layers align without visible seams, clipping, drift, or misalignment at the target viewport.
- **SC-011**: No source-only art is requested or loaded at runtime. Browser/Tauri network inspection shows no request for `widget-reference.svg` or any `removed reference artwork/` path.
- **SC-012**: All runtime images preserve transparency and sharp rendering.
- **SC-013**: Final comparison uses all four widget screenshots at the VR-001 canvas.
- **SC-014**: The finished reminders fixture matches the source-only reference’s proportions, placement, spacing, borders, radii, colors, speech-bubble/panel shape, title-bar layout, button dimensions, typography scale, and character position when both are viewed at the VR-001 canvas.

## Assumptions

- The frontend uses the existing project architecture (SvelteKit + TypeScript + Tauri) as mandated by the project constitution.
- The native window customization permissions and APIs are available and compatible with the current project state.
- The runtime PNG assets listed in VR-008 already exist in the repository and are the mandated character, leaf, plant, and background art for this feature.
- `removed reference artwork` is the source-only composite visual reference for the reminders fixture and is not a runtime dependency.
- Character animation is presentation-only and uses the normalized runtime atlas; no domain timing or persistence is introduced.
