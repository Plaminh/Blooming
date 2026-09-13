# UI Component Contracts

## `OnboardingSetupView.svelte`

Canonical file: `frontend/src/lib/features/onboarding-setup/components/pages/OnboardingSetupView.svelte`.

This is the main entry point for the onboarding setup screen. It is completely isolated from the backend and emits events to its parent. Title-bar window actions go through `DesktopWindowService` from `$lib/platform/desktopWindow`.

### Props

```typescript
import type { DesktopWindowService } from '$lib/platform/desktopWindow';

type FocusPreset = '25 / 5' | '50 / 10' | 'CUSTOM';

interface OnboardingSetupData {
  name: string;
  timezone: string;
  focusPreset: FocusPreset;
  startAtLogin: boolean;
  keepWidgetOnTop: boolean;
}

interface Props {
  /** Optional initial data to populate the form */
  initialData?: Partial<OnboardingSetupData>;

  /** Callback fired when the user clicks FINISH */
  onFinish?: (data: OnboardingSetupData) => void;

  /** Callback fired when the user clicks BACK */
  onBack?: () => void;

  /** Optional desktop window adapter for title-bar controls. Defaults to `desktopWindowService`. */
  windowService?: DesktopWindowService;
}
```
