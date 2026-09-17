-- Scope: intended work before it is placed onto a concrete timeline.

CREATE TABLE IF NOT EXISTS tasks (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    milestone_id                UUID REFERENCES milestones(id) ON DELETE SET NULL,
    title                       VARCHAR(200) NOT NULL,
    description                 TEXT,
    category                    VARCHAR(50) NULL,
    CONSTRAINT tasks_category_valid
        CHECK (category IS NULL OR category IN ('Learning', 'Work', 'Personal')),
    estimated_duration_minutes  INTEGER NOT NULL,
    priority                    VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    importance                  VARCHAR(20) NOT NULL DEFAULT 'CORE',
    scheduling_type             VARCHAR(20) NOT NULL DEFAULT 'FLEXIBLE',
    source                      VARCHAR(20) NOT NULL DEFAULT 'MANUAL',
    status                      VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    deadline_at                 TIMESTAMPTZ,
    is_splittable               BOOLEAN NOT NULL DEFAULT FALSE,
    min_split_duration_minutes  INTEGER NULL,
    preferred_break_duration_minutes INTEGER NULL,
    fixed_start_at              TIMESTAMPTZ,
    fixed_end_at                TIMESTAMPTZ,
    completed_at                TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT tasks_title_not_blank
        CHECK (BTRIM(title) <> ''),
    CONSTRAINT tasks_duration_valid
        CHECK (estimated_duration_minutes BETWEEN 1 AND 10080),
    CONSTRAINT tasks_priority_valid
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
    CONSTRAINT tasks_importance_valid
        CHECK (importance IN ('CORE', 'OPTIONAL')),
    CONSTRAINT tasks_scheduling_type_valid
        CHECK (scheduling_type IN ('FLEXIBLE', 'FIXED')),
    CONSTRAINT tasks_source_valid
        CHECK (source IN ('MANUAL', 'AI', 'MILESTONE', 'QUICK')),
    CONSTRAINT tasks_status_valid
        CHECK (status IN ('DRAFT', 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED')),
    CONSTRAINT tasks_scheduling_window_valid
        CHECK (
            (
                scheduling_type = 'FIXED'
                AND fixed_start_at IS NOT NULL
                AND fixed_end_at IS NOT NULL
                AND fixed_end_at > fixed_start_at
            )
            OR
            (
                scheduling_type = 'FLEXIBLE'
                AND fixed_start_at IS NULL
                AND fixed_end_at IS NULL
            )
        ),
    CONSTRAINT tasks_completion_valid
        CHECK (
            (status = 'COMPLETED' AND completed_at IS NOT NULL)
            OR
            (status <> 'COMPLETED')
        ),
    CONSTRAINT tasks_min_split_duration_valid
        CHECK (min_split_duration_minutes IS NULL OR min_split_duration_minutes > 0),
    CONSTRAINT tasks_preferred_break_duration_valid
        CHECK (preferred_break_duration_minutes IS NULL OR preferred_break_duration_minutes > 0),
    CONSTRAINT tasks_min_split_duration_limit
        CHECK (min_split_duration_minutes IS NULL OR min_split_duration_minutes <= estimated_duration_minutes)
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id             UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on_task_id  UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (task_id, depends_on_task_id),
    CONSTRAINT task_dependencies_not_self
        CHECK (task_id <> depends_on_task_id)
);
