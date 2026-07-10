# 0019. The findings store remains the review loop's source of truth

**Status**: Accepted — closes the "Future" note of [ADR-0011](0011-reviewer-findings-ingest-contract.md) and the open item left by [ADR-0012](0012-ingest-findings-from-filed-markdown.md); resolves ST-0021.

## Context

Findings are represented in two places. The orchestrator's `.orchestrator/findings/FND-NNNN.json` store (ADR-0004) is the loop's own bookkeeping: one schema-validated file per finding, an orchestrator-owned monotonic id, a three-state lifecycle (`open → superseded | resolved`), and `phase`/`iteration` scoping — everything BR-014, BR-019, and SF-04 depend on. The review agents also file `docs/findings/<TAG>-NNNN.md` under the toolset-wide convention in [FINDING-FILING.md](../../../skills/_shared/FINDING-FILING.md), shared by every review skill in this repo, not just the orchestrator. ADR-0012 made the filed markdown the *ingestion source*: `DefaultFindingIngestor.ingest_open_findings` reads every `open` file and projects it into the JSON store, which stamps the id, phase, and iteration. ADR-0012 explicitly left open which of the two stores is authoritative and what becomes of the other — that is ST-0021.

Two structural facts, not visible until the filing convention is read closely, bound the answer:

- **Schema mismatch.** `docs/findings/*.md` frontmatter has a two-state `status` (`open | resolved`, no `superseded`) and no `phase` or `iteration` field. The store's three-state lifecycle and per-cycle scoping — the exact mechanism BR-014 and SF-04 depend on — has no equivalent there today.
- **Identity mismatch.** The markdown `id` (`<TAG>-NNNN`, e.g. `SPEC-0001`) is allocated by the **filing agent**, scanning existing files of the same tag (FINDING-FILING.md, "Allocate the next NNNN by scanning existing files with the same tag"). It is a reference code for the human-facing record, not the loop's identity. The current ingestor already keeps these separate: the markdown `id` maps onto `Finding.code`; `Finding.id` (`FND-NNNN`) is always minted by `FindingsStore.next_id()`. Collapsing the two stores into one would either graft phase/iteration/supersession onto a frontmatter schema owned by the whole toolset (out of this story's — and this project's — authority), or hand id-minting to the filing agent, which is a direct BR-019 violation.

Since ADR-0012, the JSON store's per-finding content (`code`, `severity`, `artifact`, `message`) is never independently authored — it is always derived from the markdown file at ingest time. The "drift" ADR-0011 warned about was specifically the interim stdout block versus the filed markdown (two independently-authored outputs of the same reviewer pass, which could diverge if the reviewer was careless); ADR-0012 already removed that channel. What remains is not drift between two sources of truth, but a derived index (the JSON store) built from one input (the markdown files) — a normal projection, not a duplication risk.

### Alternatives (Pugh Matrix)

Baseline **A**: keep the status quo — the JSON store is the loop's sole authority (identity, lifecycle, phase/iteration scoping); `docs/findings/*.md` remains the filing contract and ingestion input, unchanged. **B**: retire the JSON store; make the markdown files the loop's only store. **C**: retire `docs/findings/*.md`; have the orchestrator generate its own human-facing record from the JSON store and stop review agents from filing locally. **D**: extend the markdown frontmatter schema (add `phase`, `iteration`, a `superseded` status) so it can fully replace the JSON store.

| Criterion                                                          | Weight | A: keep both, roles unchanged | B: markdown-only | C: JSON-only | D: extend markdown schema |
| ------------------------------------------------------------------ | ------ | ----------------------------- | ---------------- | ------------ | ------------------------- |
| Determinism — loop-exit and supersession stay exact (Q1)           | 3      | 0                             | -3               | -1           | -1                        |
| Safety — BR-019 id ownership, no change to a proven mechanism (Q3) | 3      | 0                             | -3               | -1           | -2                        |
| Portability / scope — no change to a cross-toolset convention (Q5) | 2      | 0                             | -2               | -2           | -2                        |
| Operability — durable, human-legible record survives (Q4)          | 2      | 0                             | -1               | -2           | 0                         |
| Minimal dependencies / migration cost (Q7)                         | 1      | 0                             | -1               | -1           | -1                        |
| **Weighted total**                                                 |        | **0**                         | **-19**          | **-13**      | **-13**                   |

