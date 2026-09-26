# Feature: Refactor Goals into a hybrid goal-management and roadmap-tracking experience

## PRODUCT DECISION
Goals must NOT become fully read-only like Today.
Goals uses a HYBRID ownership model.

Goal UI owns:
- viewing goals
- viewing roadmap and milestone progress
- viewing milestone details
- small metadata corrections
- changing milestone target dates
- recording milestone completion

Mr. Bloom owns:
- creating goals
- creating roadmap structure
- adding milestones
- removing milestones
- reordering milestones
- restructuring roadmap
- replanning an existing roadmap
- bulk structural changes

Today remains outside this feature.

## REMOVE GENERIC "EDIT MANUALLY"
Remove the generic:
    EDIT MANUALLY
interaction from Goal Detail.
Do not use JavaScript `prompt()` dialogs for editing Goal or Milestone data.
Replace generic/manual editing with explicit field-level editing UX.

Examples:
Goal metadata:
- title
- description

Milestone metadata:
- title
- expected outcome
- target date

Each editable field must use an appropriate structured control.
Do not introduce free-text prompts.

## GOAL METADATA EDITING
Goal UI may directly edit LOW-SIDE-EFFECT goal metadata.
Target supported fields:
- Goal title
- Goal description

Editing must:
- use normal form controls
- validate input
- persist through existing backend update capabilities
- show loading/error state
- refresh local state after success

Do not allow roadmap structure changes through this editor.

## MILESTONE METADATA EDITING
Goal UI may directly edit:
- milestone title
- expected outcome
- target date

Use actual supported backend fields.
Do not invent unsupported properties.
Milestone editing must be field-level and structured.

Examples:
- title → text input
- expected outcome → text/textarea
- target date → date picker

Do NOT expose raw status enum editing as a generic field.

## MILESTONE TARGET DATE
Milestone target date may remain directly editable in Goal UI.
This is allowed because current backend milestone update logic already owns reminder synchronization.

Required invariant:
Milestone date update
→ persisted milestone update
→ reminder resynchronization
→ no stale reminder
→ no duplicate active reminder

The frontend must NOT independently manipulate reminder records.
Use the existing backend service path.

## MILESTONE STATUS
Remove free-text status editing.
The user must NOT type enum values such as PENDING, IN_PROGRESS, COMPLETED, SKIPPED, CANCELLED into a prompt.
Status changes must be represented as DOMAIN ACTIONS.

Required action:
    MARK COMPLETE

Mark Complete must use the existing milestone update/service behavior so that:
- milestone status becomes COMPLETED
- completed_at is recorded
- milestone reminder is resolved/cancelled appropriately
- Leaves are awarded according to existing Blooming economy behavior
- duplicate reward granting remains prevented by backend logic

Do not add generic status dropdowns unless explicitly supported by the existing product requirements.

## ROADMAP STRUCTURAL CHANGES
Goal UI must NOT directly support:
- Add Milestone
- Remove Milestone
- Reorder Milestones
- restructure roadmap
- bulk date restructuring
- roadmap regeneration

These belong to Mr. Bloom.
The Goal Detail screen should expose:
    ADJUST WITH MR. BLOOM
for structural changes.

## MR. BLOOM — EXISTING GOAL ADJUSTMENT
Implement product requirements for editing/replanning an EXISTING Goal through Mr. Bloom.

Target conceptual flow:
Goal Detail
→ Adjust with Mr. Bloom
→ pass Goal ID/context
→ load persisted Goal + milestones
→ convert to editable RoadmapDraft / equivalent working draft
→ user requests structural change
→ review updated roadmap
→ explicit Save
→ update existing Goal/Milestones
→ return to Goal Detail

The specification must not require a particular query-string or state mechanism unless current architecture makes one appropriate.
The important requirement is preserving existing Goal identity and milestone identity where possible.

## MR. BLOOM STRUCTURAL CAPABILITIES
Existing-goal adjustment should support structural operations such as:
- add milestone
- remove milestone
- reorder milestones
- restructure roadmap
- change multiple milestones together
- replan remaining roadmap

Do not require Mr. Bloom for simple typo corrections.

## COMPLETED MILESTONES DURING REPLAN
Completed milestones are execution history.
Existing-goal replan MUST preserve completed milestones unless the user explicitly requests otherwise and the product supports that behavior.

A roadmap replan must not silently:
- delete completed milestones
- reset completed status
- remove completed_at
- duplicate milestone rewards

Completed milestone history is authoritative.

## MILESTONE ORDERING
Current milestone ordering uses a unique `(goal_id, position)` constraint.
Do NOT implement structural reordering using naïve sequential PUT calls that temporarily create duplicate positions.
The specification must require structural roadmap updates to be atomic or otherwise safely coordinated by backend code.

## REMINDER CONSISTENCY
Any milestone mutation that affects reminders must preserve reminder integrity.

At minimum:
Changing target date:
→ reschedule reminder

Completing milestone:
→ resolve/cancel reminder

Removing milestone through structural adjustment:
→ remove/cancel associated reminder safely

Replanning milestone dates:
→ synchronize reminders to the final persisted roadmap

No stale active reminder may reference an outdated milestone date.
No duplicate active reminder should be created.

## GOALS ↔ TODAY BOUNDARY
Do not redesign Today.
Goal/milestone changes must not directly mutate Today plan geometry.
Existing milestone-linked tasks may continue using current behavior.
Do not introduce automatic milestone completion from Today task completion unless it already exists as approved product behavior.

## GOAL CREATION
Keep current ownership:
Create Goal
→ Mr. Bloom
→ RoadmapDraft
→ review
→ Save to Goals

Do NOT add a manual "Create Goal" form to Goals UI.
The backend POST /goals capability may remain even if unused by production UI.

## DELETE BEHAVIOR
Do not expose direct Goal deletion or Milestone deletion buttons in Goals UI as part of this feature.
Structural milestone removal belongs to Adjust with Mr. Bloom.
Do not automatically delete backend DELETE endpoints. They must remain until dependency analysis confirms whether they are safe to deprecate.

## GOAL COMPLETION
Do NOT invent a new Goal-completion policy in this feature.
The audit found that Goal progress is derived from completed milestones while Goal status may remain ACTIVE.
Document this as a separate consistency gap unless an existing product requirement already defines automatic or explicit Goal completion.
Do not silently implement auto-completion without a product decision.

## USER FLOWS
FLOW A — View Goal
Goals → select Goal → Goal Detail → inspect roadmap, milestones, progress

FLOW B — Edit Goal Metadata
Goal Detail → edit title/description → validate → persist → refresh UI

FLOW C — Edit Milestone Metadata
Select milestone → edit title/outcome/date → persist → reminder resync if date changed → refresh UI

FLOW D — Complete Milestone
Select milestone → Mark Complete → persisted COMPLETED state → completed_at → Leaves → reminder resolved → progress updates

FLOW E — Structural Adjustment
Goal Detail → Adjust with Mr. Bloom → load existing Goal context → modify roadmap draft → review → explicit Save → persisted roadmap updated → Goal Detail refresh

FLOW F — Replan Existing Roadmap
Goal Detail → Adjust with Mr. Bloom → request replan → preserve completed milestones → regenerate remaining roadmap → review → Save → reminders synchronized
