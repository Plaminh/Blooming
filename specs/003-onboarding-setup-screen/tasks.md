# Tasks: onboarding-setup-screen

**Input**: Design documents from `specs/003-onboarding-setup-screen/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are required where mandated by the Constitution or feature specification. Every user story still requires an independently verifiable acceptance method.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2])
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, inspection, and asset setup

- [x] T001 Inspect the reference image and measure the application window’s composition in `removed reference artwork`
- [x] T002 Inspect the existing frontend architecture, routes, component hierarchy, styling system, fonts, and assets in `frontend/src/`
- [x] T003 Identify reusable assets and components for the setup screen in `frontend/static/assets/` and `frontend/src/lib/`
- [x] T004 Add or update the required font configuration without breaking the project’s existing stack in `frontend/src/lib/shared/styles/theme.css`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T005 Create feature directory structure in `frontend/src/lib/features/onboarding-setup/`

---

## Phase 3: User Story 1 - Configure User Profile (Priority: P1) 🎯 MVP

**Goal**: As a new user, I want to set up my name, timezone, and preferred focus session preset so that the application is customized to my needs and correctly schedules reminders.

**Independent Test**: Can be tested independently by loading the components, modifying all controls, and verifying that local state updates correctly and events emit.

### Implementation for User Story 1

- [x] T006 [US1] Implement typed local interaction state (`OnboardingSetupState`) in `frontend/src/lib/features/onboarding-setup/model/OnboardingSetupState.svelte.ts`
- [x] T007 [P] [US1] Build or reuse Atomic Design atoms (Input, Select, Checkbox, Button) in `frontend/src/lib/features/onboarding-setup/components/atoms/`
- [x] T008 [US1] Add accessible labels, keyboard behavior, and focus states to atoms in `frontend/src/lib/features/onboarding-setup/components/atoms/`
- [x] T009 [US1] Build molecules (FormField, StepProgress, PresetSelector, QuoteCard) using the atoms in `frontend/src/lib/features/onboarding-setup/components/molecules/`

**Checkpoint**: At this point, User Story 1 atoms and molecules should be fully functional and testable.

---

## Phase 4: User Story 2 - UI Layout & Asset Verification (Priority: P2)

**Goal**: As a user, I want to see a polished, pixel-art themed onboarding screen that perfectly matches the reference design.

**Independent Test**: Can be tested visually by running the app and comparing the window layout against `removed reference artwork`.

### Implementation for User Story 2

- [x] T010 [P] [US2] Build organisms (`DesktopTitleBar`, `OnboardingBrandPanel`, `OnboardingSetupForm`) in `frontend/src/lib/features/onboarding-setup/components/organisms/`
- [x] T011 [US2] Compose the onboarding setup page (`OnboardingSetupView.svelte`) in `frontend/src/lib/features/onboarding-setup/components/pages/OnboardingSetupView.svelte`
- [x] T012 [US2] Integrate the screen with existing onboarding navigation boundaries without adding backend integration by creating the development-only visual test route `frontend/src/routes/onboarding-preview/+page.svelte`

**Checkpoint**: At this point, the entire page should render and update state locally.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and ensure visual fidelity

- [x] T013 Run formatting, type checking, linting, and relevant frontend tests in `frontend/`
- [x] T014 Render the screen at the reference viewport in `frontend/src/routes/onboarding-preview/+page.svelte` and capture a screenshot
- [x] T015 Compare the implementation directly against `removed reference artwork`
- [x] T016 Correct visual mismatches in `frontend/src/lib/shared/styles/theme.css` and onboarding components, and repeat verification until the result is closely aligned

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational
- **User Story 2 (P2)**: Depends on components built in US1

### Parallel Opportunities

- Inspecting assets and code (T001, T002, T003) can be done in parallel.
- Building independent atoms (T007) can be done in parallel.
- Building independent organisms (T010) can be done in parallel.

---

## Parallel Example: User Story 1

```bash
# Launch independent atom implementation in parallel:
Task: "Build or reuse Atomic Design atoms (Input) in frontend/src/lib/features/onboarding-setup/components/atoms/Input.svelte"
Task: "Build or reuse Atomic Design atoms (Select) in frontend/src/lib/features/onboarding-setup/components/atoms/Select.svelte"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify atoms and molecules render and behave correctly.

### Incremental Delivery

1. Add User Story 2 -> Build Organisms -> Compose Page -> Integrate Route
2. Add Polish -> Lint -> Screenshot -> Compare -> Correct Iteratively

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Avoid adding any backend logic or database schemas, as per constraints.
- Visual correctness against `onboarding-setup.png` is the highest priority for completion.
