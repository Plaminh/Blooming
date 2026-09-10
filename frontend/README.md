# Blooming frontend

Desktop UI for Blooming on Windows and Linux. Stack: Tauri 2, Rust, SvelteKit with static/SPA output, Svelte 5, TypeScript, Vite, and npm. The UI talks to a remote FastAPI backend.

## Architecture

This app uses a hybrid layout:

- **Feature modules** in `src/lib/features` currently contain only the placeholder UI each surface needs (`components/` plus a public `index.ts`). Add `api`, `stores`, and `types` directories later, when a real feature requires them.
- **Atomic Design** in `src/lib/shared/components` is only for reusable shared UI (`atoms`, `molecules`, `organisms`).
- **SvelteKit routes** are page composition and entry points. `+layout.svelte` files act as templates; `+page.svelte` files act as pages. There are no separate `templates` or `pages` folders.

Shared components are generic (Button, NavItem, AppNav). Feature components are product-specific (Today, Goals, Settings, widget) and stay inside their feature.

The `/widget` route loads only shared primitives plus `features/widget`. It does not import the main application navigation or other feature modules.

## Routes

| Path | Surface |
| --- | --- |
| `/` | Today (main app) |
| `/goals` | Goals (main app) |
| `/settings` | Settings (main app) |
| `/widget` | Mr. Bloom widget |

Today, Goals, and Settings share the `(app)` layout. `/widget` is outside that group.

## Configuration

`frontend/.env.example` documents public frontend configuration:

```text
PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Public frontend environment variables are embedded in the client bundle and must never contain secrets.

The API client reads `PUBLIC_API_BASE_URL` via `$env/dynamic/public` and falls back to `http://127.0.0.1:8000`. The packaged desktop app must receive its API URL at development or build time.

## Develop

From this directory:

```bash
npm run tauri dev
```

## Deferred

Real FastAPI contracts, product features, and Tauri multi-window behavior (including a dedicated widget window) are intentionally not implemented yet.
