-- Scope: long-term direction. A goal and its ordered milestones form a roadmap.

CREATE TABLE IF NOT EXISTS goals (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title               VARCHAR(200) NOT NULL,
    description         TEXT,
    roadmap_summary     TEXT,
    target_date         DATE,
    status              VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT goals_title_not_blank
        CHECK (BTRIM(title) <> ''),
    CONSTRAINT goals_status_valid
        CHECK (status IN ('DRAFT', 'ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT goals_completion_valid
        CHECK (
            (status = 'COMPLETED' AND completed_at IS NOT NULL)
            OR
            (status <> 'COMPLETED')
        )
);

CREATE TABLE IF NOT EXISTS milestones (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id             UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    title               VARCHAR(200) NOT NULL,
    description         TEXT,
    expected_outcome    TEXT,
    due_at              TIMESTAMPTZ,
    position            INTEGER NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT milestones_title_not_blank
        CHECK (BTRIM(title) <> ''),
    CONSTRAINT milestones_position_valid
        CHECK (position >= 0),
    CONSTRAINT milestones_status_valid
        CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED', 'CANCELLED')),
    CONSTRAINT milestones_completion_valid
        CHECK (
            (status = 'COMPLETED' AND completed_at IS NOT NULL)
            OR
            (status <> 'COMPLETED')
        ),
    CONSTRAINT milestones_goal_position_unique
        UNIQUE (goal_id, position)
);
