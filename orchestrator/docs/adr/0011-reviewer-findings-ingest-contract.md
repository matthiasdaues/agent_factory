# 0011. Reviewer findings ingested via a fenced JSON block

**Status**: Superseded by [ADR-0012](0012-ingest-findings-from-filed-markdown.md) — the stdout-block mechanism below is replaced by reading the filed `docs/findings/*.md` (the option-C evolution this ADR anticipated). The alternatives analysis remains valid.

> **Superseded for the orchestrator, 2026-07-12 (PhaseRunner collapse):** Reviewer findings ingestion — the whole subject of this ADR — moved to `factory/`; the orchestrator no longer ingests findings. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`.

## Context

The review loop terminates on the findings store: after a reviewer runs, the orchestrator ingests its findings, tags them with the iteration, and counts the open findings of the latest iteration to decide loop-back or approval (FR-E, SF-04, UC-02 §7). Deterministic findings arrive as `spec-lint --format json`; the semantic reviewer's findings must arrive in some parseable form so the orchestrator can map them to the finding DTO.

The review skills instruct the agent to present findings as a human-readable markdown table ([REPORT-FORMAT.md](../../../skills/_shared/REPORT-FORMAT.md)). A table is for the reader, not the parser. The question is how the reviewer communicates its findings to the orchestrator so ingestion is reliable, without sacrificing the human report.

A second store now exists alongside the orchestrator's `findings/` JSON store: the review agents also file each finding as a human-facing markdown file under `docs/findings/` with strict frontmatter (the toolset's local-first convention). This raises the option of reading those files rather than the reviewer's output.

### Alternatives (Pugh Matrix)

**A**: the reviewer ends its output with a fenced `json` findings block; the orchestrator parses it from stdout. **B**: the orchestrator parses the human markdown table in the report. **C**: the orchestrator reads the `docs/findings/*.md` files the agent wrote.

| Criterion                                                                        | Weight | A: JSON block | B: parse the table | C: read finding files |
| -------------------------------------------------------------------------------- | ------ | ------------- | ------------------ | --------------------- |
| Determinism — parseable without heuristics (Q1)                                  | 3      | +1            | -1                 | +1                    |
| Minimal risk — no change to the store model or loop semantics (Q1, Q3)           | 3      | +1            | 0                  | -1                    |
| Per-pass scoping — output is naturally one review pass, no cross-pass dedup (Q3) | 2      | +1            | +1                 | -1                    |
| Human legibility of the review output (Q4)                                       | 2      | 0             | +1                 | +1                    |
| Single source of truth with `docs/findings/` (Q5)                                | 2      | -1            | 0                  | +1                    |
| No new or brittle parser (Q7)                                                    | 1      | +1            | -1                 | 0                     |
| **Weighted total**                                                               |        | **+7**        | **0**              | **+2**                |

A wins. Parsing the human table (B) couples the ingest layer to a presentation format and is brittle — wrapped cells, column drift, multi-line messages. Reading the finding files (C) is the most coherent with the local-first convention and scores well on steady-state merits, but its realization requires resolving the relationship between the two finding stores (the orchestrator's `findings/` JSON store versus `docs/findings/`) and reworking per-pass scoping so the same file is not re-ingested each iteration — a store-model change out of scope here. A reuses the existing JSON parser, keeps the loop semantics untouched, and the reviewer's stdout is naturally scoped to a single pass.

## Decision

The semantic reviewer **ends its output with a fenced `json` block** listing exactly the findings it filed; the orchestrator ingests that block from the invocation's stdout.

- The block is `{"findings": [ { "code", "severity", "artifact", "message" }, … ]}`; a clean review emits `{"findings": []}`. Contract in [FINDING-FILING.md](../../../skills/_shared/FINDING-FILING.md#machine-readable-output).
- A `FindingIngestor` port maps the reviewer's output to findings and writes them to the store, which stamps the id, phase, and iteration (BR-019). The core depends on the port, never on the concrete mapper (ADR-0001).
- The reviewer reports on its own severity scale (`critical | major | minor`, or `high | medium | low` for the security and ATAM reviews); the ingestor maps that scale onto the store taxonomy (`error | warning | info`) so no finding is dropped.
- The reviewer emits only the findings it filed — Defects and blocking-severity findings — so the loop counts the same set that the human is asked to address; non-blocking notes stay in the report and never enter the loop.

## Consequences

**Positive**

- Deterministic ingestion with no bespoke parser: the block is machine-authored JSON, validated on the way into the store (VR-006).
- The human report is unaffected; the block is an addition, not a replacement.
- The loop-exit count reflects exactly the reviewer's filed findings, keeping SF-04 honest.

**Negative / risks**

- The findings are represented twice per review — once as the `docs/findings/*.md` artifacts and once in the stdout block. The two can drift if the reviewer is careless; the contract states they must mirror each other.
- A reviewer that omits the block reports zero findings and the phase auto-approves. This is the same failure mode as any missing gate output and is mitigated only by the agent instruction; a stricter check is deferred.

## Future

Option **C** remains the intended evolution: once the relationship between the `findings/` JSON store and `docs/findings/` is decided — whether the markdown files become the single source of truth and the JSON store a projection — ingestion should read the files directly and this block can be retired. This ADR is the interim contract, not the end state.

**Resolved by [ADR-0012](0012-ingest-findings-from-filed-markdown.md)** (ingestion source moved to the filed markdown) **and [ADR-0019](0019-findings-store-remains-the-loop-source-of-truth.md)** (the JSON store keeps the loop-state role; the filed markdown remains the ingestion input, not a second store). The stdout block this ADR chose is retired; the option A/B/C analysis above remains the historical record of that choice.
