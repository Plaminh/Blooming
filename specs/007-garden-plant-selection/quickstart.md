# Quickstart Validation Guide

**Feature**: Garden Plant Selection

## Prerequisites
* Node.js and npm installed.
* Ensure you have provided the missing assets (`lock`, `left-arrow`, `right-arrow`) in `static/assets/icons/` or similar before proceeding with visual verification.

## 1. Start the Development Server
```bash
npm run dev
```

## 2. Navigate to the Route
Open your browser or Tauri window and navigate to:
`http://localhost:5173/garden-selection`

## 3. Visual Verification Scenarios
* **Scenario A (Initial State)**: Verify the screen matches the layout of `removed reference artwork`. The Monstera plant should be visible, leaf balance at 124, and the UNLOCK button costs 120.
* **Scenario B (Navigation)**: Click the Right/Left carousel arrows. The artwork, name, description, and unlock states should change seamlessly without layout shifts.
* **Scenario C (Unlocking)**: While viewing the Monstera, click UNLOCK. The leaf balance should immediately drop from 124 to 4. The UNLOCK button should disappear or switch to a 'Selected' state.
* **Scenario D (Insufficient Funds)**: Navigate to another locked plant (if it costs > 4 leaves) and verify the UNLOCK button is disabled or visually indicates insufficiency.

## 4. Run Automated Tests
```bash
npm run test
npm run check
```
Expect all tests to pass, including regression tests for the `today` route to verify the `DesktopTitleBar` refactor.
