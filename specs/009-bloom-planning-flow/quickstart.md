# Quickstart Validation Guide: Mr. Bloom Planning and Draft Review Flow

This document provides the exact commands and manual test steps to validate the feature.

## Prerequisites
- Node.js environment configured.
- Tauri CLI installed globally or locally via `npm`.
- Rust toolchain installed (for Tauri).

## Build and Setup
1. Open terminal at the `frontend/` directory (or root if using workspace scripts).
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run TypeScript checks:
   ```bash
   npm run check
   ```
4. Run automated tests:
   ```bash
   npm run test
   ```

## Running the Application
Launch the Tauri desktop application:
```bash
npm run tauri dev
```

## Validation Scenarios

### Scenario 1: Initial State and Empty Chat
1. Click **MR. BLOOM** in the sidebar.
2. Verify the layout matches `chat-overall.png` (Live Draft placeholder on the right).
3. Try to submit an empty message. Verify the input remains disabled or submission is prevented.

### Scenario 2: Roadmap Draft Review
1. Type a long-term goal request (e.g., "I want to complete the MVP by June 30").
2. Press **Enter**.
3. Verify the mock response appears and the right panel switches to the Roadmap Draft (`plan-draft.png`).
4. Modify a milestone.
5. Click **Discard**. Verify the draft clears and placeholder returns.

### Scenario 3: Today Draft Review
1. Type a daily planning request (e.g., "Plan my day. I have 6 hours.").
2. Click the **Send icon button**.
3. Verify the mock response appears and the right panel switches to the Today Draft (`today-draft.png`).
4. Change a task duration and priority.

### Scenario 4: Timeline Draft Review
1. From the Today Draft, click **GENERATE TIMELINE**.
2. Verify the right panel switches to the Timeline Draft (`timeline-draft.png`).
3. Click **BACK TO TASKS**. Verify it returns to the Today Draft without losing changes.
4. Click **GENERATE TIMELINE** again.
5. Click **SAVE TO TODAY**. Verify the draft clears and a success message appears in the chat.

## Visual Verification
For each scenario above, capture a screenshot of the Tauri window and place it side-by-side with the corresponding reference image in `removed reference artwork`. Confirm matching typography, spacing, border styles, and colors.
