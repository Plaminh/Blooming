# Non-Functional Requirements

Every requirement includes a measurable target and a verification method. Targets are MVP quality floors and may be tightened after real measurements.

## 1. Performance and capacity

| ID | Requirement and pass threshold | Verification | Priority |
|---|---|---|---|
| NFR-PERF-001 | The preview scheduler shall complete within 500 ms at p95 for requests containing up to 50 tasks and 50 fixed events on the reference development environment, excluding network latency. | Automated performance fixture with at least 100 executions | Must |
| NFR-PERF-002 | Non-AI API operations shall complete within 1 second at p95 under a single-user workload, excluding cold starts. | API timing test or production telemetry | Should |
| NFR-AI-001 | Conversational interpretation shall return a draft or actionable timeout response within 15 seconds for at least 95% of evaluation calls. | Timed AI evaluation set | Must |

## 2. Reliability and correctness

| ID | Requirement and pass threshold | Verification | Priority |
|---|---|---|---|
| NFR-REL-001 | Zero accepted scheduler results may violate BR-001–BR-005 or BR-021–BR-037. | Property/invariant tests and regression fixtures | Must |
| NFR-REL-002 | Identical normalized scheduler input shall produce identical ordered output in 100 repeated executions. | Repeatability test | Must |
| NFR-REL-003 | A successful save shall be readable after application restart without loss of tasks, events, sessions, timezone, or configuration. | Persistence integration test | Must |
| NFR-REL-004 | Active timer recovery shall calculate elapsed/remaining time within one second of the expected value after widget hide, sleep, or main-window close. | Controlled-clock desktop/integration test | Must |
| NFR-REL-005 | Re-planning shall preserve every protected completed execution, fixed event, and locked fixed-Task PlanBlock exactly. | Before/after invariant comparison | Must |

## 3. Security and privacy

| ID | Requirement and pass threshold | Verification | Priority |
|---|---|---|---|
| NFR-SEC-001 | All external production communication shall use HTTPS/TLS; database transport shall use provider-supported encrypted connections. | Deployment configuration inspection | Must |
| NFR-SEC-002 | All request data shall be validated server-side before domain or persistence operations. | Negative API tests and code review | Must |
| NFR-SEC-003 | No API key, password, connection secret, or real `.env` file may exist in version control. | Secret scan and repository review | Must |
| NFR-PRIV-001 | Logs shall not contain task descriptions, conversational content, credentials, tokens, or full AI prompts. | Log assertions and manual review | Must |
| NFR-PRIV-002 | The AI request shall contain only fields necessary for semantic interpretation and shall exclude stored history unless explicitly required and disclosed. | Prompt-payload inspection | Must |
| NFR-PRIV-003 | The system must provide deletion of user-owned planning, Goal, Reminder, GardenState, HeartEvent, WeatherSnapshot, and execution data while documenting backup retention. | API/integration test | Must |

## 4. Usability and accessibility

| ID | Requirement and pass threshold | Verification | Priority |
|---|---|---|---|
| NFR-USE-001 | A user familiar with task planners shall be able to create a five-task structured preview in at most two minutes without documentation. | Timed usability walkthrough | Should |
| NFR-USE-002 | Validation and overload messages shall identify the affected field/task and a recovery action; status shall not rely on color alone. | UI content review and scenario tests | Must |
| NFR-ACC-001 | Critical planning and focus controls shall be keyboard-operable with visible focus indication. | Keyboard-only walkthrough | Must |
| NFR-ACC-002 | Text and essential controls shall meet WCAG 2.2 AA contrast targets. | Automated and manual contrast check | Should |
| NFR-RESP-001 | Critical full-application flows shall remain usable at typical desktop window widths from 1024 px to 1920 px without horizontal page scrolling. The widget is a compact always-on-top surface, not a mobile layout. | Desktop window-size tests | Must |

## 5. Compatibility, maintainability, and testability

| ID | Requirement and pass threshold | Verification | Priority |
|---|---|---|---|
| NFR-COMP-001 | The MVP shall run on current Windows 10/11 and a current Linux desktop environment used in the release test window. | Desktop smoke test on Windows and Linux | Must |
| NFR-MAINT-001 | Scheduling domain logic shall not depend on HTTP, database, UI, system clock, or LLM classes. | Architecture test/code review | Must |
| NFR-MAINT-002 | Public API behavior shall be documented under `/api/v1` and breaking changes shall require a version or migration decision. | OpenAPI/documentation comparison | Must |
| NFR-TEST-001 | Every Must scheduler business rule shall have at least one automated test; boundary and error rules shall have negative tests. | Traceability review | Must |
| NFR-TEST-002 | CI shall run backend tests and frontend lint/type/build checks on every pushed change before release. | CI run evidence | Must |

## 6. Date, time, AI quality, and cost

| ID | Requirement and pass threshold | Verification | Priority |
|---|---|---|---|
| NFR-TIME-001 | API timestamps shall use ISO 8601 with an explicit offset; instants shall be stored as UTC and plans shall retain an IANA timezone ID. | Serialization and persistence tests | Must |
| NFR-TIME-002 | Planning-date and day-boundary behavior shall be evaluated in the plan's timezone, including windows crossing midnight. | Boundary tests with `Asia/Ho_Chi_Minh` and one DST timezone | Must |
| NFR-AI-002 | At least 95% of evaluation outputs shall be schema-valid after one model response; 100% shall be either validated or rejected before scheduling. | Versioned AI evaluation dataset | Must |
| NFR-AI-003 | AI failure or malformed output shall never prevent manual structured planning; state-changing output must be schema-validated. | Timeout, invalid-output, and provider-unavailable tests | Must |
| NFR-COST-001 | Each conversational planning request shall be limited to one initial call and at most two clarification calls unless the user explicitly restarts. | Usage log and request counter | Must |
| NFR-REM-001 | Reminder due times must honor the user's IANA timezone. FastAPI must not be polled once per second. Duplicate persistence of one reminder action for one occurrence must not occur. | Timezone, sync, and idempotency tests | Must |
| NFR-PLANT-001 | HeartEvent writes must be deterministic, auditable, and transactional. Switching PlantType must not mutate Heart Progress or GardenState stage. | Domain and transaction tests | Must |
| NFR-WX-001 | WeatherContext refresh must be coarse (startup, wake, location change, low-frequency interval) and cached. A fetch failure may yield `UNKNOWN` and time-only visuals. Disabling weather-aware visuals must omit the weather overlay without requiring WeatherContext `UNKNOWN`. `UNKNOWN` must not affect scheduling, reminders, Heart Progress, or planning. | Cache, fallback, and negative tests | Must |

## 7. Observability

| ID | Requirement and pass threshold | Verification | Priority |
|---|---|---|---|
| NFR-OBS-001 | Errors shall include a stable error code and correlation ID while excluding personal content. | API and log test | Must |
| NFR-OBS-002 | Production monitoring shall track health, error count/rate, API latency, AI latency/failure, and AI usage without recording prompt content. | Deployment review | Must before production |

## Coverage checklist

- [x] Performance and response time
- [x] Reliability, persistence, and recovery
- [x] Security and privacy
- [x] Usability and accessibility
- [x] Desktop compatibility
- [x] Weather-context fallback and coarse caching
- [x] Maintainability and testability
- [x] Timezone and date-time correctness
- [x] AI schema validity, quality, latency, and cost
