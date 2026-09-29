# Implementation Plan: Block 1 - Staging Foundation

## 1. Current State
- Frontend uses Vite. `PUBLIC_API_BASE_URL` in `.env`.
- Tauri config lacks staging override.
- Backend CORS explicitly lists localhost in `config.py`.
- `ACCESS_TOKEN_EXPIRE_MINUTES` defaults to 1440 in `config.py` (fixed to 30 as default).

## 2. Architecture Approach
- **Frontend Staging Config**: Add `.env.staging`.
- **Tauri Staging Config**: Add `tauri.staging.conf.json`.
- **Backend CORS**: 
  - Development default: `http://localhost:1420`, `http://127.0.0.1:1420`
  - Staging override: `http://tauri.localhost`, `tauri://localhost`, hosted staging frontend origin
- **Single Instance**: Use `tauri-plugin-single-instance` to prevent multiple launches.
- **Ignore Rules**: `.gitignore` is updated to explicitly track `.env.staging` (`!.env.staging`) because it contains only public build configuration, while keeping other `.env.*` files ignored.

## 3. File-by-File Plan
- `frontend/.env.staging`: Set `PUBLIC_API_BASE_URL`.
- `frontend/src-tauri/tauri.staging.conf.json`: Set staging `productName` and `identifier`.
- `backend/app/core/config.py`: Update `FRONTEND_URLS` and default `ACCESS_TOKEN_EXPIRE_MINUTES`.
- `frontend/src-tauri/Cargo.toml`: Add `tauri-plugin-single-instance`.
- `frontend/src-tauri/src/lib.rs`: Initialize single instance plugin.

## 4. Tests
- Validate config values loaded in backend.
- Ensure Tauri compiles.

## 5. Deferred
- CSP hardening (Block 6).
- Refresh tokens (Production).
- Deep links (Future).
