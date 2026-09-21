-- Table: plants
CREATE TABLE plants (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	species VARCHAR(50) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT NOT NULL, 
	unlock_cost INTEGER NOT NULL, 
	is_active BOOLEAN DEFAULT TRUE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (species)
);

