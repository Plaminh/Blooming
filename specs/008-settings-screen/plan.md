# Implementation Plan: Settings Screen

**Branch**: `[008-settings-screen]` | **Date**: 2026-09-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/008-settings-screen/spec.md`

## Summary
Implement a high-fidelity Settings screen for Blooming, reusing the shared application shell (Sidebar, Title bar) while introducing local typed settings management, specific form controls, and validation.

## 1. Technical Context

- **Framework and language versions**: SvelteKit (`@sveltejs/kit` ^2.65.1), Svelte 5 (`^5.56.3`), TypeScript (`~6.0.3`).
- **Tauri integration**: Tauri 2 (`@tauri-apps/api` ^2, `@tauri-apps/cli` ^2). Autostart plugin is **not** present.
- **Actual Settings route**: Will be created at `frontend/src/routes/settings`.
- **Verified styling pipeline**: Global CSS (`$lib/shared/styles/global.css`), CSS variables (`theme.css`). No Tailwind present.
- **Shared shell architecture**: `<DesktopTitleBar>` and `<AppSidebar>` organisms currently used in Today and Goals routes.
- **Asset-serving conventions**: Static images from `frontend/static/assets/` (e.g. `leaf-icon.png`). Sprites rendered via `PlantSprite.svelte` or `SpriteRenderer.svelte`. SVG icons via `AppIcon.svelte`.
- **Current state-management pattern**: Svelte 5 Runes (`$state`, `$derived`) used locally within feature components (e.g. `AuthState.svelte.ts`).
- **Existing validation and testing tools**: Vitest, `@testing-library/svelte`, `svelte-check`.
- **Existing persistence**: None global. Local mocked persistence fallback will be used.

## 2. Constitution Compliance

- **SvelteKit, TypeScript, and Tauri remain unchanged**: Confirmed.
- **Atomic Design is followed**: Yes, using atoms/molecules/organisms in `$lib/features/settings`.
- **Existing shared shell and theme are reused**: Yes, `AppSidebar` and `DesktopTitleBar` are reused.
- **Backend/API scope is not expanded**: Yes, typed local UI state is used.
- **Reference screenshots are never runtime dependencies**: Yes, visual reference is only for design comparison.
- **Existing Today, Goals, Garden, onboarding, and widget screens are preserved**: Yes, testing and visual regression checks are included.
- **No Git branch, commit, or push operation is planned**: Confirmed.

## 3. Route and Navigation Strategy

- **Exact route file**: `frontend/src/routes/settings/+page.svelte`
- **URL**: `http://localhost:5173/settings` (or Tauri standard base).
- **Navigation**: `AppSidebar.svelte` has an item for "SETTINGS". We will add `onClick={() => goto('/settings')}` to it.
- **Active state**: Route will pass `activeRoute="SETTINGS"` to `<AppSidebar>`.
- **Browser fallback**: The same route works in standard browsers. `@tauri-apps/api/window` calls will be wrapped in try/catch or checked for Tauri environment to prevent crashes.

## 4. Shared-versus-feature-specific Ownership

- **Desktop title bar**: Reused unchanged (`$lib/shared/components/organisms/DesktopTitleBar.svelte`).
- **Window-control buttons**: Reused unchanged (part of TitleBar).
- **Shared sidebar**: Reused unchanged (`$lib/shared/components/organisms/AppSidebar.svelte`).
- **Sidebar navigation item**: Reused unchanged (`SidebarNavigationItem.svelte`).
- **Sidebar plant and counters**: Reused unchanged (inside Sidebar).
- **Pixel icon or sprite renderer**: Reused unchanged (`AppIcon.svelte`, `SpriteRenderer.svelte`).
- **Section panel**: Implemented inside Settings.
- **Primary and secondary buttons**: Implemented inside Settings (can generalize later).
- **Text input, Select control, Toggle switch**: Implemented inside Settings.
- **Validation message**: Implemented inside Settings.

