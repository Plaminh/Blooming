# ADR-003: Limit the LLM to Semantic Interpretation

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 8 September 2026 |
| Supersedes/superseded by | None |

## Context and decision drivers

- Conversational capture is valuable because users describe tasks and constraints informally.
- LLM output can be invalid, ambiguous, variable, delayed, or unavailable.
- Schedule correctness must be enforced consistently and remain testable.
- Personal planning text should be minimized when sent externally.

## Options considered

| Option | Advantages | Disadvantages |
|---|---|---|
| LLM handles interpretation and scheduling | One apparent intelligent step | Weak correctness guarantees and difficult traceability |
| LLM interprets; backend validates and schedules | Natural input with deterministic correctness | Requires schema, review UI, and explicit clarification/fallback |
| No LLM | Simplest privacy and reliability model | Loses the intended conversational experience |

## Decision

The LLM will convert natural-language intent into the same structured request used by manual planning or identify missing required information. Backend validation and the deterministic scheduling engine remain authoritative. Users review and may edit the interpreted draft before scheduling.

## Consequences

- Positive: one scheduling path serves both manual and conversational input.
- Positive: provider changes do not alter core scheduling semantics.
- Positive: AI failure has a straightforward manual fallback.
- Tradeoff: conversation cannot promise fully autonomous planning.
- Follow-up: version the evaluation dataset and inspect the exact minimized provider payload before conversational integration is released.

## Reconsider when

A future bounded feature requires generative suggestions that do not affect correctness-critical state and has its own validation and fallback contract.
