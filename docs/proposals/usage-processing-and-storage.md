---
schema_version: 2
title: "Usage Processing and Persistent Storage"
status: open
owner: agent-factory
created: 2026-07-28
updated: 2026-07-29
supersedes:

impact:
  scope: cross_project
  architecture_change: true
  external_contract_change: true
  boundaries:
    - factory/scripts/usage-capture
    - docs/spec/supplementary_specs/interface-contracts.md

governance:
  assurance: critical
  risk_domains:
    - data_integrity
    - operations
    - privacy
    - reliability
    - security

estimate:
  as_of: 2026-07-29
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Feature Request: Usage Processing and Persistent Storage

## Summary

Add a processing layer between raw CLI usage capture and reporting. Raw
captures become a crash-safe ingestion spool; a projector converts cumulative,
CLI-specific snapshots into interaction deltas stored in PostgreSQL. A
repository-provided Docker deployment supports local use, while environment
configuration permits remote or existing PostgreSQL clusters. Processing and
storage live in a separate `usage/` subproject and bounded context. Grafana
provides standard dashboards; Marimo provides reproducible exploratory
analysis.

## Motivation

Claude, Codex, and Copilot can repeatedly capture growing transcripts and
cumulative counters. This wastes storage and makes correct aggregation depend
on CLI-specific reader rules. A durable normalized store should remove that
redundancy without making lifecycle hooks stateful or fragile.

## Core Principles

- Capture stays fast, immutable, and best-effort.
- The database becomes the durable source of truth.
- Ingestion is transactional, idempotent, and replay-safe.
- CLI-specific inclusion and attribution rules remain explicit.
- Storage location is deployment configuration, not application logic.
- The raw spool contract is the only integration surface between Factory and
  Usage Accounting.
- Visualization reads stable database views through read-only credentials.

## Design

`factory/` owns CLI hooks, normalization, and atomic raw-spool writes. The new
`usage/` subproject owns ingestion, projection, PostgreSQL persistence,
retention, and reporting views. Neither `orchestrator/` nor Factory depends on
database availability.

1. Factory hooks atomically write a raw JSON record and transcript into an
   ingestion spool defined by a versioned contract.
2. The Usage Accounting projector validates records in session sequence,
   derives counter and transcript deltas, and writes canonical interactions to
   PostgreSQL.
3. Each transaction records the source `record_id`, source hash, projection
   version, session relationship, provider deltas, and new transcript events.
4. After a durable commit, the projector deletes the processed spool files.
   Invalid or unprojectable captures remain quarantined.
5. Reports read database views that encode each CLI's root/child accounting
   rules.

If transcript continuity or cumulative-counter monotonicity cannot be proven,
the projector stores a full checkpoint instead of a delta.

The repository provides a Docker Compose service with a named PostgreSQL volume
for durable local operation. The projector reads a standard PostgreSQL
connection URL from environment configuration; the same interface connects to
the local container, a remote deployment, or an existing cluster. Secrets stay
outside tracked files, and the supplied `.env.example` contains names and safe
defaults only.

Grafana is the primary visualization layer. Provisioned data sources and
version-controlled dashboards show usage over time, CLI/model/agent
attribution, cache ratios, session consumption, ingestion health, and projection
failures. Grafana connects through a dedicated PostgreSQL role restricted to
reporting views and runs as an optional Docker Compose profile.

Marimo is the exploratory analysis layer. Version-controlled Python notebooks
query the same reporting views for session investigations, accounting
validation, anomaly analysis, and new metric development. Its reactive model
and built-in Altair/Vega visualization support make it preferable to Jupyter
for this subproject.

## Scope

**In the first release:**

- A `usage/` subproject with its own context documentation, source, tests, and
  architecture.
- A versioned raw-spool contract owned by Factory and consumed by Usage
  Accounting.
- PostgreSQL schema and migrations, transactional projector, retry-safe
  cleanup, checkpoints, and per-CLI accounting views.
- Docker Compose service with a named persistent volume, health check, and
  local development defaults.
- Environment-based connection configuration for local, remote, and existing
  PostgreSQL deployments.
- Optional Grafana Compose profile with provisioned read-only data source and
  version-controlled starter dashboards.
- Version-controlled Marimo notebooks for exploratory analysis and accounting
  validation.

**Explicitly deferred (do NOT plan stories for these):**

- Managed database provisioning, custom visualization applications, cost
  pricing, synchronization, and multi-host ingestion coordination.
- Jupyter notebooks and self-service BI deployments such as Apache Superset or
  Metabase.

## Open Questions

- Should successfully processed spool files be deleted immediately or retained
  for a short configurable grace period?
- Is owner-only filesystem protection sufficient, or should transcript content
  also be encrypted at rest?
- Which TLS modes must the first release support for remote connections?
- Should an existing cluster use a dedicated database, a dedicated schema, or
  support both?
- Which Grafana authentication modes are required beyond local development?

## Completion Criteria

- Reprocessing the same capture cannot duplicate usage.
- A crash at any ingestion boundary loses neither raw nor committed data.
- Factory capture continues when Usage Accounting or PostgreSQL is unavailable.
- Session totals conserve provider usage without double-counting children.
- Stored transcript content contains deltas except at explicit checkpoints.
- The database can rebuild all reporting views from canonical stored facts.
- Local data survives container recreation through the named volume.
- Changing only environment configuration can target an existing or remote
  PostgreSQL cluster without changing application code.
- Grafana starts from provisioned configuration and cannot mutate accounting
  tables.
- Marimo notebooks run against the same documented reporting interface without
  privileged database credentials.

## Guiding Rule

Capture evidence first; interpret it transactionally; delete it only after the
durable representation is complete.
