-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: Oracle
-- Generated at: 2026-10-29T20:12:56.748Z

CREATE TABLE "domain" (
  "domain_id" NUMBER(19) NOT NULL,
  "name" VARCHAR2(4000) NOT NULL,
  "timezone" VARCHAR2(4000) NOT NULL,
  "odate_boundary_time" VARCHAR2(8) NOT NULL,
  "projection_horizon" NUMBER(10) NOT NULL,
  "heartbeat_interval" NUMBER(10) NOT NULL,
  "liveness_threshold" NUMBER(10) NOT NULL,
  "state" nvarchar2(255) CHECK ("state" IN ('DRAFT', 'ACTIVE', 'INACTIVE', 'RETIRED')) NOT NULL,
  "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "state_changed_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  PRIMARY KEY ("domain_id")
);

CREATE TABLE "task" (
  "task_id" NUMBER(19) NOT NULL,
  "domain_id" NUMBER(19) NOT NULL,
  "state" nvarchar2(255) CHECK ("state" IN ('ACTIVE', 'INACTIVE', 'RETIRED')) NOT NULL,
  "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "state_changed_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  PRIMARY KEY ("task_id")
);

CREATE TABLE "folder" (
  "folder_id" NUMBER(19) NOT NULL,
  "domain_id" NUMBER(19) NOT NULL,
  "kind" nvarchar2(255) CHECK ("kind" IN ('ROOT', 'REGULAR', 'SMART')) NOT NULL,
  "state" nvarchar2(255) CHECK ("state" IN ('ACTIVE', 'INACTIVE', 'RETIRED')) NOT NULL,
  "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "state_changed_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  CONSTRAINT "ck_folder_state" CHECK (kind = 'SMART' OR state = 'ACTIVE'),
  PRIMARY KEY ("folder_id")
);

CREATE TABLE "task_version" (
  "task_version_id" NUMBER(19) NOT NULL,
  "task_id" NUMBER(19) NOT NULL,
  "domain_id" NUMBER(19) NOT NULL,
  "folder_id" NUMBER(19) NOT NULL,
  "version" NUMBER(10) NOT NULL,
  "name" VARCHAR2(4000) NOT NULL,
  "dispatch_target" VARCHAR2(4000),
  "identity" CLOB,
  "scheduling" CLOB,
  "execution" CLOB,
  "dependencies" CLOB,
  "event_handling" CLOB,
  "constraints" CLOB,
  "published_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "superseded_at" TIMESTAMP WITH TIME ZONE,
  "runs_from" date NOT NULL,
  "runs_until" date,
  "runs_until_set_by_folder_id" NUMBER(19),
  "created_by" VARCHAR2(4000) NOT NULL,
  CONSTRAINT "ck_task_version_range" CHECK (runs_until IS NULL OR runs_until >= runs_from),
  PRIMARY KEY ("task_version_id")
);

CREATE TABLE "plan" (
  "plan_id" NUMBER(19) NOT NULL,
  "domain_id" NUMBER(19) NOT NULL,
  "odate" date NOT NULL,
  "state" nvarchar2(255) CHECK ("state" IN ('PENDING', 'OPEN', 'CLOSED')) NOT NULL,
  "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  PRIMARY KEY ("plan_id")
);

CREATE TABLE "task_instance" (
  "task_instance_id" NUMBER(19) NOT NULL,
  "plan_id" NUMBER(19) NOT NULL,
  "task_version_id" NUMBER(19) NOT NULL,
  "folder_version_id" NUMBER(19),
  "filled_values" CLOB NOT NULL,
  "state" nvarchar2(255) CHECK ("state" IN ('WAITING', 'QUEUED', 'RUN', 'NO_RUN')) NOT NULL,
  "result" VARCHAR2(4000),
  "queued_at" TIMESTAMP WITH TIME ZONE,
  "run_at" TIMESTAMP WITH TIME ZONE,
  "no_run_at" TIMESTAMP WITH TIME ZONE,
  "result_at" TIMESTAMP WITH TIME ZONE,
  "wake_at" TIMESTAMP WITH TIME ZONE,
  "wake_on" VARCHAR2(4000),
  "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  PRIMARY KEY ("task_instance_id")
);

