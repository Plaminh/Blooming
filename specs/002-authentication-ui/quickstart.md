# Quickstart: Authentication UI and Desktop Validation

Blooming authentication is local UI only. These checks must not contact a backend or claim that an account was created.

## Automated validation

From `frontend/`:

```bash
npm run check
npm run test
npm run build
```

From `frontend/src-tauri/`:

```bash
cargo check
```

The DOM and axe checks cover semantics and behavior; they do not prove pixel-perfect rendering or real-browser contrast.

## Browser preview

From `frontend/`, run `npm run dev`, then open `http://localhost:1420/auth`.

1. At 1440x900, compare against `design-assets/app/references/authentication-login.png`. Check the teal frame/title bar, approximately 696px illustration column, warm-cream panel, decorative leaf, typography, segmented selector, ~596px controls, full-width action, lower separator, and prompt.
2. Confirm Login is default. Exercise both segmented buttons and both bottom mode-switch buttons; exactly one form is present at a time.
3. Submit empty and invalid values. After submission, confirm errors persist while values remain invalid and clear only after correction. In Register, changing either password must revalidate confirmation.
4. Confirm Remember me is a native checkbox and all three password controls toggle independently in their applicable modes.
5. Resize moderately and shorten the viewport. The form must remain reachable, Register must not clip, the illustration must crop without distortion, and vertical scrolling must be available when content is taller than the viewport.
6. Inspect the network panel. The runtime illustration may load from `/assets/authentication/backgrounds/authentication-background.png`; `authentication-login.png` must never be requested. No authentication/API request may occur.
7. Browser title-bar and widget-to-main actions must safely no-op without errors.

## Tauri desktop validation

From `frontend/`, run:

```bash
npm run tauri dev
```

Manually verify each item before marking it complete:

- Only `companion-widget` is visible at startup; the configured `main` window is hidden.
- A single click on the widget surface does not open `main`.
- A genuine double-click on a non-interactive widget surface opens the existing `main` window at `/auth` and focuses it.
- Double-clicking a widget button does not open `main`; existing buttons, drag behavior, animation, and speech/reminder content remain intact.
- Rapid and repeated surface double-clicks focus the same window and never produce duplicates.
- If `main` is minimized, a widget double-click unminimizes and focuses it.
- The main title bar drags the window; minimize and maximize/restore work; close hides `main` without terminating the widget; a later widget double-click reopens it.
- At 1440x900 and the 1000x700 minimum, Login and Register remain usable and visually coherent.

Windows behavior can be completed in the current environment. Linux remains a configuration/build-support check unless the application is actually launched on Linux; do not mark Linux runtime behavior manually verified from Windows.
