# Data Model: Settings Screen

## Settings Profile
The core data entity representing a user's preferences.

### Fields
- `email`: string (e.g. `"you@example.com"`) - Currently a fixture as auth state lacks a global session.
- `mrBloomName`: string (e.g. `"Mr. Bloom"`)
- `timezone`: string (e.g. `"Asia/Ho_Chi_Minh"`) - IANA identifier.
- `focusDuration`: number (e.g. `25`) - in minutes.
- `breakDuration`: number (e.g. `5`) - in minutes.
- `startAtLogin`: boolean (e.g. `true`)
- `keepWidgetOnTop`: boolean (e.g. `true`)
- `reminderTime`: string (e.g. `"20:00"`) - 24-hour time string format.
- `emailReminders`: boolean (e.g. `true`)

### Validation Rules
- `mrBloomName`: Must not be empty, must not be whitespace-only, max length 50 characters.
- `timezone`: Must be a valid IANA timezone string (validated against `Intl.supportedValuesOf('timeZone')`).
- `focusDuration`: Must be a number > 0.
- `breakDuration`: Must be a number > 0.
- `reminderTime`: Must match `^([01]\d|2[0-3]):([0-5]\d)$`.

## Form State Model
Used specifically for the Settings screen UI.

### Fields
- `draftSettings`: Settings Profile (Currently edited values)
- `savedSettings`: Settings Profile (Last successfully persisted values)
- `isDirty`: boolean (Derived: true if draft differs from saved)
- `isSaving`: boolean (True while save operation is pending)
- `validationErrors`: Record<keyof Settings Profile, string> (Key-value map of field errors)

### State Transitions
1. **Initial Load**: `savedSettings` initialized with defaults/fixtures. `draftSettings` = `savedSettings`.
2. **Edit**: Modify `draftSettings[field]`. `isDirty` updates automatically via derivation.
3. **Cancel**: `draftSettings` = `savedSettings`. Clear `validationErrors`.
4. **Save (Success)**: Validate `draftSettings`. `savedSettings` = `draftSettings`. `isDirty` becomes false.
5. **Save (Failure)**: `validationErrors` populated. `draftSettings` remains unchanged.
