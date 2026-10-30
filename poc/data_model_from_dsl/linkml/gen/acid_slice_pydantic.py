from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.12.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'gc',
     'default_range': 'string',
     'id': 'https://example.org/gigacron/acid-slice',
     'imports': ['linkml:types'],
     'name': 'acid_slice',
     'prefixes': {'gc': {'prefix_prefix': 'gc',
                         'prefix_reference': 'https://example.org/gigacron/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'acid-slice.yaml'} )

class DomainState(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RETIRED = "RETIRED"


class TaskState(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RETIRED = "RETIRED"


class FolderKind(str, Enum):
    ROOT = "ROOT"
    REGULAR = "REGULAR"
    SMART = "SMART"


class FolderState(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    RETIRED = "RETIRED"


class PlanState(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class TaskInstanceState(str, Enum):
    WAITING = "WAITING"
    QUEUED = "QUEUED"
    RUN = "RUN"
    NO_RUN = "NO_RUN"


class AttemptState(str, Enum):
    DISPATCHING = "DISPATCHING"
    DISPATCHED = "DISPATCHED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class OutboxMessageType(str, Enum):
    COMMAND = "COMMAND"
    COMMAND_OFFER = "COMMAND_OFFER"
    CONTROL = "CONTROL"


class OutboxDeliveryState(str, Enum):
    PENDING = "PENDING"
    LEASED = "LEASED"
    SENT = "SENT"
    ACKED = "ACKED"



class Domain(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'sql_table': {'tag': 'sql_table', 'value': 'domain'}},
         'from_schema': 'https://example.org/gigacron/acid-slice',
         'unique_keys': {'uq_domain_name': {'unique_key_name': 'uq_domain_name',
                                            'unique_key_slots': ['name']}}})

    domain_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'TaskVersion', 'Plan']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'TaskVersion']} })
    timezone: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain']} })
    odate_boundary_time: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain']} })
    projection_horizon: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain']} })
    heartbeat_interval: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain']} })
    liveness_threshold: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain']} })
    state: DomainState = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance']} })
    created_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance', 'Outbox']} })
    state_changed_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder']} })
    updated_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Plan', 'TaskInstance', 'Attempt', 'Outbox']} })


class Task(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'domain_owned': {'tag': 'domain_owned', 'value': True},
                         'sql_table': {'tag': 'sql_table', 'value': 'task'}},
         'from_schema': 'https://example.org/gigacron/acid-slice',
         'unique_keys': {'uq_task_domain': {'unique_key_name': 'uq_task_domain',
                                            'unique_key_slots': ['domain_id',
                                                                 'task_id']}}})

    task_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Task', 'TaskVersion']} })
    domain_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'TaskVersion', 'Plan']} })
    state: TaskState = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance']} })
    created_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance', 'Outbox']} })
    state_changed_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder']} })


class Folder(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'domain_owned': {'tag': 'domain_owned', 'value': True},
                         'sql_table': {'tag': 'sql_table', 'value': 'folder'}},
         'from_schema': 'https://example.org/gigacron/acid-slice',
         'rules': [{'description': "kind = 'SMART' OR state = 'ACTIVE'",
                    'postconditions': {'slot_conditions': {'state': {'equals_string': 'ACTIVE',
                                                                     'name': 'state'}}},
                    'preconditions': {'slot_conditions': {'kind': {'name': 'kind',
                                                                   'none_of': [{'equals_string': 'SMART'}]}}},
                    'title': 'ck_folder_state'}],
         'unique_keys': {'uq_folder_domain': {'unique_key_name': 'uq_folder_domain',
                                              'unique_key_slots': ['domain_id',
                                                                   'folder_id']},
                         'uq_folder_kind': {'unique_key_name': 'uq_folder_kind',
                                            'unique_key_slots': ['folder_id', 'kind']}}})

    folder_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Folder', 'TaskVersion']} })
    domain_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'TaskVersion', 'Plan']} })
    kind: FolderKind = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Folder']} })
    state: FolderState = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance']} })
    created_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance', 'Outbox']} })
    state_changed_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder']} })


class TaskVersion(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'domain_owned': {'tag': 'domain_owned', 'value': True},
                         'sql_table': {'tag': 'sql_table', 'value': 'task_version'}},
         'from_schema': 'https://example.org/gigacron/acid-slice',
         'unique_keys': {'uq_task_version_number': {'unique_key_name': 'uq_task_version_number',
                                                    'unique_key_slots': ['task_id',
                                                                         'version']}}})

    task_version_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion', 'TaskInstance']} })
    task_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Task', 'TaskVersion']} })
    domain_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'TaskVersion', 'Plan']} })
    folder_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Folder', 'TaskVersion']} })
    version: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    name: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'TaskVersion']} })
    dispatch_target: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    identity: Optional[Any] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    scheduling: Optional[Any] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    execution: Optional[Any] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    dependencies: Optional[Any] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    event_handling: Optional[Any] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    constraints: Optional[Any] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    published_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    superseded_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    runs_from: date = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    runs_until: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    runs_until_set_by_folder_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })
    created_by: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion']} })


