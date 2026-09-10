-- Scope: natural-language planning conversations in the full application.
-- Widget reminder bubbles are event UI and are not stored as chat messages.

CREATE TABLE IF NOT EXISTS planning_sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type        VARCHAR(20) NOT NULL,
    status              VARCHAR(30) NOT NULL DEFAULT 'OPEN',
    context_date        DATE,
    closed_at           TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT planning_sessions_type_valid
        CHECK (session_type IN ('DAILY_PLAN', 'PLAN_EDIT', 'REPLAN', 'ROADMAP')),
    CONSTRAINT planning_sessions_status_valid
        CHECK (status IN ('OPEN', 'AWAITING_CLARIFICATION', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT planning_sessions_closed_at_valid
        CHECK (closed_at IS NULL OR closed_at >= created_at)
);

CREATE TABLE IF NOT EXISTS planning_messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    planning_session_id UUID NOT NULL
                            REFERENCES planning_sessions(id) ON DELETE CASCADE,
    role                VARCHAR(20) NOT NULL,
    content             TEXT NOT NULL,
    structured_payload  JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT planning_messages_role_valid
        CHECK (role IN ('USER', 'ASSISTANT', 'SYSTEM')),
    CONSTRAINT planning_messages_content_not_blank
        CHECK (BTRIM(content) <> ''),
    CONSTRAINT planning_messages_payload_object
        CHECK (
            structured_payload IS NULL
            OR jsonb_typeof(structured_payload) = 'object'
        )
);

