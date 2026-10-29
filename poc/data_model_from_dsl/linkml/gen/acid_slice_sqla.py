
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class Any(Base):
    """
    Opaque JSON payload.
    """
    __tablename__ = 'Any'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    

    def __repr__(self):
        return f"Any(id={self.id},)"



    


class Domain(Base):
    """
    None
    """
    __tablename__ = 'Domain'

    domain_id = Column(Integer(), primary_key=True, nullable=False )
    name = Column(Text(), nullable=False )
    timezone = Column(Text(), nullable=False )
    odate_boundary_time = Column(Time(), nullable=False )
    projection_horizon = Column(Integer(), nullable=False )
    heartbeat_interval = Column(Integer(), nullable=False )
    liveness_threshold = Column(Integer(), nullable=False )
    state = Column(Enum('DRAFT', 'ACTIVE', 'INACTIVE', 'RETIRED', name='DomainState'), nullable=False )
    created_at = Column(DateTime(), nullable=False )
    state_changed_at = Column(DateTime(), nullable=False )
    updated_at = Column(DateTime(), nullable=False )
    

    def __repr__(self):
        return f"Domain(domain_id={self.domain_id},name={self.name},timezone={self.timezone},odate_boundary_time={self.odate_boundary_time},projection_horizon={self.projection_horizon},heartbeat_interval={self.heartbeat_interval},liveness_threshold={self.liveness_threshold},state={self.state},created_at={self.created_at},state_changed_at={self.state_changed_at},updated_at={self.updated_at},)"



    


class Task(Base):
    """
    None
    """
    __tablename__ = 'Task'

    task_id = Column(Integer(), primary_key=True, nullable=False )
    domain_id = Column(Integer(), ForeignKey('Domain.domain_id'), nullable=False )
    state = Column(Enum('ACTIVE', 'INACTIVE', 'RETIRED', name='TaskState'), nullable=False )
    created_at = Column(DateTime(), nullable=False )
    state_changed_at = Column(DateTime(), nullable=False )
    

    def __repr__(self):
        return f"Task(task_id={self.task_id},domain_id={self.domain_id},state={self.state},created_at={self.created_at},state_changed_at={self.state_changed_at},)"



    


class Folder(Base):
    """
    None
    """
    __tablename__ = 'Folder'

    folder_id = Column(Integer(), primary_key=True, nullable=False )
    domain_id = Column(Integer(), ForeignKey('Domain.domain_id'), nullable=False )
    kind = Column(Enum('ROOT', 'REGULAR', 'SMART', name='FolderKind'), nullable=False )
    state = Column(Enum('ACTIVE', 'INACTIVE', 'RETIRED', name='FolderState'), nullable=False )
    created_at = Column(DateTime(), nullable=False )
    state_changed_at = Column(DateTime(), nullable=False )
    

    def __repr__(self):
        return f"Folder(folder_id={self.folder_id},domain_id={self.domain_id},kind={self.kind},state={self.state},created_at={self.created_at},state_changed_at={self.state_changed_at},)"



    


