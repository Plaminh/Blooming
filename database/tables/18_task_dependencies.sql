-- Table: task_dependencies
CREATE TABLE task_dependencies (
	task_id UUID NOT NULL, 
	depends_on_task_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (task_id, depends_on_task_id), 
	CONSTRAINT task_dependencies_not_self CHECK (task_id <> depends_on_task_id), 
	FOREIGN KEY(task_id) REFERENCES tasks (id) ON DELETE CASCADE, 
	FOREIGN KEY(depends_on_task_id) REFERENCES tasks (id) ON DELETE CASCADE
);
CREATE INDEX task_dependencies_prerequisite_idx ON task_dependencies (depends_on_task_id);
