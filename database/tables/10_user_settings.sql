-- Table: user_settings
CREATE TABLE user_settings (
	user_id UUID NOT NULL, 
	timezone VARCHAR(64) DEFAULT 'UTC' NOT NULL, 
	default_focus_minutes INTEGER DEFAULT 25 NOT NULL, 
	default_break_minutes INTEGER DEFAULT 5 NOT NULL, 
	reminders_enabled BOOLEAN DEFAULT TRUE NOT NULL, 
	milestone_reminder_lead_time_minutes INTEGER DEFAULT 1440 NOT NULL, 
	quiet_hours_enabled BOOLEAN DEFAULT FALSE NOT NULL, 
	quiet_hours_start TIME WITHOUT TIME ZONE, 
	quiet_hours_end TIME WITHOUT TIME ZONE, 
	widget_visibility BOOLEAN DEFAULT TRUE NOT NULL, 
	widget_always_on_top BOOLEAN DEFAULT FALSE NOT NULL, 
	launch_on_startup BOOLEAN DEFAULT FALSE NOT NULL, 
	weather_enabled BOOLEAN DEFAULT FALSE NOT NULL, 
	weather_location VARCHAR(100), 
	weather_location_name VARCHAR(255),
	weather_lat NUMERIC(5, 2),
	weather_lon NUMERIC(6, 2),
	scene_season VARCHAR(20) DEFAULT 'AUTO' NOT NULL,
	weather_animation_enabled BOOLEAN DEFAULT TRUE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (user_id), 
	CONSTRAINT user_settings_milestone_reminder_lead_time_minutes_valid CHECK (milestone_reminder_lead_time_minutes BETWEEN 0 AND 43200), 
	CONSTRAINT user_settings_focus_duration_valid CHECK (default_focus_minutes BETWEEN 1 AND 720), 
	CONSTRAINT user_settings_break_duration_valid CHECK (default_break_minutes BETWEEN 0 AND 180), 
	CONSTRAINT user_settings_quiet_hours_pair CHECK ((quiet_hours_start IS NULL AND quiet_hours_end IS NULL) OR (quiet_hours_start IS NOT NULL AND quiet_hours_end IS NOT NULL)), 
	CONSTRAINT user_settings_weather_lat_valid CHECK (weather_lat IS NULL OR weather_lat BETWEEN -90.00 AND 90.00),
	CONSTRAINT user_settings_weather_lon_valid CHECK (weather_lon IS NULL OR weather_lon BETWEEN -180.00 AND 180.00),
	CONSTRAINT user_settings_scene_season_valid CHECK (scene_season IN ('AUTO', 'SPRING', 'SUMMER', 'AUTUMN', 'WINTER')),
	CONSTRAINT user_settings_weather_coordinate_pair CHECK ((weather_lat IS NULL AND weather_lon IS NULL) OR (weather_lat IS NOT NULL AND weather_lon IS NOT NULL)),
	CONSTRAINT user_settings_weather_name_not_blank CHECK (weather_location_name IS NULL OR BTRIM(weather_location_name) <> ''),
	CONSTRAINT user_settings_weather_coordinates_named CHECK ((weather_lat IS NULL AND weather_lon IS NULL) OR (weather_location_name IS NOT NULL AND BTRIM(weather_location_name) <> '')),
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
DROP TRIGGER IF EXISTS user_settings_set_updated_at ON user_settings;
CREATE TRIGGER user_settings_set_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
