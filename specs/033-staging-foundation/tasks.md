# Tasks: Block 1 - Staging Foundation

- [x] T01: Audit frontend `.env` and `vite.config.ts`.
- [x] T02: Audit `tauri.conf.json` and Cargo dependencies.
- [x] T03: Audit backend `config.py` for CORS, JWT, Brevo.
- [x] T04: Create `frontend/.env.staging`.
- [x] T05: Create `frontend/src-tauri/tauri.staging.conf.json`.
- [x] T06: Update `FRONTEND_URLS` in `backend/app/core/config.py` for packaged Tauri origins.
- [x] T07: Update `ACCESS_TOKEN_EXPIRE_MINUTES` default to 30 in `backend/app/core/config.py`.
- [x] T08: Add `tauri-plugin-single-instance` to `Cargo.toml`.
- [x] T09: Initialize single instance plugin in `src/lib.rs`.
- [x] T10: Audit `.gitignore`.
- [x] T11: Generate Env Audit table.
- [x] T12a: Frontend staging build (PASS).
- [ ] T12b: Run native Tauri staging build (NOT VERIFIED: Cargo unavailable).
