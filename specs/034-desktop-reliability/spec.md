# Feature Specification: Block 2 - Tauri Desktop Reliability

**Status**: Implemented; native/manual verification pending

## Goal

Keep the widget, focus timer, reminders, and session state correct across sleep, offline periods, reconnects, and long-running desktop use.

## Current-state findings

The widget used three independent polling/listener paths. Focus elapsed time was timestamp-based and backend rewards were already idempotent, but no frontend retry queue or time-jump signal existed.

## Requirements and architecture

- Native lifecycle, focus, visibility, online, widget, and periodic triggers converge on one `resync()`.
- The three independent reads execute concurrently and overlapping calls coalesce.
- Safe GET requests retry with bounded exponential backoff and jitter; mutations do not.
- `/focus/finish` network failures are stored in a small device-local deduplicated queue and flushed online.
- Widget position is device-local; account settings remain server-owned.
- The timer derives elapsed time from server timestamps and finishes at most once.
- Native file logs rotate; widget is fixed size and always on top.

## Success criteria

Automated reliability and duplicate-finish tests pass. Packaged lifecycle behavior is not considered verified until exercised manually.