A wins by a wide margin. **B** requires the loop's three-state lifecycle and phase/iteration scoping to be reconstructed on a two-state, unscoped schema owned by every review skill in the toolset, not just the orchestrator — and moves id-minting to the filing agent, breaking BR-019 outright. **C** keeps the loop's invariants intact but deletes the toolset's local-first finding record for every non-orchestrator use of the review skills (spec review, Fagan, security, ATAM, bug hunts run standalone) — a much larger blast radius than this story's scope. **D** still requires coordinating a schema change across every skill that files findings, and, once the phase/iteration/supersession fields exist there, is functionally the JSON store re-expressed in markdown — no dependency is actually removed, and every git-diffable finding file grows a rewritten frontmatter block on every cycle it stays open, which is worse for Q4 than today's file-per-finding JSON.

## Decision

The **`.orchestrator/findings/FND-NNNN.json` store remains the review loop's single source of truth**, unchanged from ADR-0004/ADR-0012. `docs/findings/*.md` remains the filing contract and the ingestion input, also unchanged — it is not promoted to a second store, and it is not retired.

- The relationship is one-directional: `docs/findings/*.md` → `FindingIngestor.ingest_open_findings` → `FindingsStore`. The store is a per-run **projection** of the filed files, never the reverse; no finding's content is independently authored in both places (true since ADR-0012, now made explicit).
- `Finding.id` (`FND-NNNN`) and the markdown frontmatter `id` (`<TAG>-NNNN`) are different identifiers for different purposes: the loop's own identity (BR-019, orchestrator-owned, minted by `FindingsStore.next_id()`) versus a human/toolset-facing reference code (owned by the filing agent, mapped onto `Finding.code`). Neither source mints the loop's id; this was already true in the shipped ingestor and is now the recorded decision, not an implementation accident.
- The loop's lifecycle (`open → superseded | resolved`), phase/iteration scoping, cap counting (BR-001/003/014), and the loop-exit predicate (SF-04) are exactly as ADR-0004 and ADR-0012 left them. No migration is required for existing runs — no schema, store, or ingestion-contract code changes.
- The now-permanently-closed ADR-0011 interim mechanism (the stdout `json` block, `map_semantic` in `finding_ingest.py`) is deleted along with its fixtures; it served only the stdout path this decision does not revive.

## Consequences

**Positive**

- ST-0021 is closed without touching a cross-toolset convention (FINDING-FILING.md) or the loop's proven, tested state machine — zero risk to BR-014, BR-019, SF-04, or resume idempotency (FAGAN-0043/0049).
- The "same finding represented twice, and the two can drift" framing in ADR-0011 is retired: the relationship is now documented as store-derived-from-file, not two independent authors of the same fact.
- Dead code from the superseded stdout mechanism (`map_semantic` and its structured-block scanner) is removed, along with the test fixtures that existed only to exercise it.

**Negative / risks**

- The cosmetic accumulation ADR-0012 already flagged stands: a finding that stays `open` across cycles is re-read and re-projected each cycle, leaving one superseded JSON record per cycle behind it. This is unchanged and still adequate at the documented scale (findings per run are tens, not thousands — ADR-0004).
- A finding filed under `docs/findings/*.md` outside an orchestrator run (a standalone review) is never tagged with a phase or iteration and never reaches the loop — this is existing, expected behaviour (the loop only ever reads the files an orchestrator-driven reviewer pass produced), not a new gap introduced here.
