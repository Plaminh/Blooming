DO $$
DECLARE
    required_table TEXT;
    required_tables TEXT[] := ARRAY[
        'plants', 'users', 'ai_usage_log', 'auth_sessions',
        'email_verification_tokens', 'garden_states', 'goals',
        'planning_sessions', 'plant_ownerships', 'user_settings',
        'daily_plans', 'milestones', 'planning_messages',
        'availability_windows', 'plan_revisions', 'recurring_tasks', 'tasks',
        'plan_blocks', 'task_dependencies', 'focus_runs', 'reminders',
        'focus_run_events', 'reminder_actions', 'reward_events'
    ];
BEGIN
    FOREACH required_table IN ARRAY required_tables LOOP
        IF to_regclass('public.' || required_table) IS NULL THEN
            RAISE EXCEPTION 'Unversioned database is not baseline-compatible: missing table %', required_table;
        END IF;
    END LOOP;

    IF NOT EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto'
    ) THEN
        RAISE EXCEPTION 'Unversioned database is not baseline-compatible: pgcrypto is missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'focus_runs'
          AND column_name = 'planned_focus_seconds'
    ) OR NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'reward_events'
          AND column_name = 'idempotency_key'
    ) THEN
        RAISE EXCEPTION 'Unversioned database is not baseline-compatible: critical columns are missing';
    END IF;
END
$$;
