# Blooming frontend

Desktop UI for Blooming on Windows and Linux. Stack: Tauri 2, Rust, SvelteKit with static/SPA output, Svelte 5, TypeScript, Vite, and npm.

## Architecture

The desktop application has a main planning window and a companion widget:

- **Feature module** at `src/lib/features/companion-widget/` with Atomic Design inside that feature (`atoms`, `molecules`, `organisms`), plus `fixtures/`, `types/`, `styles/`, and `model/`.
- **SvelteKit routes** are thin entry points. `+layout.svelte` files act as templates; `+page.svelte` files act as pages.

## Routes

| Path | Surface |
| --- | --- |
| `/widget` | Companion widget (default paused fixture) |
| `/widget-preview` | Development fixture selector outside the widget |
| `/auth` | Authentication entry point for the main window |
| `/onboarding` | Initial setup |
| `/today`, `/goals`, `/mr-bloom`, `/statistics`, `/settings` | Authenticated application surfaces |

Tauri creates the `main` window at `/auth` and the `companion-widget` window at
`/widget`. `/widget-preview` is development-only.

## Configuration

`frontend/.env.example` documents public frontend configuration:

```text
PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

The API client appends endpoint paths such as `/auth/login` and `/me`; it does
not append the backend API prefix. Therefore every environment must set
`PUBLIC_API_BASE_URL` to a base URL ending in exactly `/api/v1`. Hosted builds
(including Vercel) additionally require a public HTTPS URL and fail if they
would otherwise ship a local loopback address.

Public frontend environment variables are embedded in the client bundle and must never contain secrets.

## Develop

From the repository root, use the canonical launch commands so PostgreSQL and
the backend are started and checked before the frontend:

```bash
npm run dev:web
npm run dev:tauri
```

For frontend-only development from this directory:

```bash
npm run tauri dev
```

Browser preview: `npm run dev`, then open `http://127.0.0.1:1420/auth`,
`/widget`, or `/widget-preview`.

## Asset policy

All frontend runtime images live under `frontend/static/assets/`
and are referenced through root-relative `/assets/...` URLs.

`design-assets/` contains source/reference material only.

Tauri packaging icons remain under the Tauri-owned icon directory and
are not part of the frontend runtime asset convention.
