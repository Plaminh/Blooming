# Implementation Plan: Garden Plant Selection

**Branch**: `[007-garden-plant-selection]` | **Date**: 2026-09-14 | **Spec**: [spec.md](./spec.md)

## Summary

Implement the Garden Plant Selection full-screen UI (`CHOOSE YOUR PLANT`) allowing users to browse their available plants in a carousel and unlock them with leaf currency. This is driven by local view-model state and SvelteKit/Tauri frontend infrastructure, avoiding speculative backend persistence.

---

### 1. Technical context

* **Framework and language versions**: SvelteKit `^2.65.1`, Svelte `^5.56.3`, TypeScript `~6.0.3`.
* **Tauri integration**: Tauri CLI and API `^2`.
* **Verified styling pipeline**: Global CSS (`app.html`, `global.css`, `theme.css`) with standard CSS classes and variables. PostCSS/Tailwind is not explicitly used for these components; custom CSS scopes and tokens are confirmed.
* **Asset-serving conventions**: Static assets from `static/assets/...` and `/assets/...` aliases.
* **Route and page ownership**: SvelteKit filesystem routing (`src/routes/...`).
* **Existing shared components**: 
  - `$lib/shared/components/organisms/AppSidebar.svelte` (Not used here)
  - `$lib/features/onboarding-setup/components/organisms/DesktopTitleBar.svelte` (Customized TitleBar found, needs safe reuse/move)
  - `$lib/shared/components/atoms/AppIcon.svelte` (For icon resolution)
  - `$lib/features/companion-widget/components/atoms/PlantSprite.svelte` (For sprite rendering)
* **Test and build tooling**: Vitest `^5.0.0`, Svelte Testing Library `^5.4.2`, `svelte-check`, `vite build`.

### 2. Constitution compliance

* **SvelteKit, TypeScript, and Tauri remain unchanged**: Yes, no new frameworks are introduced.
* **Atomic Design is followed**: Yes, the plan maps strictly to Atoms, Molecules, Organisms, and Page.
* **Shared theme and title bar are reused**: Yes, we will refactor/reuse `DesktopTitleBar`.
* **Backend scope is not expanded**: Yes, mocked local data is used.
* **No reference screenshot becomes a runtime dependency**: Yes, the PNG is only for measurement/inspection.
* **No Git branch, commit, or push operation is planned**: Confirmed, managed manually by user.

### 3. Route strategy

* **Which SvelteKit route file renders this screen**: `src/routes/garden-selection/+page.svelte` (creating a new route is appropriate because this is a distinct full-screen UI, separated from Today and Goals).
* **How users reach the route**: Likely from a button in the Today/Goals Garden preview (which we will wire to navigate to `/garden-selection`).
* **Whether the Garden preview in Today/Goals should link to it**: Yes, the smaller preview should link to this full-screen route.
* **Whether browser preview and Tauri use the same route**: Yes, SvelteKit routing serves both.
* **How the route behaves when Tauri APIs are unavailable**: The `DesktopTitleBar` graceful degradation (already implemented via `windowService`) will hide or disable desktop-specific controls in normal browsers.

### 4. Shared-versus-feature-specific ownership

| Component / Element | Ownership | Reuse / Refactor Plan |
| :--- | :--- | :--- |
| Desktop title bar | Shared (`$lib/shared/components/organisms/`) | Move from `onboarding-setup` to `shared` for global reuse. |
| Window controls | Shared | Already integrated into `DesktopTitleBar`. |
| Blooming logo | Shared | Reuse `/assets/icons/leaf-icon.png`. |
| Pixel typography | Shared | Reuse existing CSS variables from `global.css`. |
| Leaf icon | Shared | `$lib/shared/components/atoms/AppIcon.svelte` (with `sprout`). |
| Shared icon/sprite renderer | Shared | Refactor/reuse logic from `PlantSprite.svelte` to a shared util or generic renderer. |
| Buttons | Shared / Feature | Standardize green pixel buttons if not in `shared`, otherwise create feature specific. |
| Currency display | Feature | Specific to `garden-selection` (or `shared` if needed by others later). |
| Plant artwork renderer | Feature | Wrapper around `PlantSprite` scaled appropriately. |
| Garden preview panel | Shared / Other Feature | Kept entirely separate; no coupling to this full-screen layout. |
| Full-screen plant selection | Feature | Owned entirely by `$lib/features/garden-selection/`. |

