\set ON_ERROR_STOP on

BEGIN;

DO $$
DECLARE
    required_table TEXT;
BEGIN
    FOREACH required_table IN ARRAY ARRAY[
        'users', 'user_settings', 'auth_sessions',
        'goals', 'milestones',
        'planning_sessions', 'planning_messages',
        'tasks', 'task_dependencies',
        'daily_plans', 'availability_windows', 'plan_blocks', 'plan_revisions',
        'focus_runs', 'focus_run_events',
        'reminders', 'reminder_actions',
        'heart_events', 'garden_states'
    ]
    LOOP
        IF to_regclass('public.' || required_table) IS NULL THEN
            RAISE EXCEPTION 'Required table is missing: %', required_table;
        END IF;
    END LOOP;
END;
$$;

DO $$
DECLARE
    sample_user_id             UUID;
    sample_goal_id             UUID;
    sample_milestone_id        UUID;
    prerequisite_task_id       UUID;
    sample_task_id             UUID;
    sample_session_id          UUID;
    sample_plan_id             UUID;
    sample_block_id            UUID;
    sample_revision_id         UUID;
    sample_focus_run_id        UUID;
    sample_reminder_id         UUID;
BEGIN
    INSERT INTO users (email, password_hash, display_name)
    VALUES ('schema-test@blooming.local', 'not-a-real-password-hash', 'Schema Test')
    RETURNING id INTO sample_user_id;

    INSERT INTO user_settings (
        user_id, timezone, quiet_hours_enabled, quiet_hours_start, quiet_hours_end
    ) VALUES (
        sample_user_id, 'Asia/Ho_Chi_Minh', TRUE, TIME '22:00', TIME '07:00'
    );

    INSERT INTO auth_sessions (
        user_id, refresh_token_hash, device_name, platform, expires_at
    ) VALUES (
        sample_user_id,
        'schema-test-refresh-token-hash',
        'Test Desktop',
        'WINDOWS',
        NOW() + INTERVAL '1 day'
    );

    INSERT INTO goals (user_id, title, status, target_date)
    VALUES (sample_user_id, 'Ship Blooming MVP', 'ACTIVE', CURRENT_DATE + 30)
    RETURNING id INTO sample_goal_id;

    INSERT INTO milestones (goal_id, title, expected_outcome, position, status, due_at)
    VALUES (
        sample_goal_id,
        'Finish scheduling loop',
        'A task can be planned, focused, and repaired',
        0,
        'IN_PROGRESS',
        NOW() + INTERVAL '7 days'
    )
    RETURNING id INTO sample_milestone_id;

    INSERT INTO planning_sessions (user_id, session_type, context_date)
    VALUES (sample_user_id, 'DAILY_PLAN', CURRENT_DATE)
    RETURNING id INTO sample_session_id;

    INSERT INTO planning_messages (
        planning_session_id, role, content, structured_payload
    ) VALUES (
        sample_session_id,
        'USER',
        'Plan a focused database session.',
        '{"intent":"create_daily_plan"}'::JSONB
    );

    INSERT INTO tasks (
        user_id, title, estimated_duration_minutes, priority,
        importance, scheduling_type, source, status
    ) VALUES (
        sample_user_id,
        'Read database notes',
        25,
        'MEDIUM',
        'CORE',
        'FLEXIBLE',
        'MANUAL',
        'PENDING'
    )
    RETURNING id INTO prerequisite_task_id;

    INSERT INTO tasks (
        user_id, milestone_id, title, estimated_duration_minutes, priority,
        importance, scheduling_type, source, status
    ) VALUES (
        sample_user_id,
        sample_milestone_id,
        'Build database schema',
        50,
        'HIGH',
        'CORE',
        'FLEXIBLE',
        'MILESTONE',
        'IN_PROGRESS'
    )
    RETURNING id INTO sample_task_id;

    INSERT INTO task_dependencies (task_id, depends_on_task_id)
    VALUES (sample_task_id, prerequisite_task_id);

    INSERT INTO daily_plans (
        user_id, planning_session_id, plan_date, status,
        reality_check, timezone_snapshot, confirmed_at
    ) VALUES (
        sample_user_id,
        sample_session_id,
        CURRENT_DATE,
        'CONFIRMED',
        'COMFORTABLE',
        'Asia/Ho_Chi_Minh',
        NOW()
    )
    RETURNING id INTO sample_plan_id;

    INSERT INTO availability_windows (
        daily_plan_id, available_start_at, available_end_at
    ) VALUES (
        sample_plan_id,
        NOW(),
        NOW() + INTERVAL '3 hours'
    );

    INSERT INTO plan_blocks (
        daily_plan_id, task_id, block_type, planned_start_at,
        planned_end_at, position, status
    ) VALUES (
        sample_plan_id,
        sample_task_id,
        'TASK',
        NOW() + INTERVAL '5 minutes',
        NOW() + INTERVAL '55 minutes',
        0,
        'PLANNED'
    )
    RETURNING id INTO sample_block_id;

    INSERT INTO plan_revisions (
        daily_plan_id, revision_number, reason, trigger_type,
        generated_by, before_snapshot, after_snapshot
    ) VALUES (
        sample_plan_id,
        1,
        'Initial confirmed schedule',
        'MANUAL_EDIT',
        'USER',
        '{}'::JSONB,
        '{"blocks":1}'::JSONB
    )
    RETURNING id INTO sample_revision_id;

    INSERT INTO focus_runs (
        user_id, task_id, plan_block_id, status, outcome,
        planned_focus_seconds, planned_break_seconds,
        started_at, expected_end_at, ended_at, actual_duration_seconds
    ) VALUES (
        sample_user_id,
        sample_task_id,
        sample_block_id,
        'ENDED',
        'DONE',
        3000,
        600,
        NOW() - INTERVAL '50 minutes',
        NOW(),
        NOW(),
        3000
    )
    RETURNING id INTO sample_focus_run_id;

    INSERT INTO focus_run_events (focus_run_id, event_type, occurred_at)
    VALUES
        (sample_focus_run_id, 'STARTED', NOW() - INTERVAL '50 minutes'),
        (sample_focus_run_id, 'ENDED', NOW()),
        (sample_focus_run_id, 'OUTCOME_RECORDED', NOW());

    INSERT INTO reminders (
        user_id, plan_block_id, reminder_type, message,
        due_at, original_due_at, status, viewed_at, completed_at
    ) VALUES (
        sample_user_id,
        sample_block_id,
        'PLAN_BLOCK_START',
        'It is time to build the database schema.',
        NOW(),
        NOW(),
        'COMPLETED',
        NOW(),
        NOW()
    )
    RETURNING id INTO sample_reminder_id;

    INSERT INTO reminder_actions (reminder_id, action_type)
    VALUES (sample_reminder_id, 'COMPLETE');

    INSERT INTO heart_events (
        user_id, event_type, heart_amount, idempotency_key, source_focus_run_id
    ) VALUES (
        sample_user_id,
        'FOCUS_COMPLETED',
        10,
        'schema-test:focus-completed',
        sample_focus_run_id
    );

    INSERT INTO garden_states (
        user_id, total_heart, stage, leaf_count
    ) VALUES (
        sample_user_id, 10, 'SPROUTING', 1
    );

    IF NOT EXISTS (
        SELECT 1
        FROM reminders
        WHERE id = sample_reminder_id
          AND status = 'COMPLETED'
          AND viewed_at IS NOT NULL
    ) THEN
        RAISE EXCEPTION 'Reminder state smoke assertion failed.';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM heart_events
        WHERE user_id = sample_user_id
          AND idempotency_key = 'schema-test:focus-completed'
    ) THEN
        RAISE EXCEPTION 'Heart event smoke assertion failed.';
    END IF;

    RAISE NOTICE 'Blooming schema smoke test passed; rolling back sample data.';
END;
$$;

ROLLBACK;

