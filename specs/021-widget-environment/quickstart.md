# Quickstart Validation

## Feature Verification

This feature implements the Widget Environment Rendering System including asset migration, time-of-day logic, seasonal logic, and procedural rain.

1. **Verify Asset Locations**
   Run the following commands to confirm that assets are placed in the correct directories and old directories are removed.
   ```bash
   # Check new directories
   ls frontend/src/lib/assets/widget/environment/daytime/
   ls frontend/src/lib/assets/widget/environment/season/
   ls frontend/src/lib/assets/widget/environment/weather/

   # Ensure old directories are gone
   ls -d daytime season weather # Should return no matches
   ```

2. **Verify Frontend Build & Types**
   Run standard checks to catch any broken static imports.
   ```bash
   cd frontend
   npm run check
   npm run build
   ```

3. **Verify Frontend Tests**
   Run unit and DOM tests to verify weather fallback and rain density.
   ```bash
   cd frontend
   npm run test
   ```

4. **Verify Runtime Assets (Widget Scene)**
   - Apply backend migrations with `cd backend && alembic upgrade head` before starting the API.
   - Run backend unit tests with `cd backend && python -m pytest tests/unit -q`.
   - Start the Vite dev server (`npm run dev`).
   - Launch the SvelteKit application and open the widget view.
   - Verify that there are no 404 errors in the browser console/network tab for environment images.
   - Ensure the layers (sky, bushes, weather overlays) compose visually without errors.
   - Note: Enable weather and save a city in onboarding or Settings; the widget then fetches the current condition from the authenticated backend route. Unavailable weather falls back to CLEAR.