### 5. Atomic Design component map

**Proposed Repository Paths**:

#### Atoms
* `$lib/shared/components/atoms/SpriteRenderer.svelte` (Shared pixel sprite renderer logic)
* `$lib/features/garden-selection/components/atoms/PlantArtwork.svelte`
* `$lib/features/garden-selection/components/atoms/CarouselArrow.svelte`
* `$lib/features/garden-selection/components/atoms/LockIcon.svelte` (or in `shared`)
* `$lib/features/garden-selection/components/atoms/UnlockButton.svelte`
* `$lib/features/garden-selection/components/atoms/PixelHeading.svelte`

#### Molecules
* `$lib/features/garden-selection/components/molecules/LeafBalance.svelte`
* `$lib/features/garden-selection/components/molecules/PlantIdentity.svelte` (Name + Description)
* `$lib/features/garden-selection/components/molecules/UnlockCost.svelte`
* `$lib/features/garden-selection/components/molecules/CarouselControls.svelte`

#### Organisms
* `$lib/shared/components/organisms/DesktopTitleBar.svelte` (Refactored location)
* `$lib/features/garden-selection/components/organisms/PlantPreviewArea.svelte`
* `$lib/features/garden-selection/components/organisms/UnlockPanel.svelte`
* `$lib/features/garden-selection/components/organisms/GardenSelectionContent.svelte`

#### Page/template
* `src/routes/garden-selection/+page.svelte` (Owns selected-plant index, currency, and local unlock state).

### 6. Asset inventory

| Visual Element | Repository Path | Dimensions | Type | Display Target | Notes / Blockers |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Blooming leaf logo | `/assets/icons/leaf-icon.png` | - | Image | 40x40 | Shared, existing. |
| Currency leaf icon | `/assets/icons/leaf-icon.png` | - | Image | ~24x24 | Shared, existing. |
| Monstera artwork | `/assets/plants/monstera-spritesheet.png` | 2304x896 | Sprite | Scaled up | Needs custom `displayHeight` scale via SpriteRenderer. |
| Plant shadow | (To be extracted or generated via CSS) | - | CSS/Image | - | Investigate if baked into sprite. |
| **Lock icon** | **MISSING** | - | - | - | **BLOCKER**: Explicit pixel art lock asset needed. |
| **Previous arrow** | **MISSING** | - | - | - | **BLOCKER**: Explicit pixel art arrow needed. |
| **Next arrow** | **MISSING** | - | - | - | **BLOCKER**: Explicit pixel art arrow needed. |
| Window-control icons| SVGs in `DesktopTitleBar.svelte` | 18x18 | SVG | 29x28 | Existing. |

*(Note: Missing assets are logged as blockers. Do not invent filenames or crop from garden.png).*

### 7. Typed data model

```typescript
// $lib/features/garden-selection/types/index.ts
export type PlantId = 'monstera' | 'sunflower' | 'bonsai' | 'jasmine' | 'lavender';

export interface PlantPresentation {
  id: PlantId;
  name: string;
  description: string[]; // Two lines of description
  species: PlantId;      // Maps to existing PlantSpecies
  unlockCost: number;
}

export interface UserSessionState {
  leafBalance: number;
  unlockedPlants: Set<PlantId>;
}

export interface GardenSelectionState {
  plants: PlantPresentation[];
  currentIndex: number;
  session: UserSessionState;
}
```
*Note: We store data models in `$lib/features/garden-selection/model/` with typed fixtures.*

### 8. State and behavior design

* **Initial State**: `currentIndex = 0` (Monstera), `leafBalance = 124`, Monstera cost = `120`.
* **Carousel Navigation**: Clicking Left/Right increments/decrements `currentIndex`. If at bounds, disable buttons or wrap (we will disable boundary buttons to match typical desktop app conventions).
* **Syncing**: All view data (artwork, text, unlock state) is reactive derived from `plants[currentIndex]`.
* **Unlock Flow**: 
  1. Click UNLOCK.
  2. If `leafBalance < cost`, do nothing (button disabled).
  3. If `leafBalance >= cost`, deduct `cost` from `leafBalance`.
  4. Add `plant.id` to `session.unlockedPlants`.
* **Repeat charges / Double click**: Prevented because the button disappears/disables immediately upon state change (plant becomes unlocked).
* **Already-unlocked**: Show "Selected" or "Unlocked" text without the unlock cost row, disabling the primary button.

