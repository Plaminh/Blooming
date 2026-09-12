# Visual acceptance: Compact Desktop Companion Widget

**Purpose**: Record the results of manual visual and platform verification.
**Status**: Implemented — manual acceptance pending. Browser fixture review is recorded; live network inspection, reference comparison, and Tauri platform checks are still outstanding.

**Reference**: `design-assets/widget/references/widget-reference.svg`, under the source-only rules in [spec.md](../spec.md) VR-015.
**Reference metrics**: [plan.md](../plan.md) → *Reference metrics*. Implemented values live in `frontend/src/lib/features/companion-widget/model/layout.ts`.
**Procedure**: [quickstart.md](../quickstart.md).

Screenshots are QA evidence, not repository content: capture them to a scratch directory outside the repo, and keep any capture tool's browser profile in an OS temporary directory.

## Checklist

### Source-only exclusion

- [ ] Browser or Tauri network inspection shows no request for any `design-assets/` path
- [ ] The reference SVG on disk is byte-identical to intake (not re-exported)

### Canvas and aspect

- [ ] Widget default size is the spec canvas
- [ ] Screenshots preserve the reference aspect ratio
- [ ] 90–110% resize shows no scrollbar, clipping, or overlap
- [x] Supplied PNG leaf is aligned beside `BLOOMING`; no leaf-balance pill is visible

### Reminders versus the reference (required)

- [ ] Capture the reminders fixture at the spec canvas
- [ ] Compare it side by side with the reference SVG in an external viewer
- [ ] Proportions, placement, spacing, border thickness, corner radii, colors, panel shape and tail, title-bar layout, button sizes, type scale, and character position match
- [ ] Title bar, panel, text, buttons, bell, and window controls are live Svelte/HTML, not the SVG's embedded rasters
- [ ] Sky, bushes, and Mr. Bloom come from the runtime PNGs

### Four fixtures

- [x] Every permitted animation frame shows exactly one complete, undistorted Mr. Bloom and no neighboring fragment
- [x] Exactly one selected plant appears at the far-left edge behind Mr. Bloom in every state
- [x] Paused: all four clean sleeping frames in order, cyan sleep effects baked into frames 2–3, large clock, RESUME then END
- [x] Behind schedule: alert pose, separate orange marks, wide bubble, no clock, REPLAN then LATER then OPEN
- [x] Offline: happy pose, separate Wi-Fi and red `×`, compact bubble, large clock, no action buttons
- [x] Reminders: alert pose, separate pink marks, bell, `2 REMINDERS`, VIEW then DISMISS
- [x] No placeholders, emoji, or generic icon libraries in any state

### Platform

- [ ] Windows: minimize, maximize/restore, close, title-bar drag via `npm run tauri dev`
- [ ] Linux: same set of checks


## Results

| Item | Status | Notes |
|---|---|---|
| Reminders vs reference comparison | **Not performed** | No side-by-side comparison has been run against the SVG. |
| Four-fixture screenshots | **Passed in browser preview** | Captured outside the repository on Windows after atlas cleanup; every permitted frame was inspected, including all four Paused frames. |
| Network inspection | **Not performed** | Automated source and rendered-URL exclusion is covered by `assets.test.ts`; live network inspection is still outstanding. |
| Windows window controls | **Not performed** | `npm run tauri dev` has not been run for this verification. |
| Linux window controls | **Unverified** | No Linux host available in this environment. |

## Notes

- Automated checks that currently pass (`npm run check`, `npm run test`, `npm run build`) do not substitute for any item above.
- Record concrete gaps here when the comparison is performed, rather than marking items complete because the files exist.
