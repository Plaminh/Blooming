# Widget art intake

Supplied companion-widget artwork. No ownership, attribution, or licensing information came with these files. Source files in this folder are the authoritative originals and must stay unchanged.

## Runtime assets

Served from `frontend/static/`, referenced only by `/assets/widget/...` URLs.

| File | Dimensions | Usage |
|---|---|---|
| `frontend/static/assets/widget/backgrounds/default-sky.png` | 1880 × 837 | Back layer: sky, clouds, city skyline |
| `frontend/static/assets/widget/backgrounds/background-bushes.png` | 1881 × 836 | Foreground layer: foliage, plants, ground |
| `frontend/static/assets/widget/characters/mr-bloom-spritesheet.png` | 1152 × 1152 | Normalized animated Mr. Bloom atlas, 4 × 8 grid of 288 × 144 cells |
| `frontend/static/assets/widget/icons/leaf-icon.png` | 128 × 128 | Title-bar logo; transparent source padding leaves an approximately 28px visible mark |
| `frontend/static/assets/widget/plants/*-spritesheet.png` | 2304 × 896 | Normalized 8 × 2 plant atlases, 288 × 448 cells |

The source Mr. Bloom artwork is an irregular `1536 × 1152` sheet with eight exact 144px rows. `tools/widget-assets/NormalizeWidgetAssets.cs` extracts its four left-to-right sprite clusters per row without rescaling, left-aligns every frame in a row to a shared slot (the widest frame), bottom-aligns it, and writes the normalized `1152 × 1152`, `4 × 8`, `288 × 144` runtime atlas listed above. The rendered character viewport is `220 × 110`. State rows and permitted columns are authoritative in `specs/001-companion-widget/data-model.md` (`paused` row 7 `[0, 1, 2, 3]`, `behindSchedule` row 6 `[0, 2]`, `offline` row 3 `[0, 1, 2, 3]`, `reminders` row 4 `[1]`). Paused uses the cyan sleep effects baked into those frames.

Plant sources are `1774 × 887` and not a uniform CSS grid. Runtime copies are normalized by `tools/widget-assets/NormalizeWidgetAssets.cs` into an integer `8 × 2` atlas. Frames `0–7` are the upper row, left to right; frames `8–15` are the lower row. Relative plant scale is preserved and pots are bottom-centered. Jasmine’s source filename `jasmine-spriresheet.png` is corrected only on the runtime copy.

The active plant is presentation data until application state owns it. Reward calculation and garden growth are out of scope. The widget has no leaf-balance presentation surface.

## Source-only asset

| File | Canvas | Usage |
|---|---|---|
| `design-assets/widget/references/widget-reference.svg` | 680 × 289 | Visual comparison target for the reminders state |

Restrictions: never import, request, serve, bundle, or copy it into `frontend/static/`; never render it as the widget; never edit, optimize, re-export, or overwrite it. See `specs/001-companion-widget/spec.md` (VR-015).