## 5. Atomic Design Component Map

**Atoms (`$lib/features/settings/components/atoms/`)**
- `SectionHeading.svelte`
- `TextInput.svelte`
- `SelectField.svelte`
- `ToggleSwitch.svelte`
- `Button.svelte`
- `ValidationMessage.svelte`

**Molecules (`$lib/features/settings/components/molecules/`)**
- `LabeledField.svelte` (Wraps label + any input)
- `AccountIdentity.svelte`
- `SettingsActionGroup.svelte`

**Organisms (`$lib/features/settings/components/organisms/`)**
- `AccountPanel.svelte`
- `GeneralPanel.svelte`
- `FocusTimerPanel.svelte`
- `NotificationsPanel.svelte`
- `SettingsForm.svelte` (The overall form coordinator)

**Page/Template (`src/routes/settings/+page.svelte`)**
- Orchestrates `DesktopTitleBar`, `AppSidebar`, and `SettingsForm`. Instantiates the Settings State.

## 6. Asset Inventory

| Visual element | Real repository path | Render component | Dimensions | Ownership |
| --- | --- | --- | --- | --- |
| Blooming logo | `/assets/...` (Used in TitleBar) | `img` | ~40x40 | Shared |
| Navigation icons | `$lib/shared/components/atoms/AppIcon.svelte` | `AppIcon` | ~24x24 | Shared |
| Sidebar plant | `PlantSprite.svelte` | `PlantSprite` | N/A | Shared |
| Leaf / Water | `/assets/widget/icons/leaf-icon.png`, `AppIcon` | `img`, `AppIcon` | 25x29 | Shared |
| Account/User | `$lib/shared/components/atoms/AppIcon.svelte` (name="user") | `AppIcon` | ~24x24 | Settings/Shared |
| Gear icon | `$lib/shared/components/atoms/AppIcon.svelte` (name="settings") | `AppIcon` | ~24x24 | Settings/Shared |
| Clock icon | `$lib/shared/components/atoms/AppIcon.svelte` (name="clock"?) | `AppIcon` | ~24x24 | Settings/Shared |
| Bell icon | `$lib/shared/components/atoms/AppIcon.svelte` (name="bell"?) | `AppIcon` | ~24x24 | Settings/Shared |
| Dropdown/Toggles| CSS/Inline SVG | N/A | N/A | Settings |

*Note: If specific icons (clock, bell, user) are missing from `AppIcon.svelte`, they must be added to the shared SVG definitions using project asset files.*

## 7. Typed Settings Data Model

*(See `data-model.md` for full breakdown).*
- `email`: `you@example.com`
- `mrBloomName`: `"Mr. Bloom"`
- `timezone`: `"Asia/Ho_Chi_Minh"`
- `focusDuration`: `25` (number)
- `breakDuration`: `5` (number)
- `startAtLogin`: `true`
- `keepWidgetOnTop`: `true`
- `reminderTime`: `"20:00"`
- `emailReminders`: `true`

## 8. Form-state Architecture

`SettingsState.svelte.ts` will manage:
- `savedSettings` (Source of truth)
- `draftSettings` (Bound to inputs)
- `$derived(isDirty)` (Checks equality of draft vs saved)
- `validationErrors` (Record of field names to strings)
- `isSaving` (Boolean)

Editing fields modifies `draftSettings`. Cancel restores `savedSettings` into `draftSettings`. Save validates `draftSettings`, and if valid, overwrites `savedSettings`.

## 9. Settings Control Behavior

- **Mr. Bloom's name**: Trims on blur. Emits error if empty/whitespace or >50 chars.
- **Timezone**: Populated from `Intl.supportedValuesOf('timeZone')`.
- **Focus/Break duration**: Choices: 5, 10, 15, 20, 25, 30, 45, 60 minutes.
- **Reminder time**: HTML `<input type="time">` or custom select matching "HH:mm".
- **Toggles**: Custom styling visually matching the green toggle in the reference, using hidden checkbox for semantics and keyboard focus.

