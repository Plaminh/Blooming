# Data Model

## Entities

### OnboardingSetupState

Represents the local form state for the onboarding setup screen.

#### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `string` | `"Mr. Bloom"` | The user's chosen name. |
| `timezone` | `string` | `"Asia/Ho_Chi_Minh"` | The user's timezone selection. |
| `focusPreset` | `FocusPreset` | `"25 / 5"` | The selected focus session preset. |
| `startAtLogin` | `boolean` | `true` | Whether the app should start at login. |
| `keepWidgetOnTop` | `boolean` | `true` | Whether the widget stays above other windows. |

#### Enums

**FocusPreset**
- `"25 / 5"` (25 minutes focus, 5 minutes break)
- `"50 / 10"` (50 minutes focus, 10 minutes break)
- `"CUSTOM"` (Custom duration, for this screen just updates description)

#### Validation Rules
- **Name**: Must be gracefully handled if empty. The UI defaults to reasonable bounds (e.g. falling back to "Friend" or keeping the input but showing a warning, though the spec says "handled gracefully by UI state, defaulting to reasonable bounds"). We'll allow empty string but perhaps validate on Finish.
- **Timezone**: Must be a valid IANA timezone string from a pre-defined list.
- **FocusPreset**: Must be exactly one of the three options.

#### State Transitions
- **UpdateName**: Updates `name` field.
- **UpdateTimezone**: Updates `timezone` field.
- **SelectPreset**: Updates `focusPreset`.
- **ToggleStartAtLogin**: Toggles `startAtLogin` boolean.
- **ToggleKeepWidgetOnTop**: Toggles `keepWidgetOnTop` boolean.

`OnboardingSetupView` (under `components/pages/`) reads `state.data` and emits `onFinish` / `onBack`. Optional `windowService?: DesktopWindowService` is a view prop for title-bar controls, not part of this form model.
