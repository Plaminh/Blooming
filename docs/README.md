# Blooming Personal Project Documentation Templates

This pack is based on the useful documentation structure from AmeThyst, cleaned up for a solo portfolio project and extended for Blooming's scheduling and AI behavior.

**Source of truth for product decisions:** `02-product/Blooming-Concept-Updated.md`. Other documents must not preserve conflicting stack, widget, plant, reminder, or scope behavior.

## Design rule

- Keep one canonical copy of each project document.
- Create repeated files only for a real unit of work: one sprint report per sprint, one ADR per major decision, and one specification folder per feature.
- Do not create empty future documents merely to increase the file count.
- Use Markdown and Mermaid so documentation stays version-controlled with code.
- Replace `<PLACEHOLDERS>` and delete `<!-- guidance comments -->` before publishing.

## Included project documents

This package now contains both reusable templates and Blooming's current project documents:

- Files ending in `_template.md` and `07-specifications/feature-template/` are reusable blank templates.
- Filled documents use the final filename without `_template`, for example `product-proposal.md`.
- `project-readme.md` is Blooming's current project README; this `README.md` explains the documentation package.
- `02-product/Blooming-Concept-Updated.md` is the frozen MVP concept.
- `07-specifications/001-quick-planning/` contains the implementation-ready specification, two-increment plan, tasks, and tests for the deterministic scheduler.
- Test results, bug reports, AI evaluation results, deployment/release documents, sprint reports, and the reflective report must be instantiated only when real evidence exists.

## What changed from AmeThyst

| AmeThyst artifact | Decision for Blooming | Reason |
|---|---|---|
| Project Proposal | Keep | Useful short explanation of why the product should exist. |
| App Survey | Keep | Grounds product differentiation and UI decisions. |
| Vision Document | Keep | Defines users, positioning, product features, assumptions, and quality goals. |
| Project Plan | Keep and simplify | Remove team roles; keep milestones, schedule, risks, builds, and quality. |
| Planning + Weekly + Review reports | Merge into one `sprint-report` per sprint | They describe one sprint lifecycle and do not need three separate files. |
| Team Contract | Remove | No team exists. |
| Spec Kit Summary | Remove | The feature specification folders are better evidence. |
| Changes files per PA | Replace with one `CHANGELOG.md` | No assignment resubmission lifecycle. |
| Duplicate files under both `management/PAx` and canonical folders | Remove | Keep one source of truth. Git already preserves history. |
| Per-section performed/reviewed/edited lines | Remove | Meaningless for one developer. |
| Use-case model and specifications | Keep | Useful for non-trivial workflows and portfolio explanation. |
| C4 context, container/component, deployment | Keep | They explain the implemented system at different levels. |
| Test plan, cases, execution, bugs | Keep | Separate planning, design, evidence, and defect records. |
| Reflective report | Keep and personalize | Useful for portfolio learning and interview preparation. |
| AI usage report | Keep as one continuous log | Provides transparent evidence without repeating it every sprint. |

## Added for Blooming

- Frozen product concept: `02-product/Blooming-Concept-Updated.md` is the single source of truth for MVP product decisions.
- MVP scope: prevents the full product vision from becoming the first release.
- Product backlog: separates future ideas from committed work.
- Domain glossary and scheduler business rules: prevents ambiguity in Task, PlanBlock, FocusRun, overload, breaks, and re-planning.
- Explicit functional and non-functional requirements.
- UI/UX design record with flows, screens, states, and accessibility.
- Data/API design: keeps contracts clear before implementation.
- ADRs: records only important, expensive-to-reverse decisions.
- Security/privacy: Blooming stores personal routines and may send text to an LLM.
- Per-feature spec/plan/tasks/tests: preserves the Spec Kit-style implementation workflow.
- AI evaluation: tests schema validity, interpretation quality, fallback, latency, and cost.
- Setup/deployment, release notes, and demo script: make the repository usable and portfolio-ready.

## Folder structure

```text
docs/
├── README.md
├── CHANGELOG.md
├── 01-discovery/
├── 02-product/
├── 03-management/
│   └── sprints/
├── 04-requirements/
├── 05-ui-ux/
├── 06-architecture/
│   └── adr/
├── 07-specifications/
│   └── 001-feature-name/
├── 08-testing/
└── 09-release/
```

## Template inventory

### Root

- `project-readme_template.md`
- `changelog_template.md`

### 01 - Discovery

- `product-proposal_template.md`
- `app-survey_template.md`

### 02 - Product

- `vision-document_template.md`
- `mvp-scope_template.md`

### 03 - Management

- `project-plan_template.md`
- `product-backlog_template.md`
- `sprint-report_template.md` - copy once per sprint.
- `ai-usage-report_template.md` - one continuous project log.

### 04 - Requirements

- `domain-rules_template.md`
- `functional-requirements_template.md`
- `non-functional-requirements_template.md`
- `use-case-model_template.md`
- `use-case-specification_template.md` - copy once per use case or functional group.

### 05 - UI/UX

- `ui-ux-design_template.md`

### 06 - Architecture

- `system-context_template.md`
- `container-component_template.md`
- `data-api-design_template.md`
- `deployment-diagram_template.md`
- `security-privacy_template.md`
- `adr_template.md` - optional; copy only for major decisions.

### 07 - Per-feature specification

- `spec.md`
- `plan.md`
- `tasks.md`
- `tests.md`

### 08 - Testing

- `test-plan_template.md`
- `test-cases_template.md`
- `test-execution-result_template.md`
- `bug-report_template.md`
- `ai-evaluation_template.md`

### 09 - Release

- `setup-deployment_template.md`
- `release-notes_template.md`
- `demo-script_template.md`
- `reflective-report_template.md`

## What to write before the first feature

Do not finish all 35 templates now. Before coding the deterministic Quick Planning Engine, complete:

1. Product Proposal - short first version.
2. App Survey - first comparison and conclusions.
3. Vision Document - current product direction.
4. MVP Scope - firm first-release boundary.
5. Project Plan - immediate milestones and risks.
6. Domain Rules - scheduler terminology and invariants.
7. Functional and Non-functional Requirements - Quick Plan portion.
8. Use-case model/specification - Quick Plan and overload handling.
9. System Context and Container/Component architecture - initial version.
10. Data/API Design - `/plans/preview` contract and initial entities.
11. All four files in `07-specifications/feature-template/`.

The remaining templates are filled when their trigger occurs.

## Lightweight IDs

| Artifact | Pattern | Example |
|---|---|---|
| Functional requirement | `FR-<AREA>-NNN` | `FR-PLAN-001` |
| Non-functional requirement | `NFR-<QUALITY>-NNN` | `NFR-PERF-001` |
| Business rule | `BR-NNN` | `BR-004` |
| Use case | `UC-<AREA>-NN` | `UC-PLAN-01` |
| Feature specification | `SPEC-NNN` | `SPEC-001` |
| Test case | `TC-<AREA>-NNN` | `TC-PLAN-008` |
| Bug | `BUG-NNN` | `BUG-003` |
| Architecture decision | `ADR-NNN` | `ADR-002` |
