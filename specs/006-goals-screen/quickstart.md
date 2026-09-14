# Quickstart: Validation Guide for Goals Screen

## Prerequisites
- Node.js environment
- Access to the Blooming repository with SvelteKit installed

## Validation Scenarios

### Scenario 1: Verify Visual Layout
1. Start the dev server: `npm run dev`
2. Navigate to `http://localhost:5173/goals` (or appropriate port)
3. Set browser viewport size to approximately 1440x900.
4. Verify the UI renders the three content columns properly without overflow.
5. Verify the Garden panel is flush with the bottom.

### Scenario 2: Verify Goal Selection
1. Click on "Read 12 books" in the My Goals list.
2. Verify the Goal Details header updates to "Read 12 books".
3. Verify the Roadmap updates.
4. Click back to "Complete Blooming MVP" and ensure the progress updates correctly to "50%".

### Scenario 3: Verify Actions Fallback
1. Click "CREATE GOAL WITH MR. BLOOM".
2. A placeholder accessible dialog with "Coming Soon" should appear.
3. Close the dialog.
