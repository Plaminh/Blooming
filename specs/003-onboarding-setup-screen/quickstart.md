# Quickstart & Validation Guide

## Prerequisites
- Node.js environment
- Running the Vite dev server for the frontend (`npm run dev` in `frontend` directory)

## Development preview
`/onboarding-preview` is a development-only visual test route. It mounts `OnboardingSetupView` from `frontend/src/lib/features/onboarding-setup/components/pages/OnboardingSetupView.svelte`. Keep the route for visual checks; do not treat it as a production entry.

Current preview page (`frontend/src/routes/onboarding-preview/+page.svelte`):

```svelte
<script lang="ts">
  import OnboardingSetupView from '$lib/features/onboarding-setup/components/pages/OnboardingSetupView.svelte';
  import type { OnboardingSetupData } from '$lib/features/onboarding-setup/model/OnboardingSetupState.svelte';

  function handleFinish(data: OnboardingSetupData) {
    console.log('Finished with data:', data);
    alert('Finished! Check console for payload.');
  }

  function handleBack() {
    console.log('Back clicked');
    alert('Back clicked!');
  }
</script>

<OnboardingSetupView onFinish={handleFinish} onBack={handleBack} />
```

Shared theme tokens (`--bloom-*`) come from `frontend/src/lib/shared/styles/theme.css`, imported by the root layout.

## Validation Scenarios

### Scenario 1: Visual Verification
1. Open the preview route (`http://127.0.0.1:1420/onboarding-preview`).
2. Compare the screen directly against `design-assets/app/references/onboarding-setup.png`.
3. **Verify**: The layout must be a two-column desktop frame. The left panel must have the pixel-art illustration and quote. The right panel must have the correct typography, colors, and input controls.

### Scenario 2: Form Interaction
1. Type a new name into the "Mr. Bloom's name" input.
2. Open the timezone dropdown and select a different timezone.
3. Click the "50 / 10" preset button.
4. **Verify**: The helper text beneath the preset buttons updates to reflect the new preset (e.g., "Work for 50 minutes, take a 10-minute break."). The preset button is highlighted in green.
5. Toggle the two checkboxes.

### Scenario 3: Event Emission
1. After changing values, click "FINISH".
2. **Verify**: An alert appears and the browser console logs the full state payload matching your selections.
3. Click "BACK".
4. **Verify**: The back event is logged.