class TaskVersion(Base):
    """
    None
    """
    __tablename__ = 'TaskVersion'

    task_version_id = Column(Integer(), primary_key=True, nullable=False )
    task_id = Column(Integer(), ForeignKey('Task.task_id'), nullable=False )
    domain_id = Column(Integer(), ForeignKey('Domain.domain_id'), nullable=False )
    folder_id = Column(Integer(), ForeignKey('Folder.folder_id'), nullable=False )
    version = Column(Integer(), nullable=False )
    name = Column(Text(), nullable=False )
    dispatch_target = Column(Text())
    published_at = Column(DateTime(), nullable=False )
    superseded_at = Column(DateTime())
    runs_from = Column(Date(), nullable=False )
    runs_until = Column(Date())
    runs_until_set_by_folder_id = Column(Integer(), ForeignKey('Folder.folder_id'))
    created_by = Column(Text(), nullable=False )
    identity_id = Column(Integer(), ForeignKey('Any.id'))
    identity = relationship("Any", uselist=False, foreign_keys=[identity_id])
    scheduling_id = Column(Integer(), ForeignKey('Any.id'))
    scheduling = relationship("Any", uselist=False, foreign_keys=[scheduling_id])
    execution_id = Column(Integer(), ForeignKey('Any.id'))
    execution = relationship("Any", uselist=False, foreign_keys=[execution_id])
    dependencies_id = Column(Integer(), ForeignKey('Any.id'))
    dependencies = relationship("Any", uselist=False, foreign_keys=[dependencies_id])
    event_handling_id = Column(Integer(), ForeignKey('Any.id'))
    event_handling = relationship("Any", uselist=False, foreign_keys=[event_handling_id])
    constraints_id = Column(Integer(), ForeignKey('Any.id'))
    constraints = relationship("Any", uselist=False, foreign_keys=[constraints_id])
    

    def __repr__(self):
        return f"TaskVersion(task_version_id={self.task_version_id},task_id={self.task_id},domain_id={self.domain_id},folder_id={self.folder_id},version={self.version},name={self.name},dispatch_target={self.dispatch_target},published_at={self.published_at},superseded_at={self.superseded_at},runs_from={self.runs_from},runs_until={self.runs_until},runs_until_set_by_folder_id={self.runs_until_set_by_folder_id},created_by={self.created_by},identity_id={self.identity_id},scheduling_id={self.scheduling_id},execution_id={self.execution_id},dependencies_id={self.dependencies_id},event_handling_id={self.event_handling_id},constraints_id={self.constraints_id},)"



    


class Plan(Base):
    """
    None
    """
    __tablename__ = 'Plan'

    plan_id = Column(Integer(), primary_key=True, nullable=False )
    domain_id = Column(Integer(), ForeignKey('Domain.domain_id'), nullable=False )
    odate = Column(Date(), nullable=False )
    state = Column(Enum('PENDING', 'OPEN', 'CLOSED', name='PlanState'), nullable=False )
    created_at = Column(DateTime(), nullable=False )
    updated_at = Column(DateTime(), nullable=False )
    

    def __repr__(self):
        return f"Plan(plan_id={self.plan_id},domain_id={self.domain_id},odate={self.odate},state={self.state},created_at={self.created_at},updated_at={self.updated_at},)"



    


class TaskInstance(Base):
    """
    None
    """
    __tablename__ = 'TaskInstance'

    task_instance_id = Column(Integer(), primary_key=True, nullable=False )
    plan_id = Column(Integer(), ForeignKey('Plan.plan_id'), nullable=False )
    task_version_id = Column(Integer(), ForeignKey('TaskVersion.task_version_id'), nullable=False )
    folder_version_id = Column(Integer())
    state = Column(Enum('WAITING', 'QUEUED', 'RUN', 'NO_RUN', name='TaskInstanceState'), nullable=False )
    result = Column(Text())
    queued_at = Column(DateTime())
    run_at = Column(DateTime())
    no_run_at = Column(DateTime())
    result_at = Column(DateTime())
    wake_at = Column(DateTime())
    wake_on = Column(Text())
    created_at = Column(DateTime(), nullable=False )
    updated_at = Column(DateTime(), nullable=False )
    filled_values_id = Column(Integer(), ForeignKey('Any.id'), nullable=False )
    filled_values = relationship("Any", uselist=False, foreign_keys=[filled_values_id])
    

    def __repr__(self):
        return f"TaskInstance(task_instance_id={self.task_instance_id},plan_id={self.plan_id},task_version_id={self.task_version_id},folder_version_id={self.folder_version_id},state={self.state},result={self.result},queued_at={self.queued_at},run_at={self.run_at},no_run_at={self.no_run_at},result_at={self.result_at},wake_at={self.wake_at},wake_on={self.wake_on},created_at={self.created_at},updated_at={self.updated_at},filled_values_id={self.filled_values_id},)"



    


