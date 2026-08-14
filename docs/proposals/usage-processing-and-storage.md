---
schema_version: 2
title: "Usage Processing and Persistent Storage"
status: accepted
owner: agent-factory
created: 2026-07-28
updated: 2026-08-06
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
- A versioned raw-spool domain contract, published by Factory as its owning
  publisher and consumed by Usage Accounting as a range-accepting consumer,
  living in a root-level `contracts/` folder (JSON Schema + version field +
  compatibility policy, enforced by a deterministic gate).
- PostgreSQL schema and migrations, transactional projector, retry-safe
  cleanup, checkpoints, and per-CLI accounting views.
- Docker Compose service with a named persistent volume, health check, and
  local development defaults.
- Exchangeable connection, schema, and table configuration sourced from an
  `.env` file, GitHub secrets, or AWS Secrets Manager behind one interface,
  for local, remote, and existing PostgreSQL deployments.
- Optional Grafana Compose profile with provisioned read-only data source and
  version-controlled starter dashboards.
- Version-controlled Marimo notebooks for exploratory analysis and accounting
  validation.

**Explicitly deferred (do NOT plan stories for these):**

- Managed database provisioning, custom visualization applications, cost
  pricing, synchronization, and multi-host ingestion coordination.
- Jupyter notebooks and self-service BI deployments such as Apache Superset or
  Metabase.

## Decisions (resolved at intake, 2026-07-29)

- **Domain boundary**: the `usage/` subproject is an isolated bounded domain
  with its own full requirement-generation phase (own PRD, actor-goal list,
  use cases, and supplementary specs). The raw spool file format is the
  versioned domain contract between Factory (capture) and `usage/` (storage +
  analysis); so long as the spool contract does not break, storage and
  analysis are an independent use case and decouple from Factory's evolution.
  The implementation stack (language, dependency model) is an architecture-
  phase decision, deferred.

- **Contract home**: cross-context machine-consumed contracts live in a
  versioned `contracts/` folder at the repo root (artifact class distinct from
  `docs/spec/` prose and `docs/adr/` decisions). The spool contract is a
  published, single-owner artifact — Factory is the owning publisher, `usage/`
  the range-accepting consumer — so `contracts/` is a set of owned published
  artifacts, not a no-man's land. Each contract carries its own frontmatter
  (owner context, version, compatibility policy) and is enforced by a
  deterministic gate (schema validity, producer conformance, consumer major-
  range acceptance). Prose explanation stays in `docs/`.

- **Spool retention**: successfully processed spool files are deleted
  immediately after durable commit. Recorded `record_id` / source-hash
  metadata is the audit trail; failures go to the configurable quarantine.

- **Transcript encryption at rest**: owner-only filesystem protection
  (capture already enforces `0700`/`0600`) is sufficient for release 1.
  Explicit transcript encryption-at-rest is deferred.

- **TLS modes**: release 1 supports `disable` (local container) and
  `verify-full` (cert-verifying safe default for remote/existing clusters),
  with libpq `sslmode` pass-through so `require` / `verify-ca` work without
  code changes.

- **Existing-cluster layout**: support both a dedicated database and a
  dedicated schema. The projector connects with a dedicated role that
  `CREATE SCHEMA` in a configurable database (default a dedicated
  `factory_usage` database, with an option to point at an existing DB's
  dedicated schema). Connection, schema, and table configuration are
  exchangeable parameters sourced from an `.env` file, GitHub secrets, or AWS
  Secrets Manager behind one interface.

- **Grafana authentication**: local dev uses anonymous/`admin` for the optional
  Compose profile. SSO/OAuth is deferred; Grafana is provisioned so auth comes
  from its own configuration.

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
