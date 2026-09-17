# Quickstart Validation Guide

## Prerequisites
- Backend running at `http://localhost:8000`
- Frontend running at `http://localhost:5173`
- A user account with some populated DailyPlans, Tasks, and completed FocusRuns.

## Validation Scenarios

1. **Verify Summary Metrics**
   - Navigate to the Statistics screen.
   - Change the period (e.g., Current Week).
   - Ensure the total focus time and distinct study days accurately match the focus runs that are marked 'ENDED'.
   - Verify plans marked 'COMPLETED' add to completed count, and 'CONFIRMED'/'ACTIVE' add to unfinished count.

2. **Verify Daily Chart**
   - Review the bar chart and heatmap.
   - Verify the dates with no focus runs show 0 hours, keeping the chart continuous.

3. **Verify Plan History Pagination & Filtering**
   - Scroll down to the Plan History Panel.
   - Change the filter to "Completed". Only completed plans should appear.
   - Change the filter to "Unfinished". Only active/confirmed plans should appear.
   - Ensure pagination buttons correctly retrieve the next page (page 2) and that items are consistent without duplication.