class Attempt(Base):
    """
    None
    """
    __tablename__ = 'Attempt'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    task_instance_id = Column(Integer(), ForeignKey('TaskInstance.task_instance_id'), nullable=False )
    attempt_no = Column(Integer(), nullable=False )
    agent_id = Column(Integer(), nullable=False )
    attempt_state = Column(Enum('DISPATCHING', 'DISPATCHED', 'RUNNING', 'SUCCEEDED', 'FAILED', 'UNKNOWN', name='AttemptState'), nullable=False )
    exit_code = Column(Integer())
    dispatching_at = Column(DateTime(), nullable=False )
    dispatched_at = Column(DateTime())
    running_at = Column(DateTime())
    unknown_at = Column(DateTime())
    finished_at = Column(DateTime())
    started_at = Column(DateTime())
    ended_at = Column(DateTime())
    updated_at = Column(DateTime(), nullable=False )
    

    def __repr__(self):
        return f"Attempt(id={self.id},task_instance_id={self.task_instance_id},attempt_no={self.attempt_no},agent_id={self.agent_id},attempt_state={self.attempt_state},exit_code={self.exit_code},dispatching_at={self.dispatching_at},dispatched_at={self.dispatched_at},running_at={self.running_at},unknown_at={self.unknown_at},finished_at={self.finished_at},started_at={self.started_at},ended_at={self.ended_at},updated_at={self.updated_at},)"



    


class Outbox(Base):
    """
    None
    """
    __tablename__ = 'Outbox'

    message_id = Column(Integer(), primary_key=True, nullable=False )
    task_instance_id = Column(Integer())
    attempt_no = Column(Integer())
    agent_id = Column(Integer(), nullable=False )
    message_type = Column(Enum('COMMAND', 'COMMAND_OFFER', 'CONTROL', name='OutboxMessageType'), nullable=False )
    delivery_state = Column(Enum('PENDING', 'LEASED', 'SENT', 'ACKED', name='OutboxDeliveryState'), nullable=False )
    leased_until = Column(DateTime())
    created_at = Column(DateTime(), nullable=False )
    leased_at = Column(DateTime())
    sent_at = Column(DateTime())
    acked_at = Column(DateTime())
    updated_at = Column(DateTime(), nullable=False )
    payload_id = Column(Integer(), ForeignKey('Any.id'), nullable=False )
    payload = relationship("Any", uselist=False, foreign_keys=[payload_id])
    

    def __repr__(self):
        return f"Outbox(message_id={self.message_id},task_instance_id={self.task_instance_id},attempt_no={self.attempt_no},agent_id={self.agent_id},message_type={self.message_type},delivery_state={self.delivery_state},leased_until={self.leased_until},created_at={self.created_at},leased_at={self.leased_at},sent_at={self.sent_at},acked_at={self.acked_at},updated_at={self.updated_at},payload_id={self.payload_id},)"



    


class AuditEvent(Base):
    """
    None
    """
    __tablename__ = 'AuditEvent'

    audit_event_id = Column(Integer(), primary_key=True, nullable=False )
    event_type_id = Column(Integer(), nullable=False )
    audited_entity_id = Column(Integer(), nullable=False )
    entity_id = Column(Integer(), nullable=False )
    from_state = Column(Text())
    to_state = Column(Text(), nullable=False )
    principal = Column(Text(), nullable=False )
    ticket_ref = Column(Text())
    recorded_at = Column(DateTime(), nullable=False )
    effective_at = Column(DateTime(), nullable=False )
    supersedes_event_id = Column(Integer(), ForeignKey('AuditEvent.audit_event_id'))
    detail_id = Column(Integer(), ForeignKey('Any.id'))
    detail = relationship("Any", uselist=False, foreign_keys=[detail_id])
    

    def __repr__(self):
        return f"AuditEvent(audit_event_id={self.audit_event_id},event_type_id={self.event_type_id},audited_entity_id={self.audited_entity_id},entity_id={self.entity_id},from_state={self.from_state},to_state={self.to_state},principal={self.principal},ticket_ref={self.ticket_ref},recorded_at={self.recorded_at},effective_at={self.effective_at},supersedes_event_id={self.supersedes_event_id},detail_id={self.detail_id},)"



    


