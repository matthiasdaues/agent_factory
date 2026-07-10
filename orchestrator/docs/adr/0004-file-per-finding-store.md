# 0004. File-per-finding JSON findings store

**Status**: Accepted

## Context

Findings are the source of truth for loop state (FR-E, G4): the loop-exit condition counts `open` findings of the latest iteration, and the store must hold both deterministic findings (from `spec-lint`) and semantic findings (from the reviewer) in the same shape (FR-E3). Every finding must validate against a schema (VR-006), get a unique orchestrator-assigned id (BR-019, VR-007), and be written atomically (BR-017). External ticket tools are explicitly out of scope now but must map cleanly later (NG3, T-04).

The question is the storage substrate for findings.

### Alternatives (Pugh Matrix)

Baseline **A**: a single `findings.json` array. **B**: one JSON file per finding under `findings/`. **C**: a SQLite database. **D**: an external tracker (GitHub Issues) — listed for completeness though excluded by NG3.

| Criterion                                         | Weight | A: single JSON | B: file-per-finding | C: SQLite | D: external tracker |
| ------------------------------------------------- | ------ | -------------- | ------------------- | --------- | ------------------- |
| Determinism — per-record schema validation (Q1)   | 3      | 0              | +1                  | +1        | 0                   |
| Operability — git-diffable, human-readable (Q4)   | 2      | 0              | +1                  | -1        | -1                  |
| Safety — atomic write-then-rename per record (Q3) | 3      | 0              | +1                  | 0         | -1                  |
| Minimal dependencies (Q7)                         | 1      | 0              | 0                   | 0         | -1                  |
| Maps to a future ticket adapter (Q5)              | 2      | 0              | +1                  | 0         | +1                  |
| **Weighted total**                                |        | **0**          | **+10**             | **+2**    | **-4**              |

B wins. A single array (A) forces a whole-file rewrite for every finding — no per-record atomicity and noisy diffs. SQLite (C) validates well and is stdlib, but is opaque to git and needs transactional care for atomicity. An external tracker (D) is excluded by NG3 and adds a network dependency.

## Decision

Store findings as **one JSON file per finding** under `findings/`, each named by its id (`FND-NNNN.json`):

- The orchestrator owns a **monotonic allocator**; each ingested finding gets a unique id on ingest. Sources never mint ids (BR-019, VR-007).
- Every finding is validated against the finding schema ([interface-contracts.md](../spec/supplementary_specs/interface-contracts.md)) before it is accepted (VR-006).
- Deterministic (`spec-lint --format json`) and semantic (reviewer / `inspect-spec`) findings are mapped to the same DTO and land in the same store in the same shape (FR-E3).
- Files are written atomically (write-then-rename); status transitions (`open → superseded | resolved`) rewrite a single file.

## Consequences

**Positive**

- Per-record atomicity: writing or superseding one finding never risks the others (QS-09).
- Findings are git-diffable and human-readable; a review's output is legible in a PR (Q4).
- One record maps one-to-one onto a future ticket, keeping the T-04 adapter simple (Q5).

**Negative / risks**

- Many small files per iteration; directory listing is the query mechanism (adequate at this scale — findings per run are tens, not thousands).
- The monotonic allocator must be crash-safe so ids are never reused; it is part of the atomic-write discipline ([ADR-0005](0005-run-state-lock-and-branch.md)).
