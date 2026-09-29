# Staging Readiness Verification Record

Date: 2026-09-29

`PASS` means the named command or behavior was observed. `NOT VERIFIED` means required tooling, a native packaged environment, or hosted credentials were unavailable. No unavailable check is treated as passing.

## Block 1

| Check | Status | Evidence |
|---|---|---|
| Backend configuration | PASS | config unit tests |
| Development compatibility | PASS | backend unit and frontend suites |
| Frontend staging build | PASS | `npm run build -- --mode staging` |
| Tauri staging build | NOT VERIFIED | Cargo unavailable |
| Packaged launch | NOT VERIFIED | no native artifact |
| Backend connectivity | NOT VERIFIED | local backend/DB not running |
| Double launch | NOT VERIFIED | requires packaged native launch |

## Block 2 automated and manual verification

Automated tests cover device settings, time jumps, central coalescing resync, network-vs-401 handling, GET backoff/jitter, queue deduplication/flush/failure retention, and frontend finish-once behavior. The HTTP duplicate-finish regression exists but could not execute because Docker Desktop was stopped.

| Manual scenario | Status |
|---|---|
| Widget position persistence | NOT VERIFIED |
| Always-on-top and fixed sizing | NOT VERIFIED |
| Offline cold start and recovery | NOT VERIFIED |
| Close-to-tray, tray open, Quit/no orphan | NOT VERIFIED |
| Autostart ON/OFF and `--autostart` behavior | NOT VERIFIED |
| Sleep shorter/longer than Pomodoro and completion on wake | NOT VERIFIED |
| Network off/on and offline finish/reconnect flush/reward once | NOT VERIFIED |
| Fullscreen behavior | NOT VERIFIED |
| Native rotating log file | NOT VERIFIED |

## Block 3

| Check | Status |
|---|---|
| Environment contract/static secret audit | PASS |
| Local packaged-test CSP | PASS |
| Real hosted staging CSP | NOT VERIFIED — hosted API origin does not exist yet |
| Migration structure and runner contract | PASS |
| Compose configuration render | PASS |
| Fresh DB and upgrade DB migration | NOT VERIFIED |
| Schema smoke and baseline parity against PostgreSQL | NOT VERIFIED |
| Backend image build/run | NOT VERIFIED |
| `/health`, `/health/db`, `/health/ready` in container | NOT VERIFIED |
| DB/backend restart and invalid-config rehearsal | NOT VERIFIED |

Docker CLI is installed, but the Docker Desktop Linux daemon was unavailable. Cargo is unavailable. These are environment limitations, not successful checks.

## Block 4 final matrix

All hosted/manual items are `NOT VERIFIED`: cold start with backend down; backend recovery; sleep during Pomodoro; network off/on; offline finish queue; close to tray; tray Quit; double launch; autostart on/off; fullscreen; due reminder; tray alert icon; clock/timezone change; email verification; migration dry run; backup restore; native log availability; duplicate focus reward; and no logout on temporary network loss.

External staging PostgreSQL, backend deployment, hosted verification, real-URL Tauri installer, clean-machine installation, and final end-to-end testing are also `NOT VERIFIED` because no provider credentials or hosted target were available.

## Roadmap status

- Block 1 — INCOMPLETE: native staging build, packaged launch, connectivity, and double-launch observation remain.
- Block 2 — INCOMPLETE: Cargo/native compile and packaged Windows lifecycle matrix remain; DB-backed duplicate-finish test must run with Docker.
- Block 3 — INCOMPLETE: Docker image/Compose/database migration and readiness rehearsal must run with an active daemon.
- Block 4 — INCOMPLETE: hosted infrastructure, secrets, Brevo flow, installer, clean-machine and full E2E verification remain.
