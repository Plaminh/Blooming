# Tasks: Refactor Goals into a hybrid goal-management and roadmap-tracking experience

## GROUP 1 — LOCK NEW GOAL UI CONTRACT
Add/update tests proving:
- no generic EDIT MANUALLY action
- no window.prompt() usage
- Goal title displayed
- Goal description displayed
- explicit Goal metadata edit controls exist
- structural Add/Remove/Reorder controls do NOT exist directly in Goal UI
- Adjust with Mr. Bloom exists

## GROUP 2 — GOAL METADATA EDITING
Implement/test structured editing for: Goal title, Goal description.
Tasks must include: validation, loading state, error handling, backend persistence, local/store refresh, cancel behavior.

## GROUP 3 — MILESTONE METADATA EDITING
Implement/test structured editing for: milestone title, expected outcome, target date.
Remove prompt()-based date editing. Use an appropriate date control. Verify update uses existing milestone backend service.

## GROUP 4 — MARK MILESTONE COMPLETE
Replace prompt()-based status editing with explicit: MARK COMPLETE.
Tests must verify: status becomes COMPLETED, completed_at set, reminder resolved, Leaves granted once, repeated completion does not duplicate reward, progress UI refreshes.

## GROUP 5 — REMINDER REGRESSION TESTS
Add backend tests for: milestone date changed → reminder due_at updated, old reminder does not remain active incorrectly, completion → reminder resolved, repeated updates → no duplicate active reminders.

## GROUP 6 — ADJUST WITH MR. BLOOM HANDOFF
Implement/test: Goal Detail → Adjust with Mr. Bloom
Carry sufficient context: goal ID, selected milestone ID when relevant.
Mr. Bloom must load persisted Goal and roadmap context.

## GROUP 7 — EXISTING GOAL DRAFT
Extend/reuse RoadmapDraft to represent an existing Goal safely.
Preserve: Goal identity, existing milestone IDs, titles, descriptions, expected outcomes, dates, positions, status, completed_at where needed.
Do not make completed milestones editable in ways that erase execution history.

## GROUP 8 — STRUCTURAL ROADMAP EDITING
Support through Mr. Bloom: add milestone, remove pending milestone, reorder milestones, restructure remaining roadmap, replan remaining roadmap.
Do not expose these operations directly in Goal Detail.

## GROUP 9 — TRANSACTIONAL SAVE OF EXISTING ROADMAP
Implement backend/service support for saving modified existing roadmap.
Must safely handle: update existing milestone, create new milestone, remove milestone, reorder milestones, preserve completed milestone history, synchronize reminders, preserve linked relationships where required.
Must run transactionally.

## GROUP 10 — REORDER SAFETY
Add tests proving roadmap reorder does not violate `(goal_id, position)` unique constraint.
Do not use naïve one-by-one position updates if they can conflict.

## GROUP 11 — AUTHORIZATION
Add/verify tests: User A cannot edit User B Goal, User A cannot edit User B milestone, User A cannot load User B Goal into Mr. Bloom, User A cannot save structural changes to User B Goal.

## GROUP 12 — FRONTEND CLEANUP
Remove: window.prompt() handlers, generic Edit Manually handlers, dead fallback editing state, stale types, obsolete CSS, unused imports.
Do not remove backend APIs unless proven orphaned.

## GROUP 13 — MANUAL TEST UPDATE
Update Goal manual scenarios. Replace prompt-based cases with: Goal title/description structured edit, Milestone title/outcome structured edit, milestone date + reminder sync, Mark Complete, Adjust with Mr. Bloom, replan existing roadmap, completed milestone preservation.

## GROUP 14 — FINAL VERIFICATION
Run: Goal frontend tests, Mr. Bloom roadmap tests, Goal backend API/service tests, reminder tests, authorization tests, frontend check/typecheck, relevant full regression suite.