## 10. Save and Cancel Behavior

- **Save Changes**: Validates draft. Mocks persistence since no global settings store exists. Tries to apply Tauri preferences (Catching errors if in browser). Clears `isDirty`. Sets accessible success message.
- **Cancel**: Overwrites `draft` with `saved`. Clears validation errors. No routing occurs.

## 11. Logout Behavior

- Since no global Auth store session exists, a mocked implementation will be created. The "LOGOUT" button will trigger `goto('/auth')` as the local fallback behavior.

## 12. Tauri Platform Behavior

- **Start Blooming at login**: `tauri-plugin-autostart` is missing. Will store locally and skip API call to prevent crashes.
- **Keep widget on top**: Will use `Window.getByLabel('companion-widget').setAlwaysOnTop(isTop)` inside a try-catch to handle the browser fallback or if the widget is closed.

## 13. Layout Strategy

- Reference native viewport: **1540x975**.
- Outer Page Grid: Same as `today` screen (100vw/100vh with min boundaries).
- Inner Window Layout: Same as `today-window` (border, box-shadow, cream background).
- Two columns for Settings:
  - Left column: General Panel.
  - Right column: Focus Timer (top), Notifications (bottom).
- Footer Actions: Bottom-right aligned inside the settings content container.

## 14. Styling Strategy

- Use `theme.css` tokens (e.g., `--bloom-primary-green`, `--bloom-text-dark-blue`).
- Recreate panel styles (thin grey borders, rounded corners) with CSS variables.
- Pixel fonts for headings (Cascadia Mono/Consolas from theme).

## 15. Accessibility Plan

- Semantics: Use `<form>`, `<label for="...">`, `<button type="button|submit">`.
- Toggles: Hidden `<input type="checkbox">` visually mapped to the custom toggle element.
- Focus: `outline: 2px solid var(--bloom-text-control-blue)` for focused inputs.
- Aria-live regions for Save success/errors.

## 16. Testing Strategy

- `SettingsState.test.ts`: Validate dirty state, form validation, and save/cancel logic.
- `Settings.test.ts` (Component test): Mount form, test input interactions, click Cancel, verify revert.
- Visual integration tests for Tauri API mocking (verifying `setAlwaysOnTop` is called).

## 17. Visual-verification Strategy

1. Run `npm run dev`. Navigate to `/settings`.
2. Resize browser viewport precisely to 1540x975.
3. Compare side-by-side with `design-assets/app/references/settings.png`.
4. Fix layout grid -> panel sizes -> typography -> colors.

## 18. Regression Strategy

- Run `npm run check` and `npm run test` to ensure `AppSidebar` modifications (adding `onClick` to Settings nav item) do not break the Today or Goals routes.

## 19. Implementation Sequence

1. Define `SettingsState.svelte.ts` (Data model).
2. Create basic `frontend/src/routes/settings/+page.svelte` shell reusing Sidebar and TitleBar.
3. Build atomic form controls (`TextInput`, `ToggleSwitch`, `SelectField`).
4. Assemble Panels (`GeneralPanel`, `FocusTimerPanel`, etc.).
5. Wire up Save, Cancel, and Logout behaviors.
6. Apply styling to match 1540x975 reference dimensions.
7. Integrate `tauri` window calls for "Keep widget on top".
8. Write unit tests for `SettingsState`.
9. Perform visual comparison check.

## 20. Risks and Mitigations

- **Missing Icons in AppIcon**: If a bell/clock icon isn't in `AppIcon`, we will implement it gracefully as CSS or SVG instead of a broken image.
- **Sidebar Regression**: Adding an `onClick` for settings to `AppSidebar` should not affect existing active state logic since the `activeRoute` prop already handles visual highlighting.
- **Tauri API Crashes**: Using `@tauri-apps/api/window` in the browser throws exceptions. All Tauri calls must be guarded or try/catched.
