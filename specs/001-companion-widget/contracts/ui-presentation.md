# Contract: Companion widget UI and window

This feature exposes **no HTTP API**. The contract is the Tauri window plus the TypeScript presentation model in [data-model.md](../data-model.md).

## Window

| Field | Value |
|---|---|
| Label | `companion-widget` |
| Creation | Static `app.windows` entry in `frontend/src-tauri/tauri.conf.json` |
| URL | `/widget` |
| Dev resolution | `http://localhost:1420/widget` |
| Production resolution | Prerendered `widget.html` via `@sveltejs/adapter-static`, SPA `index.html` fallback retained |
| Size | 680 × 289 CSS pixels at default (spec VR-001 canvas) |
| `decorations` | `false` |
| `transparent` | `false` |
| `resizable` | `true`, because maximize/restore is exposed in the title bar |
| Duplicate policy | Do not construct another window with this label |
| Controls | `getCurrentWindow()` minimize, toggleMaximize, close; title-bar `data-tauri-drag-region` excluding the controls |
| Non-Tauri host | Window controls stay rendered and no-op; rejected window promises are swallowed |

Tauri creates only this window.

## Presentation

Input: `CompanionWidgetPresentation` discriminated on `kind`: `paused` | `behindSchedule` | `offline` | `reminders`.

Output: one widget surface. Callbacks are optional and variant-specific. See [data-model.md](../data-model.md).

## Assets the contract may reference

- `/assets/widget/environment/daytime/morning.png`
- `/assets/widget/environment/season/spring.png`
- `/assets/mr-bloom/mr-bloom-spritesheet.png`
- `/assets/icons/leaf-icon.png`
- `/assets/plants/{monstera,sunflower,bonsai,jasmine,lavender}-spritesheet.png`

Forbidden: any `removed reference artwork/` path, including `widget-reference.svg`, and any inline base64 image.

`leaf-icon.png` is decorative title-bar branding beside visible `BLOOMING` text. It is not a balance badge. Character atlas dimensions and permitted frame sequences are defined once in [data-model.md](../data-model.md).
