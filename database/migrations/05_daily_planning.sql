-- Scope: a user's confirmed daily schedule and its revision history.

CREATE TABLE IF NOT EXISTS daily_plans (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    planning_session_id     UUID REFERENCES planning_sessions(id) ON DELETE SET NULL,
    plan_date               DATE NOT NULL,
    status                  VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    reality_check           VARCHAR(20),
    timezone_snapshot       VARCHAR(64) NOT NULL,
    confirmed_at            TIMESTAMPTZ,
    completed_at            TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT daily_plans_status_valid
        CHECK (status IN ('DRAFT', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'ARCHIVED')),
    CONSTRAINT daily_plans_reality_check_valid
        CHECK (reality_check IS NULL OR reality_check IN ('COMFORTABLE', 'TIGHT', 'OVERLOADED')),
    CONSTRAINT daily_plans_timezone_not_blank
        CHECK (BTRIM(timezone_snapshot) <> ''),
    CONSTRAINT daily_plans_confirmation_valid
        CHECK (
            status = 'DRAFT'
            OR confirmed_at IS NOT NULL
        ),
    CONSTRAINT daily_plans_completion_valid
        CHECK (
            (status = 'COMPLETED' AND completed_at IS NOT NULL)
            OR
            (status <> 'COMPLETED')
        ),
    CONSTRAINT daily_plans_one_per_local_date
        UNIQUE (user_id, plan_date)
);

CREATE TABLE IF NOT EXISTS availability_windows (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_plan_id       UUID NOT NULL REFERENCES daily_plans(id) ON DELETE CASCADE,
    available_start_at  TIMESTAMPTZ NOT NULL,
    available_end_at    TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT availability_windows_range_valid
        CHECK (available_end_at > available_start_at),
    CONSTRAINT availability_windows_unique
        UNIQUE (daily_plan_id, available_start_at, available_end_at)
);

CREATE TABLE IF NOT EXISTS plan_blocks (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_plan_id       UUID NOT NULL REFERENCES daily_plans(id) ON DELETE CASCADE,
    task_id             UUID REFERENCES tasks(id) ON DELETE CASCADE,
    block_type          VARCHAR(20) NOT NULL,
    title               VARCHAR(200),
    planned_start_at    TIMESTAMPTZ NOT NULL,
    planned_end_at      TIMESTAMPTZ NOT NULL,
    position            INTEGER NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'PLANNED',
    is_locked           BOOLEAN NOT NULL DEFAULT FALSE,
    created_by          VARCHAR(20) NOT NULL DEFAULT 'SCHEDULER',
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT plan_blocks_type_valid
        CHECK (block_type IN ('TASK', 'BREAK', 'BUFFER', 'FIXED_EVENT')),
    CONSTRAINT plan_blocks_range_valid
        CHECK (planned_end_at > planned_start_at),
    CONSTRAINT plan_blocks_position_valid
        CHECK (position >= 0),
    CONSTRAINT plan_blocks_status_valid
        CHECK (status IN ('PLANNED', 'ACTIVE', 'COMPLETED', 'SKIPPED', 'CANCELLED')),
    CONSTRAINT plan_blocks_creator_valid
        CHECK (created_by IN ('SCHEDULER', 'USER')),
    CONSTRAINT plan_blocks_task_link_valid
        CHECK (
            (block_type = 'TASK' AND task_id IS NOT NULL)
            OR
            (block_type <> 'TASK' AND task_id IS NULL)
        ),
    CONSTRAINT plan_blocks_non_task_title
        CHECK (block_type = 'TASK' OR (title IS NOT NULL AND BTRIM(title) <> '')),
    CONSTRAINT plan_blocks_completion_valid
        CHECK (
            (status = 'COMPLETED' AND completed_at IS NOT NULL)
            OR
            (status <> 'COMPLETED')
        ),
    CONSTRAINT plan_blocks_position_unique
        UNIQUE (daily_plan_id, position)
);

CREATE TABLE IF NOT EXISTS plan_revisions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    daily_plan_id       UUID NOT NULL REFERENCES daily_plans(id) ON DELETE CASCADE,
    revision_number     INTEGER NOT NULL,
    reason              TEXT NOT NULL,
    trigger_type        VARCHAR(30) NOT NULL,
    generated_by        VARCHAR(20) NOT NULL,
    before_snapshot     JSONB NOT NULL,
    after_snapshot      JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT plan_revisions_number_valid
        CHECK (revision_number >= 1),
    CONSTRAINT plan_revisions_reason_not_blank
        CHECK (BTRIM(reason) <> ''),
    CONSTRAINT plan_revisions_trigger_valid
        CHECK (trigger_type IN ('MANUAL_EDIT', 'DELAY', 'NEED_MORE_TIME', 'SKIP', 'CONFLICT', 'RECOVERY')),
    CONSTRAINT plan_revisions_generated_by_valid
        CHECK (generated_by IN ('USER', 'SYSTEM', 'AI')),
    CONSTRAINT plan_revisions_before_object
        CHECK (jsonb_typeof(before_snapshot) = 'object'),
    CONSTRAINT plan_revisions_after_object
        CHECK (jsonb_typeof(after_snapshot) = 'object'),
    CONSTRAINT plan_revisions_number_unique
        UNIQUE (daily_plan_id, revision_number)
);
