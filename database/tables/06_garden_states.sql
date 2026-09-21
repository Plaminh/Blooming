-- Table: garden_states
CREATE TABLE garden_states (
	user_id UUID NOT NULL, 
	water_balance INTEGER DEFAULT 0 NOT NULL, 
	leaves_balance INTEGER DEFAULT 0 NOT NULL, 
	selected_plant_id UUID, 
	growth_points INTEGER DEFAULT 0 NOT NULL, 
	last_watered_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (user_id), 
	CONSTRAINT garden_states_water_valid CHECK (water_balance >= 0), 
	CONSTRAINT garden_states_leaves_valid CHECK (leaves_balance >= 0), 
	CONSTRAINT garden_states_growth_points_valid CHECK (growth_points >= 0), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(selected_plant_id) REFERENCES plants (id) ON DELETE SET NULL
);
DROP TRIGGER IF EXISTS garden_states_set_updated_at ON garden_states;
CREATE TRIGGER garden_states_set_updated_at
    BEFORE UPDATE ON garden_states
    FOR EACH ROW EXECUTE FUNCTION set_row_updated_at();
