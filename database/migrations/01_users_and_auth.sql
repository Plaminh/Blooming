-- Scope: user identity, account-wide preferences, and revocable login sessions.
-- Device-only window/widget preferences remain in Tauri's local store.

CREATE TABLE IF NOT EXISTS users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email               VARCHAR(320) NOT NULL,
    password_hash       TEXT NOT NULL,
    display_name        VARCHAR(100),
    account_status      VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    last_login_at       TIMESTAMPTZ,
    email_verified_at   TIMESTAMPTZ NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT users_email_not_blank
        CHECK (BTRIM(email) <> ''),
    CONSTRAINT users_account_status_valid
        CHECK (account_status IN ('ACTIVE', 'DISABLED'))
);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id                         UUID PRIMARY KEY
                                        REFERENCES users(id) ON DELETE CASCADE,
    timezone                        VARCHAR(64) NOT NULL DEFAULT 'UTC',
    default_focus_minutes           INTEGER NOT NULL DEFAULT 25,
    default_break_minutes           INTEGER NOT NULL DEFAULT 5,
    reminders_enabled               BOOLEAN NOT NULL DEFAULT TRUE,
    milestone_reminder_lead_time_minutes INTEGER NOT NULL DEFAULT 1440,
    CONSTRAINT user_settings_milestone_reminder_lead_time_minutes_valid
        CHECK (milestone_reminder_lead_time_minutes BETWEEN 0 AND 43200),
    quiet_hours_enabled             BOOLEAN NOT NULL DEFAULT FALSE,
    quiet_hours_start               TIME,
    quiet_hours_end                 TIME,
    mr_bloom_display_name           VARCHAR(60) NOT NULL DEFAULT 'Mr. Bloom',
    widget_visibility               BOOLEAN NOT NULL DEFAULT TRUE,
    widget_always_on_top            BOOLEAN NOT NULL DEFAULT FALSE,
    launch_on_startup               BOOLEAN NOT NULL DEFAULT FALSE,
    weather_enabled                 BOOLEAN NOT NULL DEFAULT FALSE,
    weather_location                VARCHAR(100),
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT user_settings_focus_duration_valid
        CHECK (default_focus_minutes BETWEEN 1 AND 720),
    CONSTRAINT user_settings_break_duration_valid
        CHECK (default_break_minutes BETWEEN 0 AND 180),
    CONSTRAINT user_settings_quiet_hours_pair
        CHECK (
            (quiet_hours_start IS NULL AND quiet_hours_end IS NULL)
            OR
            (quiet_hours_start IS NOT NULL AND quiet_hours_end IS NOT NULL)
        ),
    CONSTRAINT user_settings_mr_bloom_name_not_blank
        CHECK (BTRIM(mr_bloom_display_name) <> '')
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash  TEXT NOT NULL UNIQUE,
    device_name         VARCHAR(120),
    platform            VARCHAR(20),
    expires_at          TIMESTAMPTZ NOT NULL,
    last_used_at        TIMESTAMPTZ,
    revoked_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT auth_sessions_platform_valid
        CHECK (platform IS NULL OR platform IN ('WINDOWS', 'LINUX', 'OTHER')),
    CONSTRAINT auth_sessions_expiry_valid
        CHECK (expires_at > created_at),
    CONSTRAINT auth_sessions_revocation_valid
        CHECK (revoked_at IS NULL OR revoked_at >= created_at)
);

CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash          VARCHAR(64) UNIQUE NOT NULL,
    expires_at          TIMESTAMPTZ NOT NULL,
    used_at             TIMESTAMPTZ NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT email_verification_tokens_expiry_valid
        CHECK (expires_at > created_at)
);

CREATE INDEX IF NOT EXISTS email_verification_tokens_user_active_idx 
    ON email_verification_tokens(user_id, expires_at) 
    WHERE used_at IS NULL;
