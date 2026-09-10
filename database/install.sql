\set ON_ERROR_STOP on

BEGIN;

\ir migrations/00_extensions.sql
\ir migrations/01_users_and_auth.sql
\ir migrations/02_goals_and_milestones.sql
\ir migrations/03_planning_chat.sql
\ir migrations/04_tasks_and_dependencies.sql
\ir migrations/05_daily_planning.sql
\ir migrations/06_focus.sql
\ir migrations/07_reminders.sql
\ir migrations/08_heart_and_garden.sql
\ir migrations/09_updated_at_triggers.sql
\ir migrations/10_indexes.sql

COMMIT;

\echo 'Blooming database baseline installed successfully.'

