---
schema_version: 2
title: Jira Server to Cloud Migration
status: draft
owner: md@matthiasdaues.de
created: 2026-09-23
updated: 2026-09-23
supersedes:

impact:
  scope: local
  architecture_change: false
  external_contract_change: true
  boundaries:
    - Jira Cloud REST API v3

governance:
  assurance: elevated
  risk_domains:
    - data_integrity
    - operations

estimate:
  as_of: 2026-09-23
  basis: judgment
  confidence: low
  human_review_hours:
    min: 2.0
    max: 6.0
  normalized_tokens: unknown
  estimated_consumption: unknown
---

# Feature Request: Jira Server to Cloud Migration

## Summary

A Python migration tool that imports 5,500 Jira tickets from an on-premise Jira Enterprise Server (project GB) into Atlassian Cloud Jira (project GX) via the REST API, preserving issue key numbering (GB-NNNN to GX-NNNN) and parent-child relationships. The source data is a CSV export; authentication uses a universal PAT.

## Motivation

The organisation is decommissioning its Jira Enterprise Server installation and moving to Atlassian Cloud. Atlassian's built-in CSV importer does not guarantee issue key ordering and offers no control over parent-child creation sequence. A custom migration tool is needed to preserve the numbering scheme that external references, documentation, and team memory depend on.

## Core Principles

- The PAT never enters conversation context or version control; it is read from the environment at runtime.
- Issue numbering must be deterministic: GB-N maps to GX-N for every N.
- The migration must be resumable: a failure at ticket 3,200 does not require restarting from scratch.
- Validate the full pipeline against dummy data before touching production data.

## Design

### Two-pass creation strategy

Jira Cloud auto-assigns sequential issue keys. Direct key assignment is not possible via the API. To preserve numbering:

1. **First pass — create issues in strict ascending key order.** The target project (GX) must be empty. For gaps in the old numbering sequence (e.g., GB-42 exists but GB-43 does not), create placeholder issues to consume the key slot, then close them.
2. **Second pass — set parent-child links.** After all issues exist, update each child with its parent reference via the REST API. This decouples the creation-order constraint (ascending by number) from the dependency constraint (parent before child).

### Bulk create with ordering guarantee

The Jira Cloud bulk create endpoint (`/rest/api/3/issue/bulk`) accepts up to 50 issues per request. Batches are sent in strict numerical sequence. The script verifies returned keys match expected values before sending the next batch. A mismatch halts the run.

### Rate limiting and resilience

- Exponential backoff with jitter on 429 and 5xx responses.
- Configurable request rate ceiling (default: 50 requests/second).
- Per-request timeout with retry (3 attempts).

### Resumability

A progress log (JSON lines) records every created issue: old key, new key, HTTP status, timestamp. On restart, the script reads the log, determines the last successfully created key, and resumes from the next number.

### Authentication

Basic auth header: `email:PAT`, base64-encoded. The PAT is read from `JIRA_PAT` environment variable. The email is read from `JIRA_EMAIL` environment variable or a config file.

### Rough volume estimate

- ~5,500 real tickets plus gap placeholders (count depends on highest GB key number).
- ~110+ bulk-create calls (first pass).
- ~5,500 parent-link update calls (second pass).
- Estimated wall-clock time at conservative pacing: 15-30 minutes.

## Scope

**In the first release:**

- Parse Jira CSV export into an ordered list of issue records.
- Detect gaps in the key sequence and generate placeholder records.
- Bulk-create issues in ascending key order with key verification.
- Set parent-child links in a second pass.
- Progress log for resumability.
- Dry-run mode that logs planned actions without calling the API.
- Dummy data generator for validation against a test project.

**Explicitly deferred (do NOT plan stories for these):**

- Migration of attachments, comments, or worklogs.
- Migration of custom field definitions or workflow configurations.
- Bidirectional sync or rollback tooling.
- Atlassian-native migration tools (out of scope by design).

## Design Details

- **Placeholder issues** are created with summary "[PLACEHOLDER — key reservation]", issue type "Task", and status "Done". They exist solely to consume a key slot.
- **Key verification** after each bulk-create batch: the script asserts that the Nth issue in the response has key GX-N. A mismatch is a hard stop — manual investigation is required because all subsequent keys would be off by one.
- **Field mapping** from CSV columns to Jira Cloud fields is configured in a YAML mapping file, not hard-coded.
- **Old-to-new key mapping** is written as a CSV artifact after migration completes, for use by downstream reference-update scripts.

## Open Questions

- What is the highest ticket number in GB? This determines the number of gap placeholders.
- Which CSV columns map to which Jira Cloud fields? Need a sample CSV to define the mapping.
- Are there issue types beyond the standard set (Epic, Story, Task, Bug, Sub-task)?
- Does the GX project already exist, or must it be created programmatically?
- Are there cross-project links (to projects other than GB) that need rewriting?

## Completion Criteria

- A test run against a throwaway Jira Cloud project (e.g., TX) with ~50 dummy tickets, including gaps and parent-child links, succeeds with correct key numbering and intact links.
- The full migration of ~5,500 tickets completes with a verified old-to-new key mapping.
- Every parent-child relationship in the source CSV is reproduced in the target project.
- The progress log enables a resumed run to complete without duplicating issues.

## Guiding Rule

The migration must be verifiably correct in numbering and relationships, or it must stop and say why — never silently proceed with wrong keys.
