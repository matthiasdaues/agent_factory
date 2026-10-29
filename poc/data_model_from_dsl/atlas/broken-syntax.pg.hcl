# Spike code for the data-model DSL PoC. The acid slice in Atlas HCL.
# Source: acid-slice.md (Gigacron 40954f18). Enumerated columns use
# PostgreSQL enum types; "string" columns use varchar.

schema "public" {}


enum "domain_state" {
  schema = schema.public
  values = ["DRAFT", "ACTIVE", "INACTIVE", "RETIRED"]
}
enum "task_state" {
  schema = schema.public
  values = ["ACTIVE", "INACTIVE", "RETIRED"]
}
enum "folder_kind" {
  schema = schema.public
  values = ["ROOT", "REGULAR", "SMART"]
}
enum "folder_state" {
  schema = schema.public
  values = ["ACTIVE", "INACTIVE", "RETIRED"]
}
enum "plan_state" {
  schema = schema.public
  values = ["PENDING", "OPEN", "CLOSED"]
}
enum "task_instance_state" {
  schema = schema.public
  values = ["WAITING", "QUEUED", "RUN", "NO_RUN"]
}
enum "attempt_state" {
  schema = schema.public
  values = ["DISPATCHING", "DISPATCHED", "RUNNING", "SUCCEEDED", "FAILED", "UNKNOWN"]
}
enum "outbox_message_type" {
  schema = schema.public
  values = ["COMMAND", "COMMAND_OFFER", "CONTROL"]
}
enum "outbox_delivery_state" {
  schema = schema.public
  values = ["PENDING", "LEASED", "SENT", "ACKED"]
}

