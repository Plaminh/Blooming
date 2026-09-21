-- Table: plant_ownerships
CREATE TABLE plant_ownerships (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	plant_id UUID NOT NULL, 
	unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT plant_ownerships_user_plant_key UNIQUE (user_id, plant_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(plant_id) REFERENCES plants (id) ON DELETE CASCADE
);
