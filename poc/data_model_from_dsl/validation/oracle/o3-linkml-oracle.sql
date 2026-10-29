
CREATE TABLE "Any" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_Any_id" ON "Any" (id);
COMMENT ON TABLE "Any" IS 'Opaque JSON payload.';

CREATE TABLE "Domain" (
	domain_id INTEGER NOT NULL,
	name VARCHAR2(4096 CHAR) NOT NULL,
	timezone VARCHAR2(4096 CHAR) NOT NULL,
	odate_boundary_time TIME NOT NULL,
	projection_horizon INTEGER NOT NULL,
	heartbeat_interval INTEGER NOT NULL,
	liveness_threshold INTEGER NOT NULL,
	state VARCHAR(8 CHAR) NOT NULL,
	created_at DATE NOT NULL,
	state_changed_at DATE NOT NULL,
	updated_at DATE NOT NULL,
	PRIMARY KEY (domain_id),
	UNIQUE (name)
);
CREATE INDEX "Domain_name_idx" ON "Domain" (name);
CREATE INDEX "ix_Domain_domain_id" ON "Domain" (domain_id);
COMMENT ON TABLE "Domain" IS 'None';

CREATE TABLE "Task" (
	task_id INTEGER NOT NULL,
	domain_id INTEGER NOT NULL,
	state VARCHAR(8 CHAR) NOT NULL,
	created_at DATE NOT NULL,
	state_changed_at DATE NOT NULL,
	PRIMARY KEY (task_id),
	UNIQUE (domain_id, task_id),
	FOREIGN KEY(domain_id) REFERENCES "Domain" (domain_id)
);
CREATE INDEX "ix_Task_task_id" ON "Task" (task_id);
CREATE INDEX "Task_domain_id_task_id_idx" ON "Task" (domain_id, task_id);
COMMENT ON TABLE "Task" IS 'None';

CREATE TABLE "Folder" (
	folder_id INTEGER NOT NULL,
	domain_id INTEGER NOT NULL,
	kind VARCHAR(7 CHAR) NOT NULL,
	state VARCHAR(8 CHAR) NOT NULL,
	created_at DATE NOT NULL,
	state_changed_at DATE NOT NULL,
	PRIMARY KEY (folder_id),
	UNIQUE (domain_id, folder_id),
	UNIQUE (folder_id, kind),
	FOREIGN KEY(domain_id) REFERENCES "Domain" (domain_id)
);
CREATE INDEX "ix_Folder_folder_id" ON "Folder" (folder_id);
CREATE INDEX "Folder_folder_id_kind_idx" ON "Folder" (folder_id, kind);
CREATE INDEX "Folder_domain_id_folder_id_idx" ON "Folder" (domain_id, folder_id);
COMMENT ON TABLE "Folder" IS 'None';

CREATE TABLE "Plan" (
	plan_id INTEGER NOT NULL,
	domain_id INTEGER NOT NULL,
	odate DATE NOT NULL,
	state VARCHAR(7 CHAR) NOT NULL,
	created_at DATE NOT NULL,
	updated_at DATE NOT NULL,
	PRIMARY KEY (plan_id),
	UNIQUE (domain_id, odate),
	FOREIGN KEY(domain_id) REFERENCES "Domain" (domain_id)
);
CREATE INDEX "Plan_domain_id_odate_idx" ON "Plan" (domain_id, odate);
CREATE INDEX "ix_Plan_plan_id" ON "Plan" (plan_id);
COMMENT ON TABLE "Plan" IS 'None';

CREATE TABLE "Outbox" (
	message_id INTEGER NOT NULL,
	task_instance_id INTEGER,
	attempt_no INTEGER,
	agent_id INTEGER NOT NULL,
	message_type VARCHAR(13 CHAR) NOT NULL,
	delivery_state VARCHAR(7 CHAR) NOT NULL,
	leased_until DATE,
	created_at DATE NOT NULL,
	leased_at DATE,
	sent_at DATE,
	acked_at DATE,
	updated_at DATE NOT NULL,
	payload_id INTEGER NOT NULL,
	PRIMARY KEY (message_id),
	FOREIGN KEY(payload_id) REFERENCES "Any" (id)
);
CREATE INDEX "ix_Outbox_message_id" ON "Outbox" (message_id);
COMMENT ON TABLE "Outbox" IS 'None';

