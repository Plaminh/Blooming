-- Bring databases created from the older table baseline in sync with the
-- current UserSettings model. Safe to run on every development startup.

BEGIN;

ALTER TABLE user_settings
    ADD COLUMN IF NOT EXISTS weather_location_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS weather_lat NUMERIC(5, 2),
    ADD COLUMN IF NOT EXISTS weather_lon NUMERIC(6, 2),
    ADD COLUMN IF NOT EXISTS scene_season VARCHAR(20) NOT NULL DEFAULT 'AUTO';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_settings_weather_lat_valid'
          AND conrelid = 'user_settings'::regclass
    ) THEN
        ALTER TABLE user_settings
            ADD CONSTRAINT user_settings_weather_lat_valid
            CHECK (weather_lat IS NULL OR weather_lat BETWEEN -90.00 AND 90.00);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_settings_weather_lon_valid'
          AND conrelid = 'user_settings'::regclass
    ) THEN
        ALTER TABLE user_settings
            ADD CONSTRAINT user_settings_weather_lon_valid
            CHECK (weather_lon IS NULL OR weather_lon BETWEEN -180.00 AND 180.00);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_settings_scene_season_valid'
          AND conrelid = 'user_settings'::regclass
    ) THEN
        ALTER TABLE user_settings
            ADD CONSTRAINT user_settings_scene_season_valid
            CHECK (scene_season IN ('AUTO', 'SPRING', 'SUMMER', 'AUTUMN', 'WINTER'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_settings_weather_coordinate_pair'
          AND conrelid = 'user_settings'::regclass
    ) THEN
        ALTER TABLE user_settings
            ADD CONSTRAINT user_settings_weather_coordinate_pair
            CHECK ((weather_lat IS NULL AND weather_lon IS NULL)
                OR (weather_lat IS NOT NULL AND weather_lon IS NOT NULL));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_settings_weather_name_not_blank'
          AND conrelid = 'user_settings'::regclass
    ) THEN
        ALTER TABLE user_settings
            ADD CONSTRAINT user_settings_weather_name_not_blank
            CHECK (weather_location_name IS NULL OR BTRIM(weather_location_name) <> '');
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'user_settings_weather_coordinates_named'
          AND conrelid = 'user_settings'::regclass
    ) THEN
        ALTER TABLE user_settings
            ADD CONSTRAINT user_settings_weather_coordinates_named
            CHECK ((weather_lat IS NULL AND weather_lon IS NULL)
                OR (weather_location_name IS NOT NULL AND BTRIM(weather_location_name) <> ''));
    END IF;
END
$$;

COMMIT;
