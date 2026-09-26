# Plan: Refactor Goals into a hybrid goal-management and roadmap-tracking experience

## WORKSTREAM 1 — GOAL DETAIL UI
Audit actual components/callers.
Plan removal of:
- EDIT MANUALLY generic button
- JavaScript prompt() title editing
- prompt()-based date editing
- prompt()-based milestone status editing

Plan structured controls for:
Goal: title, description
Milestone: title, expected outcome, target date

Prefer small field-level editing rather than one giant form if that matches existing UI architecture.

## WORKSTREAM 2 — MILESTONE COMPLETION
Plan explicit MARK COMPLETE behavior.
Reuse current backend milestone update service.
Verify: completed_at, Leaves, reminder resolution, idempotency, progress refresh.
Do not add a generic status editor.

## WORKSTREAM 3 — REMINDER SAFETY
Trace actual milestone update service and reminder sync calls.
Plan tests for: date change reschedules reminder, completion resolves reminder, repeated update does not duplicate active reminders.
Do not move reminder logic into frontend.

## WORKSTREAM 4 — EXISTING GOAL → MR. BLOOM HANDOFF
Trace current Mr. Bloom RoadmapDraft flow.
Design the smallest extension that supports:
Goal Detail → Adjust with Mr. Bloom → load existing Goal + milestones → editable roadmap draft → preserve persisted IDs → user modifies structure → review → Save existing Goal → return to Goal Detail.

Reuse existing roadmap draft components and stores wherever possible. Avoid building a second roadmap editor.

## WORKSTREAM 5 — EXISTING GOAL SAVE
Plan how persisted Goal identity and Milestone identity are preserved.
Classify milestones during save as: existing unchanged, existing updated, newly created, removed.
Completed milestones require special protection.
The plan must explain how backend updates are applied transactionally.
Do not implement naïve delete-all-and-recreate.

## WORKSTREAM 6 — ROADMAP REORDER SAFETY
Audit the `(goal_id, position)` unique constraint.
Plan an atomic reorder/update mechanism.
Do NOT plan independent PUT requests that can temporarily create duplicate positions.
Determine the appropriate backend transaction/service boundary.

## WORKSTREAM 7 — MR. BLOOM ROUTING
Audit AI router / roadmap handler.
Plan support for existing Goal structural adjustment.
Determine: whether EDIT_GOAL / REPLAN_GOAL intents are needed, how existing Goal context enters assistant state, how roadmap draft patches are applied, how save knows it is updating rather than creating.

## WORKSTREAM 8 — API DEPENDENCY AUDIT
Audit repository-wide callers of:
- PUT /goals/{goal_id}
- PUT /goals/{goal_id}/milestones/{milestone_id}
- POST /goals
- POST /goals/{goal_id}/milestones
- DELETE /goals/{goal_id}
- DELETE /goals/{goal_id}/milestones/{milestone_id}
Classify: production UI, Mr. Bloom, reminder/service dependency, test-only, unused.
Do not delete endpoints solely because UI does not expose them.

## WORKSTREAM 9 — TEST IMPACT
Plan frontend tests for: Goal metadata editing, Milestone metadata editing, no prompt(), no generic Edit Manually, Mark Complete, target date editing, Adjust with Mr. Bloom.
Plan backend tests for: metadata updates, reminder resync, completion side effects, authorization, existing Goal structural save, reorder safety, completed milestone preservation.

## IMPLEMENTATION ORDER
1. lock current/new behavior with tests
2. replace Goal prompt editing
3. replace Milestone prompt editing
4. add Mark Complete action
5. verify reminder integration
6. implement existing Goal handoff to Mr. Bloom
7. implement structural draft editing/replan
8. implement transactional existing-roadmap save
9. add safe reorder handling
10. clean dead UI code
11. update manual tests/docs
12. regression test
