# Data Model: MVP AI System

This document outlines the internal domain models and validation schemas for the AI routing layer. These models exist purely in memory during the request lifecycle and are not persisted directly to the database.

## Pydantic Schemas (Strict Extra="forbid")

### `AIRequestContext`
Represents the input payload given to the AI router.
- `user_input` (str): The raw natural language input from the user.
- `context_type` (str): Enum indicating the context (e.g., "today_planning", "roadmap_planning").
- `current_time` (datetime): The deterministic current time to anchor the AI's temporal references, derived server-side.
- `timezone` (str): The user's local timezone.

### `InferredValue[T]`
Provenance wrapper for AI-generated values.
- `value` (T): The actual value.
- `source` (Literal["USER", "EXTRACTED", "AI_ESTIMATE", "DEFAULT"]): Where the value came from.
- `confidence` (float, optional): AI's confidence if estimated.

### `TaskDraft`
The schema-validated output from the AI for a single task.
- `title` (str): The extracted task name.
- `duration_min` (InferredValue[int], optional): Estimated duration in minutes.
- `priority` (InferredValue[str], optional): Priority level ("P1", "P2", "P3").
- `deadline` (InferredValue[datetime], optional): Task deadline if present.
- `is_core` (InferredValue[bool], optional): Core vs optional status.
- `is_fixed` (InferredValue[bool], optional): Fixed scheduling vs flexible.
- `dependencies` (List[str]): Task titles this depends on.

### `TodayDraftProposal`
The schema-validated output for a daily plan.
- `tasks` (List[TaskDraft]): List of proposed tasks for today.

### `MilestoneDraft`
The schema-validated milestone output.
- `title` (str): Milestone title.
- `target_date` (InferredValue[datetime], optional): Proposed target date.

### `RoadmapDraftProposal`
The schema-validated output for long-term goals.
- `goal_title` (str): The overarching goal.
- `milestones` (List[MilestoneDraft]): Proposed milestones with target dates.

### TodayAIInterpretation & RoadmapAIInterpretation
These envelop the AI's response to handle both draft proposals and clarification requests securely.
- `status` (Literal["DRAFT", "NEEDS_CLARIFICATION"]): The outcome of the interpretation.
- `questions` (list[str] | None): A list of questions if status is `NEEDS_CLARIFICATION`.
- `proposal` (TodayDraftProposal | RoadmapDraftProposal | None): The drafted proposal if status is `DRAFT`.

**Semantic Invariants**:
- If `status == "DRAFT"`: `proposal` is required, `questions` must be absent.
- If `status == "NEEDS_CLARIFICATION"`: `questions` is required and non-empty, `proposal` must be absent.

## State Transitions

### AI Routing Flow
1. Server constructs `AIRequestContext` including precise `current_time`.
2. `RuleParser` evaluates `AIRequestContext`. If deterministic (e.g. simple task parsing command like `task: Clean desk, 30m`), it returns a structured task proposal immediately, bypassing AI generation, but still routing through standard business validation.
3. If unresolved, `GroqProvider` attempts to generate a JSON response.
4. Response is validated against Pydantic model (`TodayDraftProposal` or `RoadmapDraftProposal`).
5. If Groq fails natively or schema validation fails, `GeminiProvider` is invoked (fallback_triggered=True).
6. Result mapped to `BusinessValidator` which validates without persistence.
7. Final Response (`status: success`, `status: needs_clarification`, or `status: error`) returned to frontend.
