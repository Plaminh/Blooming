# Research Findings: Garden Plant Selection

## Missing Assets

**Decision**: The implementation of the Carousel Arrows and Lock Icon are currently BLOCKED.
**Rationale**: The specification explicitly forbids inventing filenames, using Unicode substitutions, or cropping the reference image. The repository inspection confirms that `lock`, `left-arrow`, and `right-arrow` pixel art assets do not currently exist in the frontend `static/assets/` directories. 
**Alternatives Considered**: Using SVG outlines from the Authentication feature was considered, but the spec mandates matching the reference image's visual fidelity, which uses pixel-art UI elements for these specific controls. We must wait for real assets.

## DesktopTitleBar Reusability

**Decision**: Relocate `$lib/features/onboarding-setup/components/organisms/DesktopTitleBar.svelte` to `$lib/shared/components/organisms/DesktopTitleBar.svelte`.
**Rationale**: The `today` and `onboarding-setup` routes already use this component. The Garden Plant Selection screen is a full-screen desktop UI that requires the exact same TitleBar. Moving it to `shared` correctly reflects its cross-feature ownership.
**Alternatives Considered**: Duplicating the component into the `garden-selection` feature was rejected as it violates the constitution's clear architectural boundaries and reuse principles.

## Plant Sprite Scaling

**Decision**: Modify or wrap the existing `PlantSprite.svelte` to accept dynamic `displayHeight` or generic scaling factors.
**Rationale**: The existing widget uses a hardcoded `148px` height for plants. The Garden Plant Selection screen features a much larger, centered plant preview. The sprite logic is identical, only the CSS `display-h` and `display-w` mapping needs to scale up.
