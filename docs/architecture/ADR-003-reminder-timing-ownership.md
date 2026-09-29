# ADR 003: Reminder Timing and Resynchronization Ownership

## Context

The Blooming desktop application requires periodic data synchronization (e.g., focus sessions, plant state, and reminders) and must respond to system lifecycle events like waking from sleep or window focus. A clear architectural boundary is needed between the Tauri runtime (Rust) and the frontend application (Svelte) to prevent duplicated polling loops and conflicting synchronization mechanisms.

## Decision

Adopt a hybrid architecture with explicitly separated responsibilities:

- **Rust/Tauri Ownership ("The Reliable Clock")**: Rust owns *native/reliable* timing (e.g., cron-like ticks) and system lifecycle triggers (wake/resume).
- **Svelte Ownership ("The Data and the UI")**: Svelte exposes one central resynchronization contract (`resync()`). Frontend lifecycle and network triggers (`visibilitychange`, `online`, `window focus`) are permitted to trigger synchronization from the frontend, provided they converge on this same `resync()` method.

**Allowed Resync Triggers**:
- `native resume` (Tauri)
- Reliable timer (Tauri)
- `window focus` (Frontend/Tauri)
- `visibilitychange` (Frontend)
- `online` (Frontend)
- Widget show (Frontend)
-> *All must invoke the same `resync()`.*

**Contract Design**:

```
Rust trigger -> Svelte resync()
  -> fetchSession()
  -> fetchReminders()
  -> refreshPlant()
```

## Rationale

By restricting Tauri to just triggering events and centralizing the synchronization logic in a single Svelte `resync()` function, we guarantee that there is exactly one way the app updates its state. This avoids overlapping intervals, ensures UI consistency, and simplifies debugging.

## Consequences & Boundaries

- **No Implementation in Block 0**: The actual Rust event implementation and the concrete Svelte `resync()` implementation are out of scope for Block 0.
- **Single Boundary**: This document establishes exactly one clear boundary for synchronization responsibility.

## Deferred Work

- **Later Blocks**: Reminder polling refactor.
- **Later Blocks**: Implementation of system sleep/resume lifecycle events in Tauri.

## Acceptance Criteria

- [ ] Rust/Tauri is clearly defined as the owner of reliable timing and lifecycle triggers.
- [ ] Svelte is clearly defined as the owner of a central `resync()` function for fetching data.
