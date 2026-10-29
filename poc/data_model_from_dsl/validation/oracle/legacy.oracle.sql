-- Spike code: Oracle DDL in the style of a legacy schema, for sql2dbml --oracle.
CREATE TABLE domain (
  domain_id NUMBER(19) NOT NULL,
  name VARCHAR2(200) NOT NULL,
  state VARCHAR2(16) NOT NULL,
  CONSTRAINT domain_pkey PRIMARY KEY (domain_id),
  CONSTRAINT uq_domain_name UNIQUE (name),
  CONSTRAINT ck_domain_state CHECK (state IN ('DRAFT', 'ACTIVE', 'INACTIVE', 'RETIRED'))
);
CREATE TABLE task (
  task_id NUMBER(19) NOT NULL,
  domain_id NUMBER(19) NOT NULL,
  CONSTRAINT task_pkey PRIMARY KEY (task_id),
  CONSTRAINT uq_task_domain UNIQUE (domain_id, task_id),
  CONSTRAINT task_domain_fk FOREIGN KEY (domain_id) REFERENCES domain (domain_id)
);
CREATE TABLE task_version (
  task_version_id NUMBER(19) NOT NULL,
  task_id NUMBER(19) NOT NULL,
  domain_id NUMBER(19) NOT NULL,
  version NUMBER(10) NOT NULL,
  scheduling CLOB,
  runs_from DATE NOT NULL,
  runs_until DATE,
  superseded_at TIMESTAMP WITH TIME ZONE,
  CONSTRAINT task_version_pkey PRIMARY KEY (task_version_id),
  CONSTRAINT uq_task_version_number UNIQUE (task_id, version),
  CONSTRAINT task_version_task_fk FOREIGN KEY (domain_id, task_id) REFERENCES task (domain_id, task_id),
  CONSTRAINT ck_task_version_range CHECK (runs_until IS NULL OR runs_until >= runs_from)
);
CREATE UNIQUE INDEX uq_task_version_current ON task_version (CASE WHEN superseded_at IS NULL THEN task_id END);
