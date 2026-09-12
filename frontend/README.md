# Blooming frontend

Desktop UI for Blooming on Windows and Linux. Stack: Tauri 2, Rust, SvelteKit with static/SPA output, Svelte 5, TypeScript, Vite, and npm.

## Architecture

The current desktop surface is the companion widget:

- **Feature module** at `src/lib/features/companion-widget/` with Atomic Design inside that feature (`atoms`, `molecules`, `organisms`), plus `fixtures/`, `types/`, `styles/`, and `model/`.
- **SvelteKit routes** are thin entry points. `+layout.svelte` files act as templates; `+page.svelte` files act as pages.

## Routes

| Path | Surface |
| --- | --- |
| `/widget` | Companion widget (default paused fixture) |
| `/widget-preview` | Development fixture selector outside the widget |

Tauri creates only the `companion-widget` window and loads `/widget`. `/widget-preview` is for `npm run dev` / `vite preview`.

## Configuration

`frontend/.env.example` documents public frontend configuration:

```text
PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Public frontend environment variables are embedded in the client bundle and must never contain secrets.

## Develop

From this directory:

```bash
npm run tauri dev
```

That command launches only the companion widget. Browser preview: `npm run dev`, then `http://127.0.0.1:1420/widget` or `/widget-preview`.