### 9. Layout strategy

* **Verified Dimensions**: Native ~1271x1062 (per reference image). We will define the outer window wrapper `max-width: 1271px; max-height: 1062px; width: 100%; height: 100%`.
* **Title Bar Height**: Typically ~42px (matching Today screen).
* **Scaling**: Use CSS Flexbox/Grid to center the `GardenSelectionContent`. The plant artwork will preserve its aspect ratio with `image-rendering: pixelated`.
* **Vertical Spacing**: Ensure generous whitespace around the plant artwork, with absolute or flex positioning for the top-right currency panel.
* **Tauri Window Size**: We will NOT change the global default Tauri size. The screen will gracefully fill the available window, preserving centered composition and aspect ratios.

### 10. Styling strategy

* **Background**: Cream background `#fbfaf5` (or check variables).
* **Frame**: Cyan border `#29b9ce` / `#0b516b`.
* **Title Bar**: Turquoise gradient `#2796ad` to `#278aa1`.
* **Fonts**: Map to `--bloom-display-font` and `--bloom-body-font`.
* **CSS Framework**: Standard scoped `<style>` blocks in Svelte components. No arbitrary Tailwind classes.
* **Pixel Art**: Ensure `image-rendering: pixelated` is applied to all sprite images.

### 11. Accessibility

* **Semantic buttons**: `<button>` for all interactables.
* **Aria labels**: `aria-label="Previous plant"`, `aria-label="Next plant"`.
* **Live region**: `aria-live="polite"` on the plant name/description to announce changes on navigation.
* **Disabled states**: `aria-disabled="true"` and `disabled` attribute for insufficient funds.
* **Keyboard Focus**: `:focus-visible` outlines matching the theme. Standard `tabindex` flows from Titlebar -> Currency -> Carousel (Left) -> Plant -> Carousel (Right) -> Unlock Action.

### 12. Testing strategy

* **Vitest**: Unit tests for the local store/view-model (testing exact deductions, preventing double charges, bounds checking).
* **Svelte Testing Library**: Render tests for `GardenSelectionContent.svelte` verifying correct initial state (124 leaves, Monstera selected) and disabled states for insufficient currency.
* **Regression Checks**: Run `npm run test` and `npm run check`. Verify `today` route still renders perfectly after moving `DesktopTitleBar`.

### 13. Visual-verification strategy

1. Start `npm run dev`.
2. Navigate to `http://localhost:5173/garden-selection`.
3. Overlay or side-by-side compare with `removed reference artwork` at `1271x1062` viewport size.
4. Tune outer layout, then plant scaling, then typography, and finally borders/shadows.
5. Do not install Playwright/Puppeteer permanently; rely on manual visual inspection loops.

### 14. Implementation sequence

1. **Phase 1**: Verify `DesktopTitleBar` safe refactor to `$lib/shared/components/organisms`. Validate `today` route.
2. **Phase 2**: Define typed local fixtures (`gardenFixtures.ts`) and view-model (`GardenSelectionState.svelte.ts`).
3. **Phase 3**: Create `SpriteRenderer` supporting arbitrary scales.
4. **Phase 4**: Build Atoms and Molecules (`LeafBalance`, `PlantIdentity`, `UnlockCost`, `CarouselControls`). **[BLOCKED on missing assets]**
5. **Phase 5**: Build Organisms (`PlantPreviewArea`, `UnlockPanel`).
6. **Phase 6**: Assemble `/garden-selection/+page.svelte`.
7. **Phase 7**: Add keyboard accessibility, focus trapping.
8. **Phase 8**: Write Vitest logic tests and Svelte render tests.
9. **Phase 9**: Visual iteration against reference PNG.
10. **Phase 10**: Final check, lint, and Tauri build validation.

### 15. Risks and mitigations

* **Missing Assets**: Lock, left arrow, right arrow are missing. Mitigation: Reported as explicit blockers. Wait for assets before proceeding with UI integration.
* **Sprite scaling**: Native `PlantSprite.svelte` is hardcoded to `148px` display height. Mitigation: Refactor it or create a configurable wrapper.
* **Shared TitleBar Regression**: Moving `DesktopTitleBar` might break `today` or `onboarding`. Mitigation: Strict type checks and localized testing on those routes before proceeding.
* **Double deduction**: Add strict state transition checks in the mock store.

---
