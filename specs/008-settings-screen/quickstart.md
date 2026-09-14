# Quickstart Validation Guide: Settings Screen

## Prerequisites
- Node.js installed
- Tauri dependencies available (if running Tauri)

## Validation Commands

### 1. Run Development Server (Browser Fallback)
```bash
npm run dev
```
Navigate to `http://localhost:5173/settings` (or the Vite assigned port).
**Expected Outcome**: The settings screen renders completely, matching the reference image layout. Tauri integration toggles (autostart, always-on-top) should gracefully log or update local state without crashing.

### 2. Form Interaction Validation
- Edit "Mr. Bloom's name" -> "SAVE CHANGES" enables (dirty state).
- Click "CANCEL" -> Reverts to original name.
- Clear "Mr. Bloom's name" -> "SAVE CHANGES" -> Validation error appears.
- Toggle "Start Blooming at login" -> visual toggle updates.

### 3. Visual Verification
- Ensure the browser window is sized to **1540x975**.
- Compare the rendered output against `design-assets/app/references/settings.png`.
- Check title bar colors, pixel font hierarchy, cream background, green toggles, and panel layouts.

### 4. Run Tauri App
```bash
npm run tauri dev
```
- Wait for the app to compile and launch.
- Navigate to the Settings screen via the sidebar.
- Toggle "Keep widget on top" and verify if the companion widget window behavior changes (if implemented, otherwise verify no crash).
