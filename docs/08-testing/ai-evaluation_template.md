# AI Evaluation: <FEATURE_NAME>

## 1. Evaluation objective and boundary

<!-- Define what the AI does, what deterministic code validates, and what failure is unacceptable. -->

| Stage | AI or deterministic | Responsibility | Fallback |
|---|---|---|---|
| `<STAGE>` | `<TYPE>` | `<RESPONSIBILITY>` | `<FALLBACK>` |

## 2. Evaluation dataset

| Dataset/version | Cases | Source | Privacy handling | Limitations |
|---|---:|---|---|---|
| `<NAME>` | `<N>` | Synthetic/User-approved/Other | `<HANDLING>` | `<LIMITS>` |

## 3. Metrics and thresholds

| Metric | Definition/method | Target |
|---|---|---:|
| Schema-valid output rate | `<METHOD>` | `<%>` |
| Interpretation quality | `<RUBRIC>` | `<TARGET>` |
| Fallback success | `<METHOD>` | `<%>` |
| Latency | `<PERCENTILE>` | `<TIME>` |
| Cost | `<UNIT>` | `<AMOUNT>` |

## 4. Results

| Category/metric | Result | Target | Pass? | Evidence |
|---|---:|---:|---|---|
| `<METRIC>` | `<RESULT>` | `<TARGET>` | Yes/No | `<LINK>` |

## 5. Error analysis

| Failure pattern | Frequency | User impact | Cause hypothesis | Mitigation |
|---|---:|---|---|---|
| `<PATTERN>` | `<N_OR_%>` | `<IMPACT>` | `<HYPOTHESIS>` | `<ACTION>` |

## 6. Limitations and release decision

Go / Conditional / No-go because `<EVIDENCE_AND_RESIDUAL_RISK>`.

