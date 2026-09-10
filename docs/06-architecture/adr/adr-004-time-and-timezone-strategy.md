# ADR-004: Store Instants in UTC and Retain the Plan Timezone

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 8 September 2026 |
| Supersedes/superseded by | None |

## Context and decision drivers

- Daily plans are understood in the user's local calendar date.
- APIs and storage must avoid ambiguous local timestamps.
- Focus recovery and re-planning compare actual instants with planned boundaries.
- Future users or deployments may use timezones with daylight-saving transitions.

## Options considered

| Option | Advantages | Disadvantages |
|---|---|---|
| Store local date-times only | Easy to display | Ambiguous across zones/DST and unsafe for elapsed-time calculations |
| Store UTC instants only | Unambiguous ordering | Loses the timezone needed to reconstruct local planning intent |
| Store UTC instants plus IANA timezone and planning date | Unambiguous and reconstructable | Requires explicit conversion rules and more fields |

## Decision

Blooming will accept ISO 8601 timestamps with explicit offsets, store persistent instants in UTC-capable columns, and retain each plan's IANA timezone ID and local planning date. Scheduling rules operate on a request normalized consistently to the plan timezone and whole-minute precision.

## Consequences

- Positive: execution duration and ordering remain unambiguous.
- Positive: local date and future timezone behavior can be reconstructed.
- Tradeoff: serialization and day-boundary tests are mandatory.
- Follow-up: include `Asia/Ho_Chi_Minh`, overnight windows, and one daylight-saving timezone in boundary tests.
- Follow-up: Tauri resolves WidgetContext time-of-day (`MORNING`, `AFTERNOON`, `EVENING`, `NIGHT`) locally from the configured timezone. That presentation context must not become a scheduler, reminder-timing, or Heart Progress input.

## Reconsider when

Never for the basic principle; implementation types may change if the selected persistence driver cannot preserve the required semantics.
