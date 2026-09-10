-- Scope: server-stored reminder definitions synchronized to Tauri for local timing.

CREATE TABLE IF NOT EXISTS reminders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    milestone_id        UUID REFERENCES milestones(id) ON DELETE CASCADE,
    plan_block_id       UUID REFERENCES plan_blocks(id) ON DELETE CASCADE,
    reminder_type       VARCHAR(30) NOT NULL,
    message             VARCHAR(300) NOT NULL,
    due_at              TIMESTAMPTZ NOT NULL,
    original_due_at     TIMESTAMPTZ NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED',
    viewed_at           TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    dismissed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT reminders_type_valid
        CHECK (reminder_type IN ('PLAN_BLOCK_START', 'MILESTONE_DUE', 'CUSTOM')),
    CONSTRAINT reminders_message_not_blank
        CHECK (BTRIM(message) <> ''),
    CONSTRAINT reminders_status_valid
        CHECK (status IN ('SCHEDULED', 'DUE', 'COMPLETED', 'DISMISSED', 'CANCELLED')),
    CONSTRAINT reminders_target_valid
        CHECK (
            (
                reminder_type = 'PLAN_BLOCK_START'
                AND plan_block_id IS NOT NULL
                AND milestone_id IS NULL
            )
            OR
            (
                reminder_type = 'MILESTONE_DUE'
                AND milestone_id IS NOT NULL
                AND plan_block_id IS NULL
            )
            OR
            (
                reminder_type = 'CUSTOM'
                AND milestone_id IS NULL
                AND plan_block_id IS NULL
            )
        ),
    CONSTRAINT reminders_completion_valid
        CHECK (
            (status = 'COMPLETED' AND completed_at IS NOT NULL)
            OR status <> 'COMPLETED'
        ),
    CONSTRAINT reminders_dismissal_valid
        CHECK (
            (status = 'DISMISSED' AND dismissed_at IS NOT NULL)
            OR status <> 'DISMISSED'
        )
);

CREATE TABLE IF NOT EXISTS reminder_actions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reminder_id         UUID NOT NULL REFERENCES reminders(id) ON DELETE CASCADE,
    action_type         VARCHAR(30) NOT NULL,
    previous_due_at     TIMESTAMPTZ,
    new_due_at          TIMESTAMPTZ,
    payload             JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT reminder_actions_type_valid
        CHECK (
            action_type IN (
                'VIEWED', 'START_FOCUS', 'REMIND_LATER', 'OPEN_BLOOMING',
                'CREATE_PLAN', 'MARK_COMPLETED', 'MOVE_MILESTONE',
                'DISMISS', 'COMPLETE'
            )
        ),
    CONSTRAINT reminder_actions_snooze_time_valid
        CHECK (
            action_type <> 'REMIND_LATER'
            OR (new_due_at IS NOT NULL AND previous_due_at IS NOT NULL AND new_due_at > previous_due_at)
        ),
    CONSTRAINT reminder_actions_payload_object
        CHECK (payload IS NULL OR jsonb_typeof(payload) = 'object')
);

