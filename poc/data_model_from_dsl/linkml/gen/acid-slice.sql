CREATE TYPE "DomainState" AS ENUM ('DRAFT', 'ACTIVE', 'INACTIVE', 'RETIRED');
CREATE TYPE "TaskState" AS ENUM ('ACTIVE', 'INACTIVE', 'RETIRED');
CREATE TYPE "FolderKind" AS ENUM ('ROOT', 'REGULAR', 'SMART');
CREATE TYPE "FolderState" AS ENUM ('ACTIVE', 'INACTIVE', 'RETIRED');
CREATE TYPE "PlanState" AS ENUM ('PENDING', 'OPEN', 'CLOSED');
CREATE TYPE "TaskInstanceState" AS ENUM ('WAITING', 'QUEUED', 'RUN', 'NO_RUN');
CREATE TYPE "AttemptState" AS ENUM ('DISPATCHING', 'DISPATCHED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'UNKNOWN');
CREATE TYPE "OutboxMessageType" AS ENUM ('COMMAND', 'COMMAND_OFFER', 'CONTROL');
CREATE TYPE "OutboxDeliveryState" AS ENUM ('PENDING', 'LEASED', 'SENT', 'ACKED');

CREATE TABLE "Any" (
	id SERIAL NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_Any_id" ON "Any" (id);
COMMENT ON TABLE "Any" IS 'Opaque JSON payload.';

CREATE TABLE "Domain" (
	domain_id SERIAL NOT NULL,
	name TEXT NOT NULL,
	timezone TEXT NOT NULL,
	odate_boundary_time TIME WITHOUT TIME ZONE NOT NULL,
	projection_horizon INTEGER NOT NULL,
	heartbeat_interval INTEGER NOT NULL,
	liveness_threshold INTEGER NOT NULL,
	state "DomainState" NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	state_changed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (domain_id),
	UNIQUE (name)
);
CREATE INDEX "Domain_name_idx" ON "Domain" (name);
CREATE INDEX "ix_Domain_domain_id" ON "Domain" (domain_id);
COMMENT ON TABLE "Domain" IS 'None';

CREATE TABLE "Task" (
	task_id SERIAL NOT NULL,
	domain_id INTEGER NOT NULL,
	state "TaskState" NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	state_changed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (task_id),
	UNIQUE (domain_id, task_id),
	FOREIGN KEY(domain_id) REFERENCES "Domain" (domain_id)
);
CREATE INDEX "ix_Task_task_id" ON "Task" (task_id);
CREATE INDEX "Task_domain_id_task_id_idx" ON "Task" (domain_id, task_id);
COMMENT ON TABLE "Task" IS 'None';

CREATE TABLE "Folder" (
	folder_id SERIAL NOT NULL,
	domain_id INTEGER NOT NULL,
	kind "FolderKind" NOT NULL,
	state "FolderState" NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	state_changed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (folder_id),
	UNIQUE (domain_id, folder_id),
	UNIQUE (folder_id, kind),
	FOREIGN KEY(domain_id) REFERENCES "Domain" (domain_id)
);
CREATE INDEX "Folder_folder_id_kind_idx" ON "Folder" (folder_id, kind);
CREATE INDEX "ix_Folder_folder_id" ON "Folder" (folder_id);
CREATE INDEX "Folder_domain_id_folder_id_idx" ON "Folder" (domain_id, folder_id);
COMMENT ON TABLE "Folder" IS 'None';

CREATE TABLE "Plan" (
	plan_id SERIAL NOT NULL,
	domain_id INTEGER NOT NULL,
	odate DATE NOT NULL,
	state "PlanState" NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (plan_id),
	UNIQUE (domain_id, odate),
	FOREIGN KEY(domain_id) REFERENCES "Domain" (domain_id)
);
CREATE INDEX "Plan_domain_id_odate_idx" ON "Plan" (domain_id, odate);
CREATE INDEX "ix_Plan_plan_id" ON "Plan" (plan_id);
COMMENT ON TABLE "Plan" IS 'None';

CREATE TABLE "Outbox" (
	message_id SERIAL NOT NULL,
	task_instance_id INTEGER,
	attempt_no INTEGER,
	agent_id INTEGER NOT NULL,
	message_type "OutboxMessageType" NOT NULL,
	delivery_state "OutboxDeliveryState" NOT NULL,
	leased_until TIMESTAMP WITHOUT TIME ZONE,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	leased_at TIMESTAMP WITHOUT TIME ZONE,
	sent_at TIMESTAMP WITHOUT TIME ZONE,
	acked_at TIMESTAMP WITHOUT TIME ZONE,
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	payload_id INTEGER NOT NULL,
	PRIMARY KEY (message_id),
	FOREIGN KEY(payload_id) REFERENCES "Any" (id)
);
CREATE INDEX "ix_Outbox_message_id" ON "Outbox" (message_id);
COMMENT ON TABLE "Outbox" IS 'None';

CREATE TABLE "AuditEvent" (
	audit_event_id SERIAL NOT NULL,
	event_type_id INTEGER NOT NULL,
	audited_entity_id INTEGER NOT NULL,
	entity_id INTEGER NOT NULL,
	from_state TEXT,
	to_state TEXT NOT NULL,
	principal TEXT NOT NULL,
	ticket_ref TEXT,
	recorded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	effective_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	supersedes_event_id INTEGER,
	detail_id INTEGER,
	PRIMARY KEY (audit_event_id),
	FOREIGN KEY(supersedes_event_id) REFERENCES "AuditEvent" (audit_event_id),
	FOREIGN KEY(detail_id) REFERENCES "Any" (id)
);
CREATE INDEX "ix_AuditEvent_audit_event_id" ON "AuditEvent" (audit_event_id);
COMMENT ON TABLE "AuditEvent" IS 'None';

CREATE TABLE "TaskVersion" (
	task_version_id SERIAL NOT NULL,
	task_id INTEGER NOT NULL,
	domain_id INTEGER NOT NULL,
	folder_id INTEGER NOT NULL,
	version INTEGER NOT NULL,
	name TEXT NOT NULL,
	dispatch_target TEXT,
	published_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	superseded_at TIMESTAMP WITHOUT TIME ZONE,
	runs_from DATE NOT NULL,
	runs_until DATE,
	runs_until_set_by_folder_id INTEGER,
	created_by TEXT NOT NULL,
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
	task_instance_id SERIAL NOT NULL,
	plan_id INTEGER NOT NULL,
	task_version_id INTEGER NOT NULL,
	folder_version_id INTEGER,
	state "TaskInstanceState" NOT NULL,
	result TEXT,
	queued_at TIMESTAMP WITHOUT TIME ZONE,
	run_at TIMESTAMP WITHOUT TIME ZONE,
	no_run_at TIMESTAMP WITHOUT TIME ZONE,
	result_at TIMESTAMP WITHOUT TIME ZONE,
	wake_at TIMESTAMP WITHOUT TIME ZONE,
	wake_on TEXT,
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	filled_values_id INTEGER NOT NULL,
	PRIMARY KEY (task_instance_id),
	FOREIGN KEY(plan_id) REFERENCES "Plan" (plan_id),
	FOREIGN KEY(task_version_id) REFERENCES "TaskVersion" (task_version_id),
	FOREIGN KEY(filled_values_id) REFERENCES "Any" (id)
);
CREATE INDEX "ix_TaskInstance_task_instance_id" ON "TaskInstance" (task_instance_id);
COMMENT ON TABLE "TaskInstance" IS 'None';

CREATE TABLE "Attempt" (
	id SERIAL NOT NULL,
	task_instance_id INTEGER NOT NULL,
	attempt_no INTEGER NOT NULL,
	agent_id INTEGER NOT NULL,
	attempt_state "AttemptState" NOT NULL,
	exit_code INTEGER,
	dispatching_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	dispatched_at TIMESTAMP WITHOUT TIME ZONE,
	running_at TIMESTAMP WITHOUT TIME ZONE,
	unknown_at TIMESTAMP WITHOUT TIME ZONE,
	finished_at TIMESTAMP WITHOUT TIME ZONE,
	started_at TIMESTAMP WITHOUT TIME ZONE,
	ended_at TIMESTAMP WITHOUT TIME ZONE,
	updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (task_instance_id, attempt_no),
	FOREIGN KEY(task_instance_id) REFERENCES "TaskInstance" (task_instance_id)
);
CREATE INDEX "Attempt_task_instance_id_attempt_no_idx" ON "Attempt" (task_instance_id, attempt_no);
CREATE INDEX "ix_Attempt_id" ON "Attempt" (id);
COMMENT ON TABLE "Attempt" IS 'None';

