# 0012. Ingest reviewer findings from the filed markdown, not stdout

**Status**: Accepted (supersedes the ingest mechanism of [ADR-0011](0011-reviewer-findings-ingest-contract.md))

> **Superseded for the orchestrator, 2026-07-12 (PhaseRunner collapse):** Findings ingestion moved to `factory/`; the orchestrator no longer reads `docs/findings/*.md` or writes findings. The `FindingsStore` JSON store itself remains in the orchestrator, now read-only. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`.

## Context

[ADR-0011](0011-reviewer-findings-ingest-contract.md) chose option A — the reviewer ends its output with a fenced `json` findings block and the orchestrator ingests that block from stdout — as the interim contract, recording option C (read the filed `docs/findings/*.md` files) as the intended evolution once the two finding stores were reconciled.

Option A then failed in practice. Requirements and reviews run through the interactive adapter path, which hands the terminal to the human and does not capture stdout (`_invoke_interactive` returns `stdout=""`). Ingesting from stdout therefore yielded nothing for every interactive review: `open_count` was zero and the phase auto-approved regardless of findings (ST-0022, observed live — the reviewer filed two `docs/findings/SPEC-*.md` files while `.orchestrator/findings/` stayed empty). The stdout channel is simply not available in the mode the review phases actually use.

The Pugh matrix in ADR-0011 already scored option C well on determinism and legibility; its only debit was the store-model reconciliation it appeared to require. That debit does not apply to the *ingestion source* alone: the loop can read the filed files and continue to project them into the existing findings store, leaving the store model (and its loop-exit, supersession, and status queries) untouched.

## Decision

The orchestrator ingests reviewer findings by **reading the agent-filed `docs/findings/*.md` files**, not the reviewer's stdout.

- The `FindingIngestor` port exposes `ingest_open_findings(phase, iteration)`. `DefaultFindingIngestor` scans `docs/findings/*.md`, takes every finding whose frontmatter `status` is `open`, maps it onto the finding DTO (id → `code`, the review-scale severity → `error|warning|info`, `artifact`, the title as `message`), and writes it to the store, which stamps the monotonic id and tags the cycle (BR-019).
- The store, the cycle tagging, supersession, and the loop-exit predicate (SF-04) are unchanged; only the *source* of a review's findings changes from stdout to the filed files.
- The reviewer no longer needs to emit a machine-readable block; filing the findings as `docs/findings/*.md` (which the agents already do) is the whole contract.

## Consequences

**Positive**

- Works in every mode. Interactive reviews now drive the loop, because the findings are read from disk, not from uncaptured stdout — the ST-0022 defect is closed.
- One artifact, not two. The findings the human reads are exactly the ones the loop counts; the stdout echo and its drift risk are gone.
- No store-model change. The proven loop machinery (open-count, supersede, cap) is reused as-is.

**Negative / risks**

- A finding that stays `open` across cycles is re-read and re-ingested each cycle, creating a superseded record per cycle in the JSON store. This is cosmetic — the loop counts only the latest cycle — but the store accumulates more records than strictly necessary.
- The store still duplicates what `docs/findings/` holds. Full unification — making the files the single source of truth and retiring or projecting the JSON store — remains open under **ST-0021**; this ADR moves the ingestion source there without yet retiring the store.

**Resolved by [ADR-0019](0019-findings-store-remains-the-loop-source-of-truth.md)**: the JSON store keeps the loop-state role (identity, lifecycle, phase/iteration scoping); the filed markdown stays the ingestion input, formally a projection source rather than a second store. No further store-model change follows from ST-0021.