table "domain" {
  schema = schema.public
  column "domain_id" {
    type = bigint
  }
  column "name" {
    type = varchar
  }
  column "timezone" {
    type = varchar
  }
  column "odate_boundary_time" {
    type = time
  }
  column "projection_horizon" {
    type = integer
  }
  column "heartbeat_interval" {
    type = integer
  }
  column "liveness_threshold" {
    type = integer
  }
  column "state" {
    type = enum.domain_state
  }
  column "created_at" {
    type = timestamptz
  }
  column "state_changed_at" {
    type = timestamptz
  }
  column "updated_at" {
    type = timestamptz
  }
  primary_key "domain_pkey" {
    columns = [column.domain_id]
  }
  unique "uq_domain_name" {
    columns = [column.name]
  }


table "task" {
  schema = schema.public
  comment = "domain-owned"
  column "task_id" {
    type = bigint
  }
  column "domain_id" {
    type = bigint
  }
  column "state" {
    type = enum.task_state
  }
  column "created_at" {
    type = timestamptz
  }
  column "state_changed_at" {
    type = timestamptz
  }
  primary_key "task_pkey" {
    columns = [column.task_id]
  }
  foreign_key "task_domain_fk" {
    columns     = [column.domain_id]
    ref_columns = [table.domain.column.domain_id]
  }
  unique "uq_task_domain" {
    columns = [column.domain_id, column.task_id]
  }
}

table "folder" {
  schema = schema.public
  comment = "domain-owned"
  column "folder_id" {
    type = bigint
  }
  column "domain_id" {
    type = bigint
  }
  column "kind" {
    type = enum.folder_kind
  }
  column "state" {
    type = enum.folder_state
  }
  column "created_at" {
    type = timestamptz
  }
  column "state_changed_at" {
    type = timestamptz
  }
  primary_key "folder_pkey" {
    columns = [column.folder_id]
  }
  foreign_key "folder_domain_fk" {
    columns     = [column.domain_id]
    ref_columns = [table.domain.column.domain_id]
  }
  unique "uq_folder_domain" {
    columns = [column.domain_id, column.folder_id]
  }
  unique "uq_folder_kind" {
    columns = [column.folder_id, column.kind]
  }
  index "uq_folder_root_per_domain" {
    unique  = true
    columns = [column.domain_id]
    where   = "kind = 'ROOT'"
  }
  check "ck_folder_kind" {
    expr = "kind IN ('ROOT', 'REGULAR', 'SMART')"
  }
  check "ck_folder_state" {
    expr = "kind = 'SMART' OR state = 'ACTIVE'"
  }
}

table "task_version" {
  schema = schema.public
  comment = "domain-owned"
  column "task_version_id" {
    type = bigint
  }
  column "task_id" {
    type = bigint
  }
  column "domain_id" {
    type = bigint
  }
  column "folder_id" {
    type = bigint
  }
  column "version" {
    type = integer
  }
  column "name" {
    type = varchar
  }
  column "dispatch_target" {
    type = varchar
    null = true
  }
  column "identity" {
    type = jsonb
    null = true
  }
  column "scheduling" {
    type = jsonb
    null = true
  }
  column "execution" {
    type = jsonb
    null = true
  }
  column "dependencies" {
    type = jsonb
    null = true
  }
  column "event_handling" {
    type = jsonb
    null = true
  }
  column "constraints" {
    type = jsonb
    null = true
  }
  column "published_at" {
    type = timestamptz
  }
  column "superseded_at" {
    type = timestamptz
    null = true
  }
  column "runs_from" {
    type = date
  }
  column "runs_until" {
    type = date
    null = true
  }
  column "runs_until_set_by_folder_id" {
    type = bigint
    null = true
  }
  column "created_by" {
    type = varchar
  }
  primary_key "task_version_pkey" {
    columns = [column.task_version_id]
  }
  foreign_key "task_version_task_fk" {
    columns     = [column.domain_id, column.task_id]
    ref_columns = [table.task.column.domain_id, table.task.column.task_id]
  }
  foreign_key "task_version_folder_fk" {
    columns     = [column.domain_id, column.folder_id]
    ref_columns = [table.folder.column.domain_id, table.folder.column.folder_id]
  }
  foreign_key "task_version_set_by_folder_fk" {
    columns     = [column.domain_id, column.runs_until_set_by_folder_id]
    ref_columns = [table.folder.column.domain_id, table.folder.column.folder_id]
  }
  unique "uq_task_version_number" {
    columns = [column.task_id, column.version]
  }
  index "uq_task_version_current" {
    unique  = true
    columns = [column.task_id]
    where   = "superseded_at IS NULL"
  }
  exclude "ex_task_version_range" {
    type = GIST
    on {
      column = column.task_id
      op     = "="
    }
    on {
      expr = "daterange(runs_from, runs_until)"
      op   = "&&"
    }
  }
  check "ck_task_version_range" {
    expr = "runs_until IS NULL OR runs_until >= runs_from"
  }
}

table "plan" {
  schema = schema.public
  comment = "domain-owned"
  column "plan_id" {
    type = bigint
  }
  column "domain_id" {
    type = bigint
  }
  column "odate" {
    type = date
  }
  column "state" {
    type = enum.plan_state
  }
  column "created_at" {
    type = timestamptz
  }
  column "updated_at" {
    type = timestamptz
  }
  primary_key "plan_pkey" {
    columns = [column.plan_id]
  }
  foreign_key "plan_domain_fk" {
    columns     = [column.domain_id]
    ref_columns = [table.domain.column.domain_id]
  }
  unique "uq_plan_domain_odate" {
    columns = [column.domain_id, column.odate]
  }
}

table "task_instance" {
  schema = schema.public
  column "task_instance_id" {
    type = bigint
  }
  column "plan_id" {
    type = bigint
  }
  column "task_version_id" {
    type = bigint
  }
  column "folder_version_id" {
    type = bigint
    null = true
  }
  column "filled_values" {
    type = jsonb
  }
  column "state" {
    type = enum.task_instance_state
  }
  column "result" {
    type = varchar
    null = true
  }
  column "queued_at" {
    type = timestamptz
    null = true
  }
  column "run_at" {
    type = timestamptz
    null = true
  }
  column "no_run_at" {
    type = timestamptz
    null = true
  }
  column "result_at" {
    type = timestamptz
    null = true
  }
  column "wake_at" {
    type = timestamptz
    null = true
  }
  column "wake_on" {
    type = varchar
    null = true
  }
  column "created_at" {
    type = timestamptz
  }
  column "updated_at" {
    type = timestamptz
  }
  primary_key "task_instance_pkey" {
    columns = [column.task_instance_id]
  }
  foreign_key "task_instance_plan_fk" {
    columns     = [column.plan_id]
    ref_columns = [table.plan.column.plan_id]
  }
  foreign_key "task_instance_task_version_fk" {
    columns     = [column.task_version_id]
    ref_columns = [table.task_version.column.task_version_id]
  }
}

table "attempt" {
  schema = schema.public
  column "task_instance_id" {
    type = bigint
  }
  column "attempt_no" {
    type = integer
  }
  column "agent_id" {
    type = bigint
  }
  column "attempt_state" {
    type = enum.attempt_state
  }
  column "exit_code" {
    type = integer
    null = true
  }
  column "dispatching_at" {
    type = timestamptz
  }
  column "dispatched_at" {
    type = timestamptz
    null = true
  }
  column "running_at" {
    type = timestamptz
    null = true
  }
  column "unknown_at" {
    type = timestamptz
    null = true
  }
  column "finished_at" {
    type = timestamptz
    null = true
  }
  column "started_at" {
    type = timestamptz
    null = true
  }
  column "ended_at" {
    type = timestamptz
    null = true
  }
  column "updated_at" {
    type = timestamptz
  }
  primary_key "attempt_pkey" {
    columns = [column.task_instance_id, column.attempt_no]
  }
  foreign_key "attempt_task_instance_fk" {
    columns     = [column.task_instance_id]
    ref_columns = [table.task_instance.column.task_instance_id]
  }
  index "uq_attempt_open" {
    unique  = true
    columns = [column.task_instance_id]
    where   = "attempt_state NOT IN ('SUCCEEDED', 'FAILED')"
  }
}

table "outbox" {
  schema = schema.public
  column "message_id" {
    type = bigint
  }
  column "task_instance_id" {
    type = bigint
    null = true
  }
  column "attempt_no" {
    type = integer
    null = true
  }
  column "agent_id" {
    type = bigint
  }
  column "message_type" {
    type = enum.outbox_message_type
  }
  column "payload" {
    type = jsonb
  }
  column "delivery_state" {
    type = enum.outbox_delivery_state
  }
  column "leased_until" {
    type = timestamptz
    null = true
  }
  column "created_at" {
    type = timestamptz
  }
  column "leased_at" {
    type = timestamptz
    null = true
  }
  column "sent_at" {
    type = timestamptz
    null = true
  }
  column "acked_at" {
    type = timestamptz
    null = true
  }
  column "updated_at" {
    type = timestamptz
  }
  primary_key "outbox_pkey" {
    columns = [column.message_id]
  }
  foreign_key "outbox_attempt_fk" {
    columns     = [column.task_instance_id, column.attempt_no]
    ref_columns = [table.attempt.column.task_instance_id, table.attempt.column.attempt_no]
  }
  index "uq_outbox_attempt" {
    unique  = true
    columns = [column.task_instance_id, column.attempt_no]
    where   = "task_instance_id IS NOT NULL"
  }
  check "ck_outbox_attempt" {
    expr = "(message_type = 'COMMAND') = (task_instance_id IS NOT NULL) AND (task_instance_id IS NULL) = (attempt_no IS NULL)"
  }
}

table "audit_event" {
  schema = schema.public
  column "audit_event_id" {
    type = bigint
  }
  column "event_type_id" {
    type = smallint
  }
  column "audited_entity_id" {
    type = smallint
  }
  column "entity_id" {
    type = bigint
  }
  column "from_state" {
    type = varchar
    null = true
  }
  column "to_state" {
    type = varchar
  }
  column "principal" {
    type = varchar
  }
  column "ticket_ref" {
    type = varchar
    null = true
  }
  column "detail" {
    type = jsonb
    null = true
  }
  column "recorded_at" {
    type = timestamptz
  }
  column "effective_at" {
    type = timestamptz
  }
  column "supersedes_event_id" {
    type = bigint
    null = true
  }
  primary_key "audit_event_pkey" {
    columns = [column.audit_event_id]
  }
  foreign_key "audit_event_supersedes_fk" {
    columns     = [column.supersedes_event_id]
    ref_columns = [table.audit_event.column.audit_event_id]
  }
}
