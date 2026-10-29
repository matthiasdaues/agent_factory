-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: PostgreSQL
-- Generated at: 2026-10-29T20:10:28.912Z

CREATE TYPE "domain_state" AS ENUM (
  'DRAFT',
  'ACTIVE',
  'INACTIVE',
  'RETIRED'
);

CREATE TYPE "task_state" AS ENUM (
  'ACTIVE',
  'INACTIVE',
  'RETIRED'
);

CREATE TYPE "folder_kind" AS ENUM (
  'ROOT',
  'REGULAR',
  'SMART'
);

CREATE TYPE "folder_state" AS ENUM (
  'ACTIVE',
  'INACTIVE',
  'RETIRED'
);

CREATE TYPE "plan_state" AS ENUM (
  'PENDING',
  'OPEN',
  'CLOSED'
);

CREATE TYPE "task_instance_state" AS ENUM (
  'WAITING',
  'QUEUED',
  'RUN',
  'NO_RUN'
);

CREATE TYPE "attempt_state" AS ENUM (
  'DISPATCHING',
  'DISPATCHED',
  'RUNNING',
  'SUCCEEDED',
  'FAILED',
  'UNKNOWN'
);

CREATE TYPE "outbox_message_type" AS ENUM (
  'COMMAND',
  'COMMAND_OFFER',
  'CONTROL'
);

CREATE TYPE "outbox_delivery_state" AS ENUM (
  'PENDING',
  'LEASED',
  'SENT',
  'ACKED'
);

CREATE TABLE "domain" (
  "domain_id" bigint NOT NULL,
  "name" varchar NOT NULL,
  "timezone" varchar NOT NULL,
  "odate_boundary_time" time NOT NULL,
  "projection_horizon" integer NOT NULL,
  "heartbeat_interval" integer NOT NULL,
  "liveness_threshold" integer NOT NULL,
  "state" domain_state NOT NULL,
  "created_at" timestamptz NOT NULL,
  "state_changed_at" timestamptz NOT NULL,
  "updated_at" timestamptz NOT NULL,
  PRIMARY KEY ("domain_id")
);

CREATE TABLE "task" (
  "task_id" bigint NOT NULL,
  "domain_id" varchar NOT NULL,
  "state" task_state NOT NULL,
  "created_at" timestamptz NOT NULL,
  "state_changed_at" timestamptz NOT NULL,
  PRIMARY KEY ("task_id")
);

CREATE TABLE "folder" (
  "folder_id" bigint NOT NULL,
  "domain_id" bigint NOT NULL,
  "kind" folder_kind NOT NULL,
  "state" folder_state NOT NULL,
  "created_at" timestamptz NOT NULL,
  "state_changed_at" timestamptz NOT NULL,
  CONSTRAINT "ck_folder_state" CHECK (kind = 'SMART' OR state = 'ACTIVE'),
  PRIMARY KEY ("folder_id")
);

CREATE TABLE "task_version" (
  "task_version_id" bigint NOT NULL,
  "task_id" bigint NOT NULL,
  "domain_id" bigint NOT NULL,
  "folder_id" bigint NOT NULL,
  "version" integer NOT NULL,
  "name" varchar NOT NULL,
  "dispatch_target" varchar,
  "identity" jsonb,
  "scheduling" jsonb,
  "execution" jsonb,
  "dependencies" jsonb,
  "event_handling" jsonb,
  "constraints" jsonb,
  "published_at" timestamptz NOT NULL,
  "superseded_at" timestamptz,
  "runs_from" date NOT NULL,
  "runs_until" date,
  "runs_until_set_by_folder_id" bigint,
  "created_by" varchar NOT NULL,
  CONSTRAINT "ck_task_version_range" CHECK (runs_until IS NULL OR runs_until >= runs_from),
  PRIMARY KEY ("task_version_id")
);

CREATE TABLE "plan" (
  "plan_id" bigint NOT NULL,
  "domain_id" bigint NOT NULL,
  "odate" date NOT NULL,
  "state" plan_state NOT NULL,
  "created_at" timestamptz NOT NULL,
  "updated_at" timestamptz NOT NULL,
  PRIMARY KEY ("plan_id")
);

CREATE TABLE "task_instance" (
  "task_instance_id" bigint NOT NULL,
  "plan_id" bigint NOT NULL,
  "task_version_id" bigint NOT NULL,
  "folder_version_id" bigint,
  "filled_values" jsonb NOT NULL,
  "state" task_instance_state NOT NULL,
  "result" varchar,
  "queued_at" timestamptz,
  "run_at" timestamptz,
  "no_run_at" timestamptz,
  "result_at" timestamptz,
  "wake_at" timestamptz,
  "wake_on" varchar,
  "created_at" timestamptz NOT NULL,
  "updated_at" timestamptz NOT NULL,
  PRIMARY KEY ("task_instance_id")
);

CREATE TABLE "attempt" (
  "task_instance_id" bigint NOT NULL,
  "attempt_no" integer NOT NULL,
  "agent_id" bigint NOT NULL,
  "attempt_state" attempt_state NOT NULL,
  "exit_code" integer,
  "dispatching_at" timestamptz NOT NULL,
  "dispatched_at" timestamptz,
  "running_at" timestamptz,
  "unknown_at" timestamptz,
  "finished_at" timestamptz,
  "started_at" timestamptz,
  "ended_at" timestamptz,
  "updated_at" timestamptz NOT NULL,
  PRIMARY KEY ("task_instance_id", "attempt_no")
);

CREATE TABLE "outbox" (
  "message_id" bigint NOT NULL,
  "task_instance_id" bigint,
  "attempt_no" integer,
  "agent_id" bigint NOT NULL,
  "message_type" outbox_message_type NOT NULL,
  "payload" jsonb NOT NULL,
  "delivery_state" outbox_delivery_state NOT NULL,
  "leased_until" timestamptz,
  "created_at" timestamptz NOT NULL,
  "leased_at" timestamptz,
  "sent_at" timestamptz,
  "acked_at" timestamptz,
  "updated_at" timestamptz NOT NULL,
  CONSTRAINT "ck_outbox_attempt" CHECK ((message_type = 'COMMAND') = (task_instance_id IS NOT NULL) AND (task_instance_id IS NULL) = (attempt_no IS NULL)),
  PRIMARY KEY ("message_id")
);

CREATE TABLE "audit_event" (
  "audit_event_id" bigint NOT NULL,
  "event_type_id" smallint NOT NULL,
  "audited_entity_id" smallint NOT NULL,
  "entity_id" bigint NOT NULL,
  "from_state" varchar,
  "to_state" varchar NOT NULL,
  "principal" varchar NOT NULL,
  "ticket_ref" varchar,
  "detail" jsonb,
  "recorded_at" timestamptz NOT NULL,
  "effective_at" timestamptz NOT NULL,
  "supersedes_event_id" bigint,
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
