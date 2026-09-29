# Implementation Plan: Block 2

1. Add fake-timer tests for time jumps, coalescing, retry, and the finish queue.
2. Introduce a framework-independent reliability module.
3. Route widget triggers through `resync()` and persist device-local position.
4. Emit native resume, add bounded native logging, and harden window configuration.
5. Add an HTTP-level duplicate focus-finish regression test.

Sub-fetches run concurrently because they have no ordering dependency. A failed sub-fetch preserves its existing UI state and leaves freshness unsuccessful.
