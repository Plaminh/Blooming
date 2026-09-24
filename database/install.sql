\set ON_ERROR_STOP on

BEGIN;

\ir 00_init.sql
\ir tables/01_plants.sql
\ir tables/02_users.sql
\ir tables/03_ai_usage_log.sql
\ir tables/04_auth_sessions.sql
\ir tables/05_email_verification_tokens.sql
\ir tables/06_garden_states.sql
\ir tables/07_goals.sql
\ir tables/08_planning_sessions.sql
\ir tables/09_plant_ownerships.sql
\ir tables/10_user_settings.sql
\ir tables/11_daily_plans.sql
\ir tables/12_milestones.sql
\ir tables/13_planning_messages.sql
\ir tables/14_availability_windows.sql
\ir tables/15_plan_revisions.sql
\ir tables/15a_recurring_tasks.sql
\ir tables/16_tasks.sql
\ir tables/17_plan_blocks.sql
\ir tables/18_task_dependencies.sql
\ir tables/19_focus_runs.sql
\ir tables/20_reminders.sql
\ir tables/21_focus_run_events.sql
\ir tables/22_reminder_actions.sql
\ir tables/23_reward_events.sql
\ir 99_seed.sql

COMMIT;

\echo 'Blooming database baseline installed successfully.'
