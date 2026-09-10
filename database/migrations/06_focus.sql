-- Scope: accurate Pomodoro execution independent of whether a window is visible.

CREATE TABLE IF NOT EXISTS focus_runs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id                 UUID REFERENCES tasks(id) ON DELETE CASCADE,
    plan_block_id           UUID REFERENCES plan_blocks(id) ON DELETE SET NULL,
    quick_task_title        VARCHAR(200),
    status                  VARCHAR(20) NOT NULL DEFAULT 'READY',
    outcome                 VARCHAR(30),
    planned_focus_seconds   INTEGER NOT NULL,
    planned_break_seconds   INTEGER NOT NULL DEFAULT 0,
    started_at              TIMESTAMPTZ,
    expected_end_at         TIMESTAMPTZ,
    paused_at               TIMESTAMPTZ,
    total_paused_seconds    INTEGER NOT NULL DEFAULT 0,
    ended_at                TIMESTAMPTZ,
    actual_duration_seconds INTEGER,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT focus_runs_subject_valid
        CHECK (
            task_id IS NOT NULL
            OR (quick_task_title IS NOT NULL AND BTRIM(quick_task_title) <> '')
        ),
    CONSTRAINT focus_runs_status_valid
        CHECK (status IN ('READY', 'FOCUSING', 'PAUSED', 'ENDED')),
    CONSTRAINT focus_runs_outcome_valid
        CHECK (outcome IS NULL OR outcome IN ('DONE', 'NEED_MORE_TIME', 'SKIP', 'FINISHED_EARLY')),
    CONSTRAINT focus_runs_focus_duration_valid
        CHECK (planned_focus_seconds BETWEEN 1 AND 86400),
    CONSTRAINT focus_runs_break_duration_valid
        CHECK (planned_break_seconds BETWEEN 0 AND 21600),
    CONSTRAINT focus_runs_pause_duration_valid
        CHECK (total_paused_seconds >= 0),
    CONSTRAINT focus_runs_actual_duration_valid
        CHECK (actual_duration_seconds IS NULL OR actual_duration_seconds >= 0),
    CONSTRAINT focus_runs_expected_end_valid
        CHECK (
            started_at IS NULL
            OR expected_end_at IS NULL
            OR expected_end_at >= started_at
        ),
    CONSTRAINT focus_runs_end_valid
        CHECK (
            ended_at IS NULL
            OR (started_at IS NOT NULL AND ended_at >= started_at)
        ),
    CONSTRAINT focus_runs_ended_state_valid
        CHECK (
            status <> 'ENDED'
            OR (ended_at IS NOT NULL AND actual_duration_seconds IS NOT NULL)
        )
);

CREATE TABLE IF NOT EXISTS focus_run_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    focus_run_id        UUID NOT NULL REFERENCES focus_runs(id) ON DELETE CASCADE,
    event_type          VARCHAR(30) NOT NULL,
    occurred_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload             JSONB,

    CONSTRAINT focus_run_events_type_valid
        CHECK (event_type IN ('STARTED', 'PAUSED', 'RESUMED', 'ENDED', 'OUTCOME_RECORDED')),
    CONSTRAINT focus_run_events_payload_object
        CHECK (payload IS NULL OR jsonb_typeof(payload) = 'object')
);
