-- Scope: keep mutable rows' updated_at values correct inside PostgreSQL.

CREATE OR REPLACE FUNCTION set_row_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS users_set_updated_at ON users;
CREATE TRIGGER users_set_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS user_settings_set_updated_at ON user_settings;
CREATE TRIGGER user_settings_set_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS auth_sessions_set_updated_at ON auth_sessions;
CREATE TRIGGER auth_sessions_set_updated_at
    BEFORE UPDATE ON auth_sessions
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS goals_set_updated_at ON goals;
CREATE TRIGGER goals_set_updated_at
    BEFORE UPDATE ON goals
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS milestones_set_updated_at ON milestones;
CREATE TRIGGER milestones_set_updated_at
    BEFORE UPDATE ON milestones
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS planning_sessions_set_updated_at ON planning_sessions;
CREATE TRIGGER planning_sessions_set_updated_at
    BEFORE UPDATE ON planning_sessions
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS tasks_set_updated_at ON tasks;
CREATE TRIGGER tasks_set_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS daily_plans_set_updated_at ON daily_plans;
CREATE TRIGGER daily_plans_set_updated_at
    BEFORE UPDATE ON daily_plans
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS availability_windows_set_updated_at ON availability_windows;
CREATE TRIGGER availability_windows_set_updated_at
    BEFORE UPDATE ON availability_windows
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS plan_blocks_set_updated_at ON plan_blocks;
CREATE TRIGGER plan_blocks_set_updated_at
    BEFORE UPDATE ON plan_blocks
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS focus_runs_set_updated_at ON focus_runs;
CREATE TRIGGER focus_runs_set_updated_at
    BEFORE UPDATE ON focus_runs
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS reminders_set_updated_at ON reminders;
CREATE TRIGGER reminders_set_updated_at
    BEFORE UPDATE ON reminders
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

DROP TRIGGER IF EXISTS garden_states_set_updated_at ON garden_states;
CREATE TRIGGER garden_states_set_updated_at
    BEFORE UPDATE ON garden_states
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();

