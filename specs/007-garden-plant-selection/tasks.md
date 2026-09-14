# Tasks: Garden Plant Selection

**Input**: Design documents from `/specs/007-garden-plant-selection/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

## Phase 1 — Preflight and foundation

- [x] T001 Read the active Garden specification, plan, constitution, and `design-assets/references/garden.png`.
- [x] T002 Confirm the exact native pixel dimensions and aspect ratio of `design-assets/references/garden.png`.
- [x] T003 Confirm the real SvelteKit Garden route (`src/routes/garden-selection/+page.svelte`) through filesystem routing and existing navigation.
- [x] T004 Verify the existing CSS pipeline, global theme tokens, resets, and pixel-font loading at runtime in `src/app.html` and `src/lib/shared/styles/global.css`.
- [x] T005 Inspect the shared Tauri title bar, draggable region, and window-control implementation in `src/lib/features/onboarding-setup/components/organisms/DesktopTitleBar.svelte`.
- [x] T006 Inspect the existing Garden preview components used by Today and Goals in `src/lib/shared/components/organisms/GardenPanel.svelte`.
- [x] T007 Record current `git status` and identify unrelated user changes that must be preserved.

## Phase 2 — Asset inventory and validation

- [x] T008 [P] Inspect and record Blooming leaf logo asset (`static/assets/widget/icons/leaf-icon.png`).
- [x] T009 [P] Inspect and record Currency leaf icon asset (`static/assets/widget/icons/leaf-icon.png`).
- [x] T010 [P] Inspect and record Monstera plant artwork asset (`static/assets/widget/plants/monstera-spritesheet.png`).
- [x] T011 [P] Inspect and record Plant shadow asset, if separate (or confirm CSS usage).
- [x] T012 [P] Implement Lock icon as a code-native pixel-icon SVG in `src/lib/features/garden-selection/components/atoms/LockIcon.svelte`.
- [x] T013 [P] Implement CarouselArrowIcon as a code-native pixel-icon SVG in `src/lib/features/garden-selection/components/atoms/CarouselArrowIcon.svelte` handling previous and next directions.
- [x] T014 [P] (Merged with T013).
- [x] T015 [P] Inspect and record Minimize, Maximize/restore, and Close icons (SVGs in `DesktopTitleBar.svelte`).
- [x] T016 [P] Inspect and record Button textures, borders, or other decorative assets if present.
- [x] T017 [P] Inspect and record any additional plant assets required for the carousel fixtures.

*Asset inspection tasks explicitly forbid importing the reference PNG, cropping from the reference, inventing filenames, using emojis, Unicode symbols, blank boxes, or unrelated placeholders, or rendering full sprite sheets normally.*

## Phase 3 — Shared primitives and safe reuse

- [x] T018 Reuse the existing shared Blooming desktop title bar by moving it to `src/lib/shared/components/organisms/DesktopTitleBar.svelte`.
- [x] T019 Reuse Tauri window controls and title-bar dragging behavior inside `DesktopTitleBar`.
- [x] T020 Reuse or safely generalize the existing shared pixel icon/sprite renderer (`src/lib/shared/components/atoms/SpriteRenderer.svelte`).
- [x] T021 Reuse the existing theme tokens and pixel fonts from global CSS.
- [x] T022 Reuse low-level plant or currency primitives only when they are not coupled to Today, Goals, or widget-specific state.
- [x] T023 Keep the small Garden preview panel separate from the full Garden Plant Selection screen.
- [x] T024 Add regression checks for Today, Goals, onboarding, widget, and the existing Garden preview when shared code changes.

## Phase 4 — Typed plant view model

- [x] T025 Define typed frontend models for Plant identifier, display name, description lines, artwork reference, optional sprite-frame metadata, unlock price, locked/unlocked state, selected state, leaf balance, carousel index, and carousel boundary behavior in `src/lib/features/garden-selection/types/index.ts`.
- [x] T026 Implement typed local fixtures displaying Monstera, balance 124, unlock cost 120, locked state, and correct heading/subtitle/description in `src/lib/features/garden-selection/model/fixtures.ts`.
- [x] T027 Establish explicit icon/asset identifier unions (forbidding `string as any` and implicit paths).

## Phase 5 — User Story 1: View the plant-selection screen (MVP)

- [x] T028 [US1] Create the Garden route page/template at `src/routes/garden-selection/+page.svelte`.
- [x] T029 [US1] Implement the full-screen cream background and cyan outer frame in `src/routes/garden-selection/+page.svelte`.
- [x] T030 [US1] Integrate the shared desktop title bar into `src/routes/garden-selection/+page.svelte`.
- [x] T031 [US1] Implement top-right leaf balance panel in `src/lib/features/garden-selection/components/molecules/LeafBalance.svelte`.
- [x] T032 [US1] Implement large `CHOOSE YOUR PLANT` heading in `src/lib/features/garden-selection/components/atoms/PixelHeading.svelte`.
- [x] T033 [US1] Implement subtitle below heading in `src/routes/garden-selection/+page.svelte`.
- [x] T034 [US1] Implement centered Monstera artwork and shadow in `src/lib/features/garden-selection/components/organisms/PlantPreviewArea.svelte`.
- [x] T035 [US1] Implement plant name and description in `src/lib/features/garden-selection/components/molecules/PlantIdentity.svelte`.
- [x] T036 [US1] Implement previous and next controls in `src/lib/features/garden-selection/components/molecules/CarouselControls.svelte`.
- [x] T037 [US1] Implement unlock button in `src/lib/features/garden-selection/components/atoms/UnlockButton.svelte`.
- [x] T038 [US1] Implement lock and cost row in `src/lib/features/garden-selection/components/molecules/UnlockCost.svelte`.
- [x] T039 [US1] Ensure native-reference viewport geometry is maintained with no accidental scrolling, clipping, or overflow.

## Phase 6 — User Story 2: Navigate the plant carousel

- [x] T040 [US2] Implement Previous-plant navigation logic in `src/lib/features/garden-selection/model/state.svelte.ts`.
- [x] T041 [US2] Implement Next-plant navigation logic in `src/lib/features/garden-selection/model/state.svelte.ts`.
- [x] T042 [US2] Update artwork, name, description, price, and state synchronously on navigation.
- [x] T043 [US2] Implement boundary wrapping or disabled-boundary behavior according to approved plan conventions.
- [x] T044 [US2] Handle edge cases: Empty plant collection, Single-plant collection, Missing selected plant, Rapid navigation.
- [x] T045 [US2] Ensure navigation does not mutate currency or unlock state.
- [x] T046 [US2] Implement keyboard activation and accessible labels.
- [x] T047 [US2] Implement current-plant announcement if required by the accessibility plan.

## Phase 7 — User Story 3: Unlock a plant

- [x] T048 [US3] Implement enabling Unlock when the plant is locked and balance is sufficient in `src/lib/features/garden-selection/model/state.svelte.ts`.
- [x] T049 [US3] Implement disabling or preventing Unlock when the balance is insufficient.
- [x] T050 [US3] Support the exact-balance case (cost equals balance).
- [x] T051 [US3] Deduct `120` from `124` exactly once in local view-model state.
- [x] T052 [US3] Update the selected plant to unlocked.
- [x] T053 [US3] Prevent repeated charges or rapid multi-click deductions.
- [x] T054 [US3] Handle an already-unlocked plant and apply the approved post-unlock button state.
- [x] T055 [US3] Preserve unlock state when navigating between local fixture plants.
- [x] T056 [US3] Ensure keyboard activation and visible focus on the unlock button.
- [x] T057 [US3] Implement accessible status feedback upon successful unlock.

## Phase 8 — Pixel-accurate styling

- [x] T058 Match native viewport and outer frame geometry in `src/routes/garden-selection/+page.svelte`.
- [x] T059 Match Title-bar dimensions.
- [x] T060 Match Currency-panel position and dimensions in `LeafBalance.svelte`.
- [x] T061 Match Main heading and subtitle geometry in `PixelHeading.svelte`.
- [x] T062 Match Monstera artwork scale and position in `PlantPreviewArea.svelte`.
- [x] T063 Match Plant name and description placement in `PlantIdentity.svelte`.
- [x] T064 Match Carousel control positions and sizes in `CarouselControls.svelte`.
- [x] T065 Match Unlock button size and placement in `UnlockButton.svelte`.
- [x] T066 Match Lock/cost row alignment in `UnlockCost.svelte`.
- [x] T067 Match Pixel-font sizes, weights, and line heights across all text elements.
- [x] T068 Match Backgrounds, colors, borders, inset effects, and shadows to the reference.
- [x] T069 Ensure crisp pixel-art rendering using `image-rendering: pixelated`.

## Phase 9 — Accessibility and environment behavior

- [x] T070 Implement semantic buttons for all interactive elements.
- [x] T071 Ensure visible keyboard focus states.
- [x] T072 Implement accessible previous/next names.
- [x] T073 Implement accessible leaf balance and unlock-price labels.
- [x] T074 Add disabled-state communication for insufficient funds.
- [x] T075 Handle decorative images properly (aria-hidden).
- [x] T076 Manage focus behavior following a successful unlock.
- [x] T077 Implement reduced-motion handling if carousel animation exists.
- [x] T078 Add Tauri window-control labels.
- [x] T079 Implement normal-browser fallback when Tauri APIs are unavailable.

## Phase 10 — Tests

- [x] T080 Write test for correct initial Monstera state, Leaf balance `124`, and Unlock cost `120` in `src/lib/features/garden-selection/model/state.test.ts`.
- [x] T081 Write test for Previous and next navigation syncing plant details.
- [x] T082 Write test for Insufficient currency and Exact-cost currency behavior.
- [x] T083 Write test for Successful unlock and single deduction (preventing repeated activation).
- [x] T084 Write test for Already-unlocked state, Empty collection, and Single-plant collection edge cases.
- [x] T085 Write test for Keyboard-only operation accessibility.
- [x] T086 Write test for Browser execution fallback without Tauri APIs.
- [x] T087 Write test for Asset integrity verification.
- [x] T088 Add regression test for shared title-bar and Today/Goals Garden preview.

## Phase 11 — Visual verification

- [x] T089 Start the existing development server and open the verified Garden route.
- [x] T090 Render at the exact native dimensions of `design-assets/references/garden.png`.
- [x] T091 Compare side-by-side or overlay/diff with the reference and record visible mismatches.
- [x] T092 Fix macro geometry first.
- [x] T093 Fix component dimensions and alignment second.
- [x] T094 Fix typography and assets third.
- [x] T095 Tune colors, borders, and shadows last.
- [x] T096 Repeat verification loops until the defined visual tolerance is met.
- [x] T097 Verify that every asset request succeeds and no broken placeholder appears.

## Phase 12 — Final validation and cleanup

- [x] T098 Run the existing formatter (`npm run format` or similar).
- [x] T099 Run Svelte/TypeScript checks (`npm run check`).
- [x] T100 Run linting (`npm run lint`).
- [x] T101 Run unit/component/integration tests (`npm run test`).
- [x] T102 Run the production build (`npm run build`).
- [x] T103 Run applicable Tauri validation.
- [x] T104 Verify normal-browser fallback manually.
- [x] T105 Recheck Today, Goals, onboarding, widget, shared title bar, and Garden preview functionality.
- [x] T106 Review `git diff` and `git status` to confirm only intended files changed.
- [x] T107 Remove debugging code, temporary files, screenshots, unused components, unused imports, and unused CSS.
- [x] T108 Update task checkboxes truthfully after each validation succeeds.

## Explicit negative checks

- [x] T109 Verify `design-assets/references/garden.png` is used only for inspection and comparison.
- [x] T110 Verify no runtime import points into `design-assets/references`.
- [x] T111 Verify no reference screenshot is used as an icon atlas, plant image, sprite sheet, or background.
- [x] T112 Verify no deeply nested unstable asset import was introduced.
- [x] T113 Verify no invented asset path exists.
- [x] T114 Verify no broken image, emoji, Unicode substitute, or blank placeholder is present.
- [x] T115 Verify no full sprite sheet is rendered accidentally.
- [x] T116 Verify no Today/Goals sidebar appears on the screen.
- [x] T117 Verify no duplicate shared title bar or theme was created.
- [x] T118 Verify no backend/API/database/persistence work was added.
- [x] T119 Verify no unrelated Garden mechanics were implemented.
- [x] T120 Verify no test or visual-verification task was marked complete without being run.
- [x] T121 Verify no Git branch, commit, or push operation was performed during implementation planning.
