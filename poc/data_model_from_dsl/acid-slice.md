---
title: Acid Slice
---

# Acid Slice

This file specifies the nine entities that every candidate story ports. It is
the fixed input of the [data-model DSL PoC](proposal-data-model-dsl-technical-poc.md).

**Source:** Gigacron `docs/spec/supplementary_specs/entity-model.md` at commit
`40954f18fe72b237ecc865905a31cf0b9b146556`. Every column, constraint, and enum
value below is copied from that file. Nothing is invented.

**Reading rules.**

- A column is NOT NULL unless the model lists it under NULL ALLOWED, or the
  constraint table makes it optional. The Mermaid diagram itself states no
  nullability, so this is the PoC's reading of the model.
- Plain indexes (`ix_*`) are left out, because they are not constraints and no
  construct tests them.
- Application-enforced rules (immutability, forward-only states) are left out,
  because no schema language can check them.
- A foreign key that points outside the slice is left out. The column stays.
  The table [Foreign keys left out](#foreign-keys-left-out) lists each one.

## Constructs

| No. | Construct                                       | Where in the slice                                                                                                                                                        |
| --- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Composite primary key                           | `attempt_pkey (task_instance_id, attempt_no)`                                                                                                                             |
| 2   | Composite foreign key                           | `task_version_task_fk`, `task_version_folder_fk`, `task_version_set_by_folder_fk`, `outbox_attempt_fk`                                                                    |
| 3   | JSON payload column                             | six `jsonb` sections on `task_version`; `task_instance.filled_values`; `outbox.payload`; `audit_event.detail`                                                             |
| 4   | Enumerated string domain                        | `domain.state`, `task.state`, `folder.kind`, `folder.state`, `plan.state`, `task_instance.state`, `attempt.attempt_state`, `outbox.message_type`, `outbox.delivery_state` |
| 5   | Self-referencing foreign key                    | `audit_event_supersedes_fk`                                                                                                                                               |
| 6   | Nullable foreign key                            | `outbox_attempt_fk (task_instance_id, attempt_no)`; `task_version.runs_until_set_by_folder_id`                                                                            |
| 7   | Multi-column UNIQUE not tied to the primary key | `uq_task_domain`, `uq_folder_domain`, `uq_folder_kind`, `uq_task_version_number`, `uq_plan_domain_odate`                                                                  |
| 8   | Partial UNIQUE                                  | `uq_folder_root_per_domain`, `uq_task_version_current`, `uq_attempt_open`, `uq_outbox_attempt`                                                                            |
| 9   | One-to-zero-or-one relationship                 | one `attempt` has at most one Command in `outbox` (`uq_outbox_attempt`)                                                                                                   |
| 10  | CHECK across columns                            | `ck_folder_state`, `ck_task_version_range`, `ck_outbox_attempt`                                                                                                           |
| 11  | Exclusion constraint                            | `ex_task_version_range` (needs the extension `btree_gist`)                                                                                                                |
| 12  | `domain_id` convention                          | Domain-owned tables `task`, `folder`, `task_version`, `plan` carry `domain_id`; `domain` is the root                                                                      |

`task_instance`, `attempt`, `outbox`, and `audit_event` reach their Domain
through a parent row and carry no `domain_id`. Construct 12 does not apply to
them.

## Entities

Types use the model's names: `bigint`, `int`, `smallint`, `string` (text),
`date`, `time`, `timestamptz`, `jsonb`, and `enum` (text restricted to the
listed values).

### domain

| Column                | Type        | Null |
| --------------------- | ----------- | ---- |
| `domain_id`           | bigint      | no   |
| `name`                | string      | no   |
| `timezone`            | string      | no   |
| `odate_boundary_time` | time        | no   |
| `projection_horizon`  | int         | no   |
| `heartbeat_interval`  | int         | no   |
| `liveness_threshold`  | int         | no   |
| `state`               | enum        | no   |
| `created_at`          | timestamptz | no   |
| `state_changed_at`    | timestamptz | no   |
| `updated_at`          | timestamptz | no   |

- `domain_pkey` PRIMARY KEY (`domain_id`)
- `uq_domain_name` UNIQUE (`name`)
- `state` ∈ {`DRAFT`, `ACTIVE`, `INACTIVE`, `RETIRED`}

### task

| Column             | Type        | Null |
| ------------------ | ----------- | ---- |
| `task_id`          | bigint      | no   |
| `domain_id`        | bigint      | no   |
| `state`            | enum        | no   |
| `created_at`       | timestamptz | no   |
| `state_changed_at` | timestamptz | no   |

- `task_pkey` PRIMARY KEY (`task_id`)
- `task_domain_fk` FOREIGN KEY (`domain_id`) → `domain (domain_id)`
- `uq_task_domain` UNIQUE (`domain_id`, `task_id`)
- `state` ∈ {`ACTIVE`, `INACTIVE`, `RETIRED`}

### folder

| Column             | Type        | Null |
| ------------------ | ----------- | ---- |
| `folder_id`        | bigint      | no   |
| `domain_id`        | bigint      | no   |
| `kind`             | enum        | no   |
| `state`            | enum        | no   |
| `created_at`       | timestamptz | no   |
| `state_changed_at` | timestamptz | no   |

- `folder_pkey` PRIMARY KEY (`folder_id`)
- `folder_domain_fk` FOREIGN KEY (`domain_id`) → `domain (domain_id)`
- `uq_folder_domain` UNIQUE (`domain_id`, `folder_id`)
- `uq_folder_kind` UNIQUE (`folder_id`, `kind`)
- `ck_folder_kind` CHECK (`kind IN ('ROOT', 'REGULAR', 'SMART')`)
- `uq_folder_root_per_domain` UNIQUE (`domain_id`) WHERE `kind = 'ROOT'`
- `ck_folder_state` CHECK (`kind = 'SMART' OR state = 'ACTIVE'`)
- `kind` ∈ {`ROOT`, `REGULAR`, `SMART`}
- `state` ∈ {`ACTIVE`, `INACTIVE`, `RETIRED`}

### task_version

| Column                        | Type        | Null |
| ----------------------------- | ----------- | ---- |
| `task_version_id`             | bigint      | no   |
| `task_id`                     | bigint      | no   |
| `domain_id`                   | bigint      | no   |
| `folder_id`                   | bigint      | no   |
| `version`                     | int         | no   |
| `name`                        | string      | no   |
| `dispatch_target`             | string      | yes  |
| `identity`                    | jsonb       | yes  |
| `scheduling`                  | jsonb       | yes  |
| `execution`                   | jsonb       | yes  |
| `dependencies`                | jsonb       | yes  |
| `event_handling`              | jsonb       | yes  |
| `constraints`                 | jsonb       | yes  |
| `published_at`                | timestamptz | no   |
| `superseded_at`               | timestamptz | yes  |
| `runs_from`                   | date        | no   |
| `runs_until`                  | date        | yes  |
| `runs_until_set_by_folder_id` | bigint      | yes  |
| `created_by`                  | string      | no   |

- `task_version_pkey` PRIMARY KEY (`task_version_id`)
- `task_version_task_fk` FOREIGN KEY (`domain_id`, `task_id`) → `task (domain_id, task_id)`
- `task_version_folder_fk` FOREIGN KEY (`domain_id`, `folder_id`) → `folder (domain_id, folder_id)`
- `task_version_set_by_folder_fk` FOREIGN KEY (`domain_id`, `runs_until_set_by_folder_id`) → `folder (domain_id, folder_id)`
- `uq_task_version_number` UNIQUE (`task_id`, `version`)
- `uq_task_version_current` UNIQUE (`task_id`) WHERE `superseded_at IS NULL`
- `ex_task_version_range` EXCLUDE USING gist (`task_id WITH =`, `daterange(runs_from, runs_until) WITH &&`)
- `ck_task_version_range` CHECK (`runs_until IS NULL OR runs_until >= runs_from`)

The model's comment on `folder_id` says the column stays null in Increment 01
(T-0051), while its constraint table says NOT NULL. The slice follows the
constraint table.

### plan

| Column       | Type        | Null |
| ------------ | ----------- | ---- |
| `plan_id`    | bigint      | no   |
| `domain_id`  | bigint      | no   |
| `odate`      | date        | no   |
| `state`      | enum        | no   |
| `created_at` | timestamptz | no   |
| `updated_at` | timestamptz | no   |

- `plan_pkey` PRIMARY KEY (`plan_id`)
- `plan_domain_fk` FOREIGN KEY (`domain_id`) → `domain (domain_id)`
- `uq_plan_domain_odate` UNIQUE (`domain_id`, `odate`)
- `state` ∈ {`PENDING`, `OPEN`, `CLOSED`}

### task_instance

| Column              | Type        | Null |
| ------------------- | ----------- | ---- |
| `task_instance_id`  | bigint      | no   |
| `plan_id`           | bigint      | no   |
| `task_version_id`   | bigint      | no   |
| `folder_version_id` | bigint      | yes  |
| `filled_values`     | jsonb       | no   |
| `state`             | enum        | no   |
| `result`            | string      | yes  |
| `queued_at`         | timestamptz | yes  |
| `run_at`            | timestamptz | yes  |
| `no_run_at`         | timestamptz | yes  |
| `result_at`         | timestamptz | yes  |
| `wake_at`           | timestamptz | yes  |
| `wake_on`           | string      | yes  |
| `created_at`        | timestamptz | no   |
| `updated_at`        | timestamptz | no   |

- `task_instance_pkey` PRIMARY KEY (`task_instance_id`)
- `task_instance_plan_fk` FOREIGN KEY (`plan_id`) → `plan (plan_id)`
- `task_instance_task_version_fk` FOREIGN KEY (`task_version_id`) → `task_version (task_version_id)`
- `state` ∈ {`WAITING`, `QUEUED`, `RUN`, `NO_RUN`}

The model lists only `folder_version_id`, `result`, and `result_at` as
nullable. The state times and `wake_*` columns are set only in some states, so
the slice reads them as nullable too.

### attempt

| Column             | Type        | Null |
| ------------------ | ----------- | ---- |
| `task_instance_id` | bigint      | no   |
| `attempt_no`       | int         | no   |
| `agent_id`         | bigint      | no   |
| `attempt_state`    | enum        | no   |
| `exit_code`        | int         | yes  |
| `dispatching_at`   | timestamptz | no   |
| `dispatched_at`    | timestamptz | yes  |
| `running_at`       | timestamptz | yes  |
| `unknown_at`       | timestamptz | yes  |
| `finished_at`      | timestamptz | yes  |
| `started_at`       | timestamptz | yes  |
| `ended_at`         | timestamptz | yes  |
| `updated_at`       | timestamptz | no   |

- `attempt_pkey` PRIMARY KEY (`task_instance_id`, `attempt_no`)
- `attempt_task_instance_fk` FOREIGN KEY (`task_instance_id`) → `task_instance (task_instance_id)`
- `uq_attempt_open` UNIQUE (`task_instance_id`) WHERE `attempt_state NOT IN ('SUCCEEDED', 'FAILED')`
- `attempt_state` ∈ {`DISPATCHING`, `DISPATCHED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `UNKNOWN`}

### outbox

| Column             | Type        | Null |
| ------------------ | ----------- | ---- |
| `message_id`       | bigint      | no   |
| `task_instance_id` | bigint      | yes  |
| `attempt_no`       | int         | yes  |
| `agent_id`         | bigint      | no   |
| `message_type`     | enum        | no   |
| `payload`          | jsonb       | no   |
| `delivery_state`   | enum        | no   |
| `leased_until`     | timestamptz | yes  |
| `created_at`       | timestamptz | no   |
| `leased_at`        | timestamptz | yes  |
| `sent_at`          | timestamptz | yes  |
| `acked_at`         | timestamptz | yes  |
| `updated_at`       | timestamptz | no   |

- `outbox_pkey` PRIMARY KEY (`message_id`)
- `outbox_attempt_fk` FOREIGN KEY (`task_instance_id`, `attempt_no`) → `attempt (task_instance_id, attempt_no)`, nullable
- `uq_outbox_attempt` UNIQUE (`task_instance_id`, `attempt_no`) WHERE `task_instance_id IS NOT NULL`
- `ck_outbox_attempt` CHECK (`(message_type = 'COMMAND') = (task_instance_id IS NOT NULL) AND (task_instance_id IS NULL) = (attempt_no IS NULL)`)
- `message_type` ∈ {`COMMAND`, `COMMAND_OFFER`, `CONTROL`}
- `delivery_state` ∈ {`PENDING`, `LEASED`, `SENT`, `ACKED`}

### audit_event

| Column                | Type        | Null |
| --------------------- | ----------- | ---- |
| `audit_event_id`      | bigint      | no   |
| `event_type_id`       | smallint    | no   |
| `audited_entity_id`   | smallint    | no   |
| `entity_id`           | bigint      | no   |
| `from_state`          | string      | yes  |
| `to_state`            | string      | no   |
| `principal`           | string      | no   |
| `ticket_ref`          | string      | yes  |
| `detail`              | jsonb       | yes  |
| `recorded_at`         | timestamptz | no   |
| `effective_at`        | timestamptz | no   |
| `supersedes_event_id` | bigint      | yes  |

- `audit_event_pkey` PRIMARY KEY (`audit_event_id`)
- `audit_event_supersedes_fk` FOREIGN KEY (`supersedes_event_id`) → `audit_event (audit_event_id)`

## Foreign keys left out

| Constraint                        | Column                            | Target outside the slice |
| --------------------------------- | --------------------------------- | ------------------------ |
| `task_instance_folder_version_fk` | `task_instance.folder_version_id` | `folder_version`         |
| `attempt_agent_fk`                | `attempt.agent_id`                | `agent`                  |
| `outbox_agent_fk`                 | `outbox.agent_id`                 | `agent`                  |
| `audit_event_type_fk`             | `audit_event.event_type_id`       | `event_type`             |
| `audit_event_entity_fk`           | `audit_event.audited_entity_id`   | `audited_entity`         |