CREATE TABLE "AuditEvent" (
	audit_event_id INTEGER NOT NULL,
	event_type_id INTEGER NOT NULL,
	audited_entity_id INTEGER NOT NULL,
	entity_id INTEGER NOT NULL,
	from_state VARCHAR2(4096 CHAR),
	to_state VARCHAR2(4096 CHAR) NOT NULL,
	principal VARCHAR2(4096 CHAR) NOT NULL,
	ticket_ref VARCHAR2(4096 CHAR),
	recorded_at DATE NOT NULL,
	effective_at DATE NOT NULL,
	supersedes_event_id INTEGER,
	detail_id INTEGER,
	PRIMARY KEY (audit_event_id),
	FOREIGN KEY(supersedes_event_id) REFERENCES "AuditEvent" (audit_event_id),
	FOREIGN KEY(detail_id) REFERENCES "Any" (id)
);
CREATE INDEX "ix_AuditEvent_audit_event_id" ON "AuditEvent" (audit_event_id);
COMMENT ON TABLE "AuditEvent" IS 'None';

CREATE TABLE "TaskVersion" (
	task_version_id INTEGER NOT NULL,
	task_id INTEGER NOT NULL,
	domain_id INTEGER NOT NULL,
	folder_id INTEGER NOT NULL,
	version INTEGER NOT NULL,
	name VARCHAR2(4096 CHAR) NOT NULL,
	dispatch_target VARCHAR2(4096 CHAR),
	published_at DATE NOT NULL,
	superseded_at DATE,
	runs_from DATE NOT NULL,
	runs_until DATE,
	runs_until_set_by_folder_id INTEGER,
	created_by VARCHAR2(4096 CHAR) NOT NULL,
	identity_id INTEGER,
	scheduling_id INTEGER,
	execution_id INTEGER,
	dependencies_id INTEGER,
	event_handling_id INTEGER,
	constraints_id INTEGER,
	PRIMARY KEY (task_version_id),
	UNIQUE (task_id, version),
	FOREIGN KEY(task_id) REFERENCES "Task" (task_id),
	FOREIGN KEY(domain_id) REFERENCES "Domain" (domain_id),
	FOREIGN KEY(folder_id) REFERENCES "Folder" (folder_id),
	FOREIGN KEY(runs_until_set_by_folder_id) REFERENCES "Folder" (folder_id),
	FOREIGN KEY(identity_id) REFERENCES "Any" (id),
	FOREIGN KEY(scheduling_id) REFERENCES "Any" (id),
	FOREIGN KEY(execution_id) REFERENCES "Any" (id),
	FOREIGN KEY(dependencies_id) REFERENCES "Any" (id),
	FOREIGN KEY(event_handling_id) REFERENCES "Any" (id),
	FOREIGN KEY(constraints_id) REFERENCES "Any" (id)
);
CREATE INDEX "ix_TaskVersion_task_version_id" ON "TaskVersion" (task_version_id);
CREATE INDEX "TaskVersion_task_id_version_idx" ON "TaskVersion" (task_id, version);
COMMENT ON TABLE "TaskVersion" IS 'None';

CREATE TABLE "TaskInstance" (
	task_instance_id INTEGER NOT NULL,
	plan_id INTEGER NOT NULL,
	task_version_id INTEGER NOT NULL,
	folder_version_id INTEGER,
	state VARCHAR(7 CHAR) NOT NULL,
	result VARCHAR2(4096 CHAR),
	queued_at DATE,
	run_at DATE,
	no_run_at DATE,
	result_at DATE,
	wake_at DATE,
	wake_on VARCHAR2(4096 CHAR),
	created_at DATE NOT NULL,
	updated_at DATE NOT NULL,
	filled_values_id INTEGER NOT NULL,
	PRIMARY KEY (task_instance_id),
	FOREIGN KEY(plan_id) REFERENCES "Plan" (plan_id),
	FOREIGN KEY(task_version_id) REFERENCES "TaskVersion" (task_version_id),
	FOREIGN KEY(filled_values_id) REFERENCES "Any" (id)
);
CREATE INDEX "ix_TaskInstance_task_instance_id" ON "TaskInstance" (task_instance_id);
COMMENT ON TABLE "TaskInstance" IS 'None';

CREATE TABLE "Attempt" (
	id INTEGER NOT NULL,
	task_instance_id INTEGER NOT NULL,
	attempt_no INTEGER NOT NULL,
	agent_id INTEGER NOT NULL,
	attempt_state VARCHAR(11 CHAR) NOT NULL,
	exit_code INTEGER,
	dispatching_at DATE NOT NULL,
	dispatched_at DATE,
	running_at DATE,
	unknown_at DATE,
	finished_at DATE,
	started_at DATE,
	ended_at DATE,
	updated_at DATE NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (task_instance_id, attempt_no),
	FOREIGN KEY(task_instance_id) REFERENCES "TaskInstance" (task_instance_id)
);
CREATE INDEX "ix_Attempt_id" ON "Attempt" (id);
CREATE INDEX "Attempt_task_instance_id_attempt_no_idx" ON "Attempt" (task_instance_id, attempt_no);
COMMENT ON TABLE "Attempt" IS 'None';

