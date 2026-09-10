-- Scope: append-only Heart Progress ledger and current garden projection.

CREATE TABLE IF NOT EXISTS heart_events (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type              VARCHAR(40) NOT NULL,
    heart_amount            INTEGER NOT NULL,
    idempotency_key         TEXT NOT NULL UNIQUE,
    source_focus_run_id     UUID REFERENCES focus_runs(id) ON DELETE CASCADE,
    source_task_id          UUID REFERENCES tasks(id) ON DELETE CASCADE,
    source_milestone_id     UUID REFERENCES milestones(id) ON DELETE CASCADE,
    source_plan_revision_id UUID REFERENCES plan_revisions(id) ON DELETE CASCADE,
    metadata                JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT heart_events_type_valid
        CHECK (
            event_type IN (
                'FOCUS_COMPLETED', 'TASK_COMPLETED', 'CORE_OBJECTIVE_COMPLETED',
                'MILESTONE_COMPLETED', 'RECOVERY_PLAN_COMPLETED'
            )
        ),
    CONSTRAINT heart_events_amount_valid
        CHECK (heart_amount > 0),
    CONSTRAINT heart_events_idempotency_key_not_blank
        CHECK (BTRIM(idempotency_key) <> ''),
    CONSTRAINT heart_events_exactly_one_source
        CHECK (
            num_nonnulls(
                source_focus_run_id,
                source_task_id,
                source_milestone_id,
                source_plan_revision_id
            ) = 1
        ),
    CONSTRAINT heart_events_source_matches_type
        CHECK (
            (event_type = 'FOCUS_COMPLETED' AND source_focus_run_id IS NOT NULL)
            OR
            (event_type IN ('TASK_COMPLETED', 'CORE_OBJECTIVE_COMPLETED') AND source_task_id IS NOT NULL)
            OR
            (event_type = 'MILESTONE_COMPLETED' AND source_milestone_id IS NOT NULL)
            OR
            (event_type = 'RECOVERY_PLAN_COMPLETED' AND source_plan_revision_id IS NOT NULL)
        ),
    CONSTRAINT heart_events_metadata_object
        CHECK (metadata IS NULL OR jsonb_typeof(metadata) = 'object')
);

CREATE TABLE IF NOT EXISTS garden_states (
    user_id             UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_heart         INTEGER NOT NULL DEFAULT 0,
    stage               VARCHAR(20) NOT NULL DEFAULT 'DORMANT',
    leaf_count          INTEGER NOT NULL DEFAULT 0,
    flower_count        INTEGER NOT NULL DEFAULT 0,
    fruit_count         INTEGER NOT NULL DEFAULT 0,
    version             INTEGER NOT NULL DEFAULT 1,
    stage_changed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT garden_states_total_valid
        CHECK (total_heart >= 0),
    CONSTRAINT garden_states_stage_valid
        CHECK (stage IN ('DORMANT', 'SPROUTING', 'GROWING', 'BLOOMING', 'FRUITING')),
    CONSTRAINT garden_states_visual_counts_valid
        CHECK (leaf_count >= 0 AND flower_count >= 0 AND fruit_count >= 0),
    CONSTRAINT garden_states_version_valid
        CHECK (version >= 1)
);