class Plan(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'domain_owned': {'tag': 'domain_owned', 'value': True},
                         'sql_table': {'tag': 'sql_table', 'value': 'plan'}},
         'from_schema': 'https://example.org/gigacron/acid-slice',
         'unique_keys': {'uq_plan_domain_odate': {'unique_key_name': 'uq_plan_domain_odate',
                                                  'unique_key_slots': ['domain_id',
                                                                       'odate']}}})

    plan_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Plan', 'TaskInstance']} })
    domain_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'TaskVersion', 'Plan']} })
    odate: date = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Plan']} })
    state: PlanState = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance']} })
    created_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance', 'Outbox']} })
    updated_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Plan', 'TaskInstance', 'Attempt', 'Outbox']} })


class TaskInstance(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'sql_table': {'tag': 'sql_table', 'value': 'task_instance'}},
         'from_schema': 'https://example.org/gigacron/acid-slice'})

    task_instance_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance', 'Attempt', 'Outbox']} })
    plan_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Plan', 'TaskInstance']} })
    task_version_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TaskVersion', 'TaskInstance']} })
    folder_version_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance']} })
    filled_values: Any = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance']} })
    state: TaskInstanceState = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance']} })
    result: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance']} })
    queued_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance']} })
    run_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance']} })
    no_run_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance']} })
    result_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance']} })
    wake_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance']} })
    wake_on: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance']} })
    created_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance', 'Outbox']} })
    updated_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Plan', 'TaskInstance', 'Attempt', 'Outbox']} })


class Attempt(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'sql_table': {'tag': 'sql_table', 'value': 'attempt'}},
         'from_schema': 'https://example.org/gigacron/acid-slice',
         'unique_keys': {'attempt_pkey': {'unique_key_name': 'attempt_pkey',
                                          'unique_key_slots': ['task_instance_id',
                                                               'attempt_no']}}})

    task_instance_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance', 'Attempt', 'Outbox']} })
    attempt_no: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt', 'Outbox']} })
    agent_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt', 'Outbox']} })
    attempt_state: AttemptState = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt']} })
    exit_code: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt']} })
    dispatching_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt']} })
    dispatched_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt']} })
    running_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt']} })
    unknown_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt']} })
    finished_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt']} })
    started_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt']} })
    ended_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt']} })
    updated_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Plan', 'TaskInstance', 'Attempt', 'Outbox']} })


class Outbox(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'sql_table': {'tag': 'sql_table', 'value': 'outbox'}},
         'from_schema': 'https://example.org/gigacron/acid-slice',
         'rules': [{'description': 'part of ck_outbox_attempt',
                    'postconditions': {'slot_conditions': {'attempt_no': {'name': 'attempt_no',
                                                                          'required': True},
                                                           'task_instance_id': {'name': 'task_instance_id',
                                                                                'required': True}}},
                    'preconditions': {'slot_conditions': {'message_type': {'equals_string': 'COMMAND',
                                                                           'name': 'message_type'}}},
                    'title': 'ck_outbox_attempt (COMMAND names its Attempt)'}]})

    message_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Outbox']} })
    task_instance_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TaskInstance', 'Attempt', 'Outbox']} })
    attempt_no: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt', 'Outbox']} })
    agent_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Attempt', 'Outbox']} })
    message_type: OutboxMessageType = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Outbox']} })
    payload: Any = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Outbox']} })
    delivery_state: OutboxDeliveryState = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Outbox']} })
    leased_until: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Outbox']} })
    created_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Task', 'Folder', 'Plan', 'TaskInstance', 'Outbox']} })
    leased_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Outbox']} })
    sent_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Outbox']} })
    acked_at: Optional[datetime ] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Outbox']} })
    updated_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Domain', 'Plan', 'TaskInstance', 'Attempt', 'Outbox']} })


class AuditEvent(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'sql_table': {'tag': 'sql_table', 'value': 'audit_event'}},
         'from_schema': 'https://example.org/gigacron/acid-slice'})

    audit_event_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    event_type_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    audited_entity_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    entity_id: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    from_state: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    to_state: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    principal: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    ticket_ref: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    detail: Optional[Any] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    recorded_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    effective_at: datetime  = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })
    supersedes_event_id: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['AuditEvent']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Domain.model_rebuild()
Task.model_rebuild()
Folder.model_rebuild()
TaskVersion.model_rebuild()
Plan.model_rebuild()
TaskInstance.model_rebuild()
Attempt.model_rebuild()
Outbox.model_rebuild()
AuditEvent.model_rebuild()
