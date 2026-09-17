# Data model

All changes edit existing authoritative SQL definitions directly. No new Alembic feature revision; baseline `6ebc3e7e2e0e` remains untouched.

| Table / source file | Added column | Constraint |
| --- | --- | --- |
| tasks / 04_tasks_and_dependencies.sql | category VARCHAR(50) NULL | NULL or Learning, Work, Personal |
| garden_states / 08_heart_and_garden.sql | growth_points INTEGER NOT NULL DEFAULT 0 | growth_points >= 0 |
| user_settings / 01_users_and_auth.sql | milestone_reminder_lead_time_minutes INTEGER NOT NULL DEFAULT 1440 | BETWEEN 0 AND 43200 |

SQLAlchemy and Pydantic mirror these contracts. Historical/unspecified category remains NULL; Uncategorized is only a presentation label. Explicit null clears category and description.

`growth_stage` is a response-only value: SPROUTING 0-99, GROWING 100-299, BLOOMING 300-699, FLOURISHING 700+. Legacy persisted stage and visual-count columns are untouched. Growth is cumulative, awarded alongside the eligible Leaves event with its original completion idempotency key; it never has its own reward event or currency.

Milestone reminders retain the actual deadline in `original_due_at`. Delivery `due_at` equals deadline minus the configured lead time, including zero. Existing reminder rows are synchronized without creating duplicate active reminders. Quiet-hours suppression does not alter status. Existing acknowledged reminders remain acknowledged.

No heart, reward, plant, ownership or unrelated garden tables/columns are dropped or recreated. The SQL tree already uses reward_events and balances; the older Alembic baseline and historical SQL smoke test still reference heart_events. That pre-existing mismatch is outside this additive correction.

Existing local databases require a manual schema update or recreation. No automatic volume deletion is performed.
