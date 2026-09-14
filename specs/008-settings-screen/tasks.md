# Tasks: Settings Screen

**Input**: Design documents from `specs/008-settings-screen/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

## Phase 1: Preflight and repository verification

**Purpose**: Initialize context and verify repository constraints.

- [X] T001 Read the active Settings spec, plan, constitution, and `design-assets/app/references/settings.png`.
- [X] T002 Verify the reference image’s exact native pixel dimensions and aspect ratio via script.
- [X] T003 Confirm the real Settings route structure in `frontend/src/routes`.
- [X] T004 Confirm how the shared sidebar navigates to Settings in `frontend/src/lib/shared/components/organisms/AppSidebar.svelte`.
- [X] T005 Verify current SvelteKit, TypeScript, and Tauri versions in `frontend/package.json` and `frontend/src-tauri/Cargo.toml`.
- [X] T006 Verify runtime styling pipeline in `frontend/src/lib/shared/styles/global.css` and `theme.css`.
- [X] T007 Inspect the shared title bar in `frontend/src/lib/shared/components/organisms/DesktopTitleBar.svelte`.
- [X] T008 Inspect the shared sidebar in `frontend/src/lib/shared/components/organisms/AppSidebar.svelte`.
- [X] T009 Inspect existing auth state in `frontend/src/lib/features/authentication/model/AuthState.svelte.ts`.
- [X] T010 Verify Tauri autostart plugin absence in `frontend/src-tauri/Cargo.toml`.
- [X] T011 Identify the actual widget window label in `frontend/src-tauri/tauri.conf.json`.
- [X] T012 Record `git status` to preserve unrelated user changes.

## Phase 2: Asset inventory

**Purpose**: Validate every required visual asset before implementation.

- [X] T013 Inspect and validate Blooming logo in `frontend/static/assets/`.
- [X] T014 Inspect and validate Today navigation icon in `frontend/src/lib/shared/components/atoms/AppIcon.svelte`.
- [X] T015 Inspect and validate Goals navigation icon in `AppIcon.svelte`.
- [X] T016 Inspect and validate Mr. Bloom navigation icon in `AppIcon.svelte`.
- [X] T017 Inspect and validate Settings gear icon in `AppIcon.svelte`.
- [X] T018 Inspect and validate Sidebar plant artwork in `frontend/src/lib/features/companion-widget/components/atoms/PlantSprite.svelte`.
- [X] T019 Inspect and validate Leaf counter icon (`frontend/static/assets/widget/icons/leaf-icon.png`).
- [X] T020 Inspect and validate Water counter icon in `AppIcon.svelte`.
- [X] T021 Inspect and validate Account/user icon in `AppIcon.svelte`.
- [X] T022 Inspect and validate General gear icon in `AppIcon.svelte`.
- [X] T023 Inspect and validate Focus Timer clock icon in `AppIcon.svelte`.
- [X] T024 Inspect and validate Notification bell icon in `AppIcon.svelte`.
- [X] T025 Confirm accessible CSS or inline SVG approach for dropdown indicator and window-control icons in `DesktopTitleBar.svelte`.

## Phase 3: Shared shell and primitives

**Purpose**: Prepare and reuse existing components safely.

- [X] T026 Reuse shared Blooming desktop title bar in `frontend/src/routes/settings/+page.svelte`.
- [X] T027 Add `onClick={() => goto('/settings')}` to the Settings `SidebarNavigationItem` in `AppSidebar.svelte`.
- [X] T028 Pass `activeRoute="SETTINGS"` to `AppSidebar.svelte` in `frontend/src/routes/settings/+page.svelte`.
- [X] T029 Reuse shared sidebar plant and resource counters.
- [X] T030 Reuse shared pixel icon renderer (`AppIcon.svelte`).
- [X] T031 Define atomic UI components for settings (buttons, inputs) in `frontend/src/lib/features/settings/components/atoms/`.
- [X] T032 Add regression coverage for `AppSidebar.svelte` in `frontend/src/lib/shared/components/organisms/AppSidebar.test.ts` to ensure `onClick` doesn't break other routes.

## Phase 4: Typed settings model and fixture state

**Purpose**: Implement the reactive form state data model.

- [X] T033 [P] Create `SettingsProfile` type definition in `frontend/src/lib/features/settings/types.ts`.
- [X] T034 Create `SettingsState.svelte.ts` in `frontend/src/lib/features/settings/model/SettingsState.svelte.ts`.
- [X] T035 Define `savedSettings` with the required initial fixture values in `SettingsState.svelte.ts`.
- [X] T036 Implement `draftSettings` populated from `savedSettings` in `SettingsState.svelte.ts`.
- [X] T037 Implement derived `isDirty` state in `SettingsState.svelte.ts`.
- [X] T038 Implement validation state (`validationErrors`) and state transition methods (Cancel, Save) in `SettingsState.svelte.ts`.

## Phase 5: User Story 1: View the Settings screen

**Goal**: Navigate to and view the reference-derived desktop layout.

- [X] T039 [US1] Create the core layout structure in `frontend/src/routes/settings/+page.svelte`.
- [X] T040 [US1] Implement large `SETTINGS` heading in `frontend/src/lib/features/settings/components/atoms/SectionHeading.svelte`.
- [X] T041 [US1] Create `AccountPanel.svelte` placeholder in `frontend/src/lib/features/settings/components/organisms/AccountPanel.svelte`.
- [X] T042 [US1] Create `GeneralPanel.svelte` placeholder in `frontend/src/lib/features/settings/components/organisms/GeneralPanel.svelte`.
- [X] T043 [US1] Create `FocusTimerPanel.svelte` placeholder in `frontend/src/lib/features/settings/components/organisms/FocusTimerPanel.svelte`.
- [X] T044 [US1] Create `NotificationsPanel.svelte` placeholder in `frontend/src/lib/features/settings/components/organisms/NotificationsPanel.svelte`.
- [X] T045 [US1] Implement SettingsActionGroup (Cancel, Save Changes buttons) in `frontend/src/lib/features/settings/components/molecules/SettingsActionGroup.svelte`.
- [X] T046 [US1] Apply CSS grid to `frontend/src/routes/settings/+page.svelte` to match the two-column layout without accidental overflow.

## Phase 6: User Story 2: View account information and logout

**Goal**: Present user account identity and allow mock logout.

- [X] T047 [US2] Implement Account/user icon and `ACCOUNT` heading in `AccountPanel.svelte`.
- [X] T048 [US2] Implement `Signed in as` label and email display in `AccountPanel.svelte`.
- [X] T049 [US2] Create local mock logout handler inside `SettingsState.svelte.ts` (or page script) that navigates to `/auth`.
- [X] T050 [US2] Implement the `LOGOUT` action button and bind it to the logout handler with keyboard support in `AccountPanel.svelte`.

## Phase 7: User Story 3: Edit General settings

**Goal**: Allow editing Mr. Bloom's name and timezone with validation.

- [X] T051 [P] [US3] Create `TextInput.svelte` atom in `frontend/src/lib/features/settings/components/atoms/TextInput.svelte`.
- [X] T052 [P] [US3] Create `ToggleSwitch.svelte` atom in `frontend/src/lib/features/settings/components/atoms/ToggleSwitch.svelte`.
- [X] T053 [US3] Implement Mr. Bloom's name labeled text input in `GeneralPanel.svelte`.
- [X] T054 [US3] Add validation logic to `SettingsState.svelte.ts` for empty, whitespace, and long names.
- [X] T055 [US3] Implement Timezone select dropdown (populated by `Intl.supportedValuesOf`) in `GeneralPanel.svelte`.
- [X] T056 [US3] Implement Start Blooming at login toggle in `GeneralPanel.svelte`.
- [X] T057 [US3] Implement Keep widget on top toggle in `GeneralPanel.svelte`.
- [X] T058 [US3] Bind all General panel inputs to `draftSettings` ensuring isolated updates.

## Phase 8: User Story 4: Configure Focus Timer

**Goal**: Configure timer durations safely.

- [X] T059 [P] [US4] Create `SelectField.svelte` atom in `frontend/src/lib/features/settings/components/atoms/SelectField.svelte`.
- [X] T060 [US4] Implement Focus Timer clock icon and heading in `FocusTimerPanel.svelte`.
- [X] T061 [US4] Implement Focus-duration select (numeric values 5, 10, 15, 20, 25, 30, 45, 60) in `FocusTimerPanel.svelte`.
- [X] T062 [US4] Implement Break-duration select (numeric values 5, 10, 15, 20) in `FocusTimerPanel.svelte`.
- [X] T063 [US4] Add validation for zero or negative duration values to `SettingsState.svelte.ts`.
- [X] T064 [US4] Bind Focus Timer selects to `draftSettings` and verify keyboard operation.

## Phase 9: User Story 5: Configure Notifications

**Goal**: Edit notification preferences.

- [X] T065 [US5] Implement Notification bell icon and heading in `NotificationsPanel.svelte`.
- [X] T066 [US5] Implement Milestone reminder time input (HTML time type or custom select) in `NotificationsPanel.svelte`.
- [X] T067 [US5] Implement Email-reminders toggle in `NotificationsPanel.svelte`.
- [X] T068 [US5] Add time format validation to `SettingsState.svelte.ts`.
- [X] T069 [US5] Bind inputs to `draftSettings` and ensure accessible checked-state communication.

## Phase 10: User Story 6: Save and cancel changes

**Goal**: Finalize or revert draft state.

- [X] T070 [US6] Wire the Cancel action in `SettingsActionGroup.svelte` to `SettingsState.cancel()`.
- [X] T071 [US6] Ensure `SettingsState.cancel()` discards draft changes and restores `savedSettings` without navigating away.
- [X] T072 [US6] Implement `SettingsState.save()` to validate complete draft before proceeding.
- [X] T073 [US6] Prevent duplicate save execution via `isSaving` guard in `SettingsState.svelte.ts`.
- [X] T074 [US6] Implement typed local persistence fallback (e.g. updating in-memory mock or LocalStorage) in `SettingsState.save()`.
- [X] T075 [US6] Expose accessible save success or failure feedback in `SettingsActionGroup.svelte`.

## Phase 11: Tauri platform integrations

**Purpose**: Execute specific window behavior gracefully.

- [X] T076 Wire "Keep widget on top" toggle to `@tauri-apps/api/window` (`Window.getByLabel('companion-widget').setAlwaysOnTop(...)`) inside `SettingsState.save()`.
- [X] T077 Wrap Tauri API calls in a `try/catch` to gracefully degrade to local state fallback in browser environments.

## Phase 12: Pixel-accurate layout and styling

**Purpose**: Precisely match `design-assets/app/references/settings.png` (1540x975).

- [X] T078 Apply global CSS grid constraints to `frontend/src/routes/settings/+page.svelte` to match the outer frame.
- [X] T079 Adjust `AppSidebar` and Main content padding widths to match reference proportions.
- [X] T080 Align `SETTINGS` heading typography and offsets.
- [X] T081 Apply thin gray panel borders, rounded corners, and exact dimensions to all panels.
- [X] T082 Align forms to match the 2-column label/input ratios.
- [X] T083 Style toggle switches to visually match the green toggles from the reference.
- [X] T084 Apply final typography, text colors (`var(--bloom-text-dark-blue)`), and button background colors.

## Phase 13: Accessibility

**Purpose**: Ensure the interface is operable by all users.

- [X] T085 Verify all inputs and selects have associated labels or `aria-label` attributes.
- [X] T086 Ensure toggle switches use `<input type="checkbox">` and correctly map the `checked` attribute visually.
- [X] T087 Apply `outline: 2px solid var(--bloom-text-control-blue)` for visible focus indicators on all form controls.
- [X] T088 Check logical focus order (Header -> Account -> General -> Focus Timer -> Notifications -> Save/Cancel).
- [X] T089 Add `aria-live="polite"` region for Save feedback messages.

## Phase 14: Tests

**Purpose**: Validate functional behavior via test suite.

- [X] T090 [P] Create `SettingsState.test.ts` to test initial reference values and draft/saved state isolation.
- [X] T091 [P] Create component tests for `TextInput`, `SelectField`, and `ToggleSwitch` in `frontend/src/lib/features/settings/components/atoms/`.
- [X] T092 Test dirty-state calculation, cancel functionality, and successful mock save in `SettingsState.test.ts`.
- [X] T093 Test name validation, duration bounds validation, and time format validation in `SettingsState.test.ts`.

## Phase 15: Visual verification

**Purpose**: Compare final render directly against the reference artifact.

- [X] T094 Run `npm run dev` and navigate to `/settings`.
- [X] T095 Resize the browser precisely to `1540x975`.
- [X] T096 Compare the rendered application side-by-side with `design-assets/app/references/settings.png`.
- [X] T097 Adjust any visual mismatches in panel sizes, gaps, or typography iteratively until tolerance is satisfied.
- [X] T098 Verify no broken icons are present.

## Phase 16: Regression checks

**Purpose**: Ensure shared shell modifications did not harm existing screens.

- [X] T099 Run development server and verify the `Today` screen renders correctly with the sidebar.
- [X] T100 Verify the `Goals` screen renders correctly and navigates properly via the sidebar.

## Phase 17: Final validation and cleanup

**Purpose**: Clean up and finalize the PR.

- [X] T101 Run `npm run check` (Svelte/TS check).
- [X] T102 Run `npm run test` (Vitest suite).
- [X] T103 Run `npm run build` to verify production compilation.
- [X] T104 Review `git diff` and `git status` to ensure only intended settings files and minor Sidebar tweaks were modified.

## Explicit negative checks

**Purpose**: Checklist confirming strict prohibitions were followed.

- [X] T105 Confirm `design-assets/app/references/settings.png` is only used for comparison and is NOT imported into code.
- [X] T106 Confirm no screenshot is used as an icon atlas or background.
- [X] T107 Confirm no invented asset paths or unstable nested paths (`../../`) exist.
- [X] T108 Confirm no emoji, generic Unicode, blank squares, or broken images remain in the UI.
- [X] T109 Confirm no Settings-only duplicate of the shared title bar or sidebar exists.
- [X] T110 Confirm no CSS classes are stored in `SettingsState` or `draftSettings` model.
- [X] T111 Confirm no `as any` is used to bypass known setting types.
- [X] T112 Confirm no backend API or database connection logic was added.
- [X] T113 Confirm no new Tauri plugin was added to `Cargo.toml` without approval.
- [X] T114 Confirm `setAlwaysOnTop` is strictly applied only to the `companion-widget` window.
- [X] T115 Confirm no dead console-only button handlers exist (Logout maps to `/auth`).
- [X] T116 Confirm no test or visual task is checked without actual verification.
- [X] T117 Confirm no Git branch, commit, or push operations were performed automatically.

---

## Dependencies & Execution Order

- **Phase 1-2**: Blocking analysis and asset verification. Must be completed first.
- **Phase 3-4**: Shared shell preparation and typed model foundation.
- **Phase 5-10**: Core user story implementation (incremental, can be done sequentially).
- **Phase 11**: Tauri integration (depends on Phase 10 save behavior).
- **Phase 12-13**: Polish and accessibility pass.
- **Phase 14-17**: Final validation, testing, and cleanup.

## Implementation Strategy

**MVP First**: Complete Phase 1-5 (User Story 1 layout) and Phase 6 (Account info). Verify the skeleton visually matches the reference. Then iteratively implement each form control in US3, US4, US5 and link them all to the Save/Cancel logic in US6. Stop and perform visual verification (Phase 15) before finalizing Tauri capabilities and tests.