CREATE TABLE "attempt" (
  "task_instance_id" NUMBER(19) NOT NULL,
  "attempt_no" NUMBER(10) NOT NULL,
  "agent_id" NUMBER(19) NOT NULL,
  "attempt_state" nvarchar2(255) CHECK ("attempt_state" IN ('DISPATCHING', 'DISPATCHED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'UNKNOWN')) NOT NULL,
  "exit_code" NUMBER(10),
  "dispatching_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "dispatched_at" TIMESTAMP WITH TIME ZONE,
  "running_at" TIMESTAMP WITH TIME ZONE,
  "unknown_at" TIMESTAMP WITH TIME ZONE,
  "finished_at" TIMESTAMP WITH TIME ZONE,
  "started_at" TIMESTAMP WITH TIME ZONE,
  "ended_at" TIMESTAMP WITH TIME ZONE,
  "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  PRIMARY KEY ("task_instance_id", "attempt_no")
);

CREATE TABLE "outbox" (
  "message_id" NUMBER(19) NOT NULL,
  "task_instance_id" NUMBER(19),
  "attempt_no" NUMBER(10),
  "agent_id" NUMBER(19) NOT NULL,
  "message_type" nvarchar2(255) CHECK ("message_type" IN ('COMMAND', 'COMMAND_OFFER', 'CONTROL')) NOT NULL,
  "payload" CLOB NOT NULL,
  "delivery_state" nvarchar2(255) CHECK ("delivery_state" IN ('PENDING', 'LEASED', 'SENT', 'ACKED')) NOT NULL,
  "leased_until" TIMESTAMP WITH TIME ZONE,
  "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "leased_at" TIMESTAMP WITH TIME ZONE,
  "sent_at" TIMESTAMP WITH TIME ZONE,
  "acked_at" TIMESTAMP WITH TIME ZONE,
  "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  CONSTRAINT "ck_outbox_attempt" CHECK ((message_type = 'COMMAND') = (task_instance_id IS NOT NULL) AND (task_instance_id IS NULL) = (attempt_no IS NULL)),
  PRIMARY KEY ("message_id")
);

CREATE TABLE "audit_event" (
  "audit_event_id" NUMBER(19) NOT NULL,
  "event_type_id" NUMBER(5) NOT NULL,
  "audited_entity_id" NUMBER(5) NOT NULL,
  "entity_id" NUMBER(19) NOT NULL,
  "from_state" VARCHAR2(4000),
  "to_state" VARCHAR2(4000) NOT NULL,
  "principal" VARCHAR2(4000) NOT NULL,
  "ticket_ref" VARCHAR2(4000),
  "detail" CLOB,
  "recorded_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "effective_at" TIMESTAMP WITH TIME ZONE NOT NULL,
  "supersedes_event_id" NUMBER(19),
  PRIMARY KEY ("audit_event_id")
);

CREATE UNIQUE INDEX "uq_domain_name" ON "domain" ("name");

CREATE UNIQUE INDEX "uq_task_domain" ON "task" ("domain_id", "task_id");

CREATE UNIQUE INDEX "uq_folder_domain" ON "folder" ("domain_id", "folder_id");

CREATE UNIQUE INDEX "uq_folder_kind" ON "folder" ("folder_id", "kind");

CREATE UNIQUE INDEX "uq_task_version_number" ON "task_version" ("task_id", "version");

CREATE UNIQUE INDEX "uq_plan_domain_odate" ON "plan" ("domain_id", "odate");

CREATE UNIQUE INDEX "uq_outbox_attempt" ON "outbox" ("task_instance_id", "attempt_no");

ALTER TABLE "task" ADD CONSTRAINT "task_domain_fk" FOREIGN KEY ("domain_id") REFERENCES "domain" ("domain_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "folder" ADD CONSTRAINT "folder_domain_fk" FOREIGN KEY ("domain_id") REFERENCES "domain" ("domain_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "task_version" ADD CONSTRAINT "task_version_task_fk" FOREIGN KEY ("domain_id", "task_id") REFERENCES "task" ("domain_id", "task_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "task_version" ADD CONSTRAINT "task_version_folder_fk" FOREIGN KEY ("domain_id", "folder_id") REFERENCES "folder" ("domain_id", "folder_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "task_version" ADD CONSTRAINT "task_version_set_by_folder_fk" FOREIGN KEY ("domain_id", "runs_until_set_by_folder_id") REFERENCES "folder" ("domain_id", "folder_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "plan" ADD CONSTRAINT "plan_domain_fk" FOREIGN KEY ("domain_id") REFERENCES "domain" ("domain_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "task_instance" ADD CONSTRAINT "task_instance_plan_fk" FOREIGN KEY ("plan_id") REFERENCES "plan" ("plan_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "task_instance" ADD CONSTRAINT "task_instance_task_version_fk" FOREIGN KEY ("task_version_id") REFERENCES "task_version" ("task_version_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "attempt" ADD CONSTRAINT "attempt_task_instance_fk" FOREIGN KEY ("task_instance_id") REFERENCES "task_instance" ("task_instance_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "attempt" ADD CONSTRAINT "outbox_attempt_fk" FOREIGN KEY ("task_instance_id", "attempt_no") REFERENCES "outbox" ("task_instance_id", "attempt_no") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "audit_event" ADD CONSTRAINT "audit_event_supersedes_fk" FOREIGN KEY ("supersedes_event_id") REFERENCES "audit_event" ("audit_event_id") DEFERRABLE INITIALLY IMMEDIATE;
