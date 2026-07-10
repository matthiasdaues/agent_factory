# 0008. Backlog as markdown with strict frontmatter

**Status**: Accepted

## Context

The planning phase must emit a backlog to the local filesystem, because external trackers are out of scope (NG3). This resolves the open question T-10, which had left the planning phase without a staging path (BR-016) or completion check (FR-H1). The backlog serves two readers: the **operator**, who reads and grooms stories, and the **implementation agent**, which builds them. The orchestrator, in turn, needs a small set of machine fields per story — id, dependencies, status, classification, declared outputs — to route work, select a model (FR-K), and detect completion.

The existing findings store (ADR-0004) is one JSON file per finding. The tempting move is to mirror it: one JSON file per story. But findings are machine-produced and machine-read; a story is human-authored and human-read. The question is which format serves a human-facing artifact that must also be machine-strict.

### Alternatives (Pugh Matrix)

Baseline **A**: one JSON file per story (mirrors the findings store). **B**: one markdown file per story with strict YAML frontmatter (machine fields) plus a prose body. **C**: plain markdown, no schema.

| Criterion                                    | Weight | A: JSON | B: markdown + frontmatter | C: plain markdown |
| -------------------------------------------- | ------ | ------- | ------------------------- | ----------------- |
| Machine strictness / determinism (Q1)        | 3      | 0       | 0                         | -1                |
| Human readability (Q4)                       | 2      | 0       | +1                        | +1                |
| Consistency with the findings store (Q4)     | 2      | 0       | -1                        | -1                |
| Token efficiency of the machine path (NFR-6) | 2      | 0       | 0                         | -1                |
| Maps to a future ticket adapter (Q5)         | 2      | 0       | 0                         | 0                 |
| **Weighted total**                           |        | **0**   | **0**                     | **-6**            |

A and B tie at zero. The matrix informs; it does not decide. The tie-breaker is the artifact's primary reader: a story exists to be read and groomed by a human, so **human readability is the deciding value** — exactly the criterion on which B beats A. C is eliminated: without a schema it cannot give the orchestrator a strict, deterministic field to read.

The token concern that a JSON advocate would raise — that frontmatter duplicates the body — does not hold. The frontmatter fields are disjoint from the prose (metadata, not narrative), the orchestrator reads only the frontmatter (it stops at the closing `---`), and the implementation agent reads only the body. Nothing is read twice.

## Decision

A story is **one markdown file** per unit of work, `backlog/ST-NNNN.md`:

- **Strict YAML frontmatter** holds the machine fields (`id`, `epic`, `title`, `classification`, `status`, `deps`, `traces`, `outputs`), validated against the StoryFrontmatter schema ([interface-contracts](../spec/supplementary_specs/interface-contracts.md)) — as strict as JSON.
- **A prose body** holds the human story: narrative, INVEST framing, acceptance criteria. No machine field is restated in the body.
- **`backlog-lint`** validates both — frontmatter schema and body traceability — and is the planning phase's gate hook (VR-022), giving the phase its BR-016 staging and FR-H1 completion. This resolves T-10.

The divergence from the findings store's JSON is deliberate and follows from the readers: findings are never a primary human artifact; stories always are.

## Consequences

**Positive**

- The backlog is legible and groomable by the operator, yet the orchestrator reads a strict, schema-validated header (Q1, Q4).
- The orchestrator loads only frontmatter for routing; the body cost falls only on the agent that must read it anyway (NFR-6).
- Each story is one file — diffable, atomic to write, and mapping cleanly onto a future ticket (Q5).

**Negative / risks**

- Two artifact formats now exist in the project — JSON findings and markdown stories. The split is justified by the different readers, but it is a real inconsistency a newcomer must be told about (documented here and in [chapter 11](../11_risks_and_technical_debt.md)).
- Markdown prose cannot be type-schematized; `backlog-lint` enforces required sections and the "no machine field in prose" rule, but body quality still rests partly on the author.
