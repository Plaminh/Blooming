-- Scope: append-only Reward ledger, current garden projection, and catalog.

CREATE TABLE IF NOT EXISTS plants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    species         VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    description     TEXT NOT NULL,
    unlock_cost     INTEGER NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS plant_ownerships (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plant_id        UUID NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
    unlocked_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT plant_ownerships_user_plant_key UNIQUE (user_id, plant_id)
);

CREATE TABLE IF NOT EXISTS reward_events (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type              VARCHAR(40) NOT NULL,
    resource_type           VARCHAR(20) NOT NULL,
    amount                  INTEGER NOT NULL,
    idempotency_key         TEXT NOT NULL UNIQUE,
    source_focus_run_id     UUID REFERENCES focus_runs(id) ON DELETE CASCADE,
    source_task_id          UUID REFERENCES tasks(id) ON DELETE CASCADE,
    source_milestone_id     UUID REFERENCES milestones(id) ON DELETE CASCADE,
    source_plan_revision_id UUID REFERENCES plan_revisions(id) ON DELETE CASCADE,
    metadata                JSONB,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT reward_events_type_valid
        CHECK (
            event_type IN (
                'FOCUS_COMPLETED', 'TASK_COMPLETED', 'CORE_OBJECTIVE_COMPLETED',
                'MILESTONE_COMPLETED', 'RECOVERY_PLAN_COMPLETED', 'PLANT_UNLOCK', 'WATER_PLANT'
            )
        ),
    CONSTRAINT reward_events_resource_type_valid
        CHECK (
            resource_type IN ('WATER', 'LEAVES')
        ),
    CONSTRAINT reward_events_idempotency_key_not_blank
        CHECK (BTRIM(idempotency_key) <> ''),
    CONSTRAINT reward_events_max_one_source
        CHECK (
            num_nonnulls(
                source_focus_run_id,
                source_task_id,
                source_milestone_id,
                source_plan_revision_id
            ) <= 1
        ),
    CONSTRAINT reward_events_metadata_object
        CHECK (metadata IS NULL OR jsonb_typeof(metadata) = 'object')
);

CREATE TABLE IF NOT EXISTS garden_states (
    user_id             UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    water_balance       INTEGER NOT NULL DEFAULT 0,
    leaves_balance      INTEGER NOT NULL DEFAULT 0,
    selected_plant_id   UUID REFERENCES plants(id) ON DELETE SET NULL,
    last_watered_at     TIMESTAMPTZ,
    growth_points       INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT garden_states_growth_points_valid CHECK (growth_points >= 0),
    stage               VARCHAR(20) NOT NULL DEFAULT 'DORMANT',
    leaf_count          INTEGER NOT NULL DEFAULT 0,
    flower_count        INTEGER NOT NULL DEFAULT 0,
    fruit_count         INTEGER NOT NULL DEFAULT 0,
    version             INTEGER NOT NULL DEFAULT 1,
    stage_changed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT garden_states_water_valid
        CHECK (water_balance >= 0),
    CONSTRAINT garden_states_leaves_valid
        CHECK (leaves_balance >= 0),
    CONSTRAINT garden_states_stage_valid
        CHECK (stage IN ('DORMANT', 'SPROUTING', 'GROWING', 'BLOOMING', 'FRUITING')),
    CONSTRAINT garden_states_visual_counts_valid
        CHECK (leaf_count >= 0 AND flower_count >= 0 AND fruit_count >= 0),
    CONSTRAINT garden_states_version_valid
        CHECK (version >= 1)
);

-- Seed catalog data idempotently
INSERT INTO plants (species, name, description, unlock_cost)
VALUES
    ('monstera', 'Monstera Deliciosa', 'A classic houseplant with large, beautiful split leaves.', 0),
    ('sunflower', 'Sunflower', 'Bright and cheerful, turning to face the sun.', 10),
    ('bonsai', 'Bonsai Tree', 'Requires patience and care, but brings deep peace.', 20),
    ('jasmine', 'Jasmine', 'A fragrant climber that blooms in the evening.', 15),
    ('lavender', 'Lavender', 'A calming, aromatic herb with lovely purple flowers.', 15)
ON CONFLICT (species) DO NOTHING;
