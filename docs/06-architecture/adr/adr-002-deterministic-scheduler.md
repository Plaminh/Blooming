# ADR-002: Use a Deterministic Scheduling Engine

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 8 September 2026 |
| Supersedes/superseded by | None |

## Context and decision drivers

- A plan must never silently overlap blocks, exceed an available window or Task deadline, move a fixed Task, alter a fixed event, miscount required Breaks, or lose Task duration.
- Scheduling results need reproducible tests and explanations.
- LLM outputs may vary across calls and providers.
- The project needs strong backend engineering evidence beyond prompt design.

## Options considered

| Option | Advantages | Disadvantages |
|---|---|---|
| LLM generates final timeline | Fast prototype and flexible language behavior | Non-repeatable, hard to guarantee invariants, expensive to regression test |
| Deterministic rules/heuristics | Repeatable, testable, explainable, provider-independent | Requires explicit rules and careful boundary handling |
| Optimization solver from the first sprint | Powerful constraint modeling | Adds modeling/library complexity before basic product behavior is validated |

## Decision

Blooming will implement a deterministic rule-based scheduler as pure domain logic. It returns one ordered PlanBlock timeline with generated Focus/Break blocks and unchanged Fixed Event blocks, enforces deadline and fixed/flexible Task rules, and applies the explicit Break formula. Identical normalized input and configuration produce identical ordered output. An optimization solver may be evaluated later only if a measured requirement cannot be met by the rule-based engine.

## Consequences

- Positive: correctness invariants and boundary behavior can be automated.
- Positive: scheduling remains available when the LLM provider fails.
- Tradeoff: task ordering and splitting policy must be documented explicitly.
- Tradeoff: early results may be less globally optimal than a solver but remain honest and understandable.
- Follow-up: treat any non-deterministic dependency on current time, database order, hash iteration, or randomization as a defect.

## Reconsider when

Real scenarios demonstrate that deterministic heuristics cannot satisfy important constraints without unacceptable schedules, and a solver spike provides measurable improvement while preserving explainability.
