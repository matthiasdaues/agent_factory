---
schema_version: 2
title: Data-Model DSL Technical Proof-of-Concept
status: open
owner: Matthias Daues
created: 2026-08-14
updated: 2026-08-14
supersedes:

impact:
  scope: cross_project
  architecture_change: false
  external_contract_change: false
  boundaries:
    - docs/spec/supplementary_specs/entity-model.md
    - factory/scripts/structurizr

governance:
  assurance: elevated
  risk_domains:
    - data_integrity
    - compatibility

estimate:
  as_of: 2026-08-14
  basis: analogous_change
  confidence: medium
  human_review_hours:
    min: 3.0
    max: 6.0
  normalized_tokens:
    min: 300000
    max: 700000
---

# Feature Request: Data-Model DSL Technical Proof-of-Concept

## Summary

Settle by observation which text-based data-modeling meta-language can hold the Gigacron entity model as a validatable documentation-as-code artifact. The completed survey answered what the candidates' documentation claims; it could not answer what their tools actually do, because no candidate was installed or executed. This proposal opens a bake-off under [technical-poc.md](../../factory/playbooks/technical-poc.md) that ports one fixed slice of the real entity model to four candidates and runs each one. The first release ends at four comparison notes and a Pugh Matrix; it does not adopt a language.

## Motivation

The persisted model lives today as a Mermaid `erDiagram` embedded in `docs/spec/supplementary_specs/entity-model.md`: 25 entities, roughly 30 relationships, and 21 prose constraints cross-linked to use cases and validation rules. Nothing validates it. Nothing connects it to the code that will implement it. It drifts silently, and the drift is discovered only by a human reading the diagram against the schema.

The survey recorded in [survey-report.md](survey-report.md) established the field on documentary evidence, and its headline is that **no candidate satisfies all three MUSTs**: a plain-text product-neutral source of truth, a validator that exits non-zero, and SVG plus PNG rendering from an ephemeral Docker container. It also established that expressiveness and toolchain maturity are uncorrelated — the strongest languages have the weakest tooling and the reverse.

That result is exactly the point at which documentary research stops paying. The remaining questions are all of the form "what does the binary actually do", and the survey's own `candidates_for_deeper_falsification_study` section names them one by one, each with the command that would answer it. Several are load-bearing. Whether `dbml2sql` really returns zero on a broken model decides whether DBML can sit behind a gate at all. Whether LinkML's generators preserve a composite key and a CHECK constraint decides whether its generation story is real. Whether Atlas can validate an HCL file without a live database decides whether it can be used while ADR-0001 leaves the product unchosen.

Deciding without running them would mean adopting a source of truth for the whole persisted model on the strength of vendor documentation, and the survey already caught vendor documentation contradicting itself twice.

## Core Principles

- **One fixed slice, ported identically.** Every candidate models the same nine entities. A candidate does not get to choose the example that flatters it.
- **Observation outranks documentation.** Every claim in a comparison note comes from a command that was run and an output that was seen. Where the survey already recorded a documented claim, the note records whether observation confirmed or contradicted it.
- **Docker or it does not count.** Every candidate is exercised only through `docker run --rm`, mirroring [structurizr](../../factory/scripts/structurizr). A capability reachable only after a local install fails the MUST it claims to satisfy.
- **A ruled-out candidate is a result.** A candidate that cannot meet its Definition of Done is recorded as answered, not as failed, and does not get more time than the others got.
- **The PoC decides nothing by itself.** It produces comparison notes. The Pugh Matrix and the ADR are separate, later, and human-approved.

## Design

### The acid slice

Nine entities drawn unchanged from `entity-model.md`, chosen because between them they carry all ten advanced constructs the brief named. This is the fixed input to every candidate story.

| Entity                | Constructs it contributes                                                                                                                                                                                       |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DOMAIN`              | root of the `domain_id` cross-cutting convention                                                                                                                                                                |
| `TASK_VERSION`        | JSON payload columns (`schedule_spec`, `retry_spec`, `cyclic_spec`)                                                                                                                                             |
| `OUTCOME_RULE`        | composite primary key (`task_version_id`, `sequence_no`)                                                                                                                                                        |
| `NAMED_RESOURCE`      | multi-column UNIQUE (`domain_id`, `name`) not tied to the primary key                                                                                                                                           |
| `NAMED_RESOURCE_LINK` | composite primary key; enumerated domain (`link_kind`); value constraint beyond type (`resource_task_weight` is a positive integer **or** the literal `ALL`)                                                    |
| `PLAN`                | second multi-column UNIQUE (`domain_id`, `odate`)                                                                                                                                                               |
| `TASK_INSTANCE`       | three simultaneous self-referencing foreign keys (`origin_instance_id`, `cyclic_root_instance_id`, `previous_iteration_id`); nullable foreign keys (`folder_run_id`, `plan_id`); enumerated `execution_context` |
| `ATTEMPT`             | the owning side of a one-to-zero-or-one relationship                                                                                                                                                            |
| `ATTEMPT_RESULT`      | the zero-or-one side                                                                                                                                                                                            |

The four logical schemas from ADR-0001 in the Gigacron repository, `docs/adr/0001-single-database-domain-scoping.md`, are preserved in the slice: `DOMAIN`, `TASK_VERSION`, `NAMED_RESOURCE`, and `NAMED_RESOURCE_LINK` sit in configuration and resources; `PLAN`, `TASK_INSTANCE`, `ATTEMPT`, and `ATTEMPT_RESULT` sit in runtime.

Two artifacts are authored once and reused by every story: `acid-slice.md`, the human-readable specification of the nine entities and their constraints, and `acid-slice-broken.<ext>`, a deliberately malformed model per candidate carrying one syntax error and one semantic error — a relationship to an undeclared entity — used to observe validator behaviour.

### One story per candidate

Each story is a plain markdown file under `poc/data_model_from_dsl/stories/`, per [technical-poc.md § Step 1](../../factory/playbooks/technical-poc.md). Each states its goal, the risk it tests, what to build, a mechanical Definition of Done, and the instruction to write a comparison note.

The four candidate stories and the specific question each exists to settle:

- **DBML** — does `dbml2sql` exit non-zero on a broken model? The survey read the CLI source and found no `process.exit(1)`. This is the single finding that decides whether the survey's most expressive language can sit behind a gate. Also: does any renderer honour `DiagramView`, the only genuinely model-aware named-view construct found in the whole field?
- **LinkML** — do the first-party Pydantic, SQLAlchemy, and SQL DDL generators preserve the composite key, the JSON column, the enumerated domain, and the `resource_task_weight` constraint? LinkML is the only candidate with first-party application-type generation, and the survey could not confirm generation fidelity for any of it.
- **Atlas HCL** — can the four-schema split be validated from the HCL file alone, or does `--dev-url` force a live database and therefore a dialect choice? Separately, confirm which Docker tag family carries which licence, which the survey left unresolved.
- **Mermaid erDiagram (incumbent baseline)** — does `mmdc` render a diagram whose relationship references an undeclared entity, silently and successfully? The baseline must be measured on the same slice as the challengers, or "better than what we have" is an assertion rather than a finding.

### Per-story Definition of Done

Mechanical, identical in shape across candidates:

1. The acid slice is expressed in the candidate's language, or the story records precisely which of the ten constructs could not be expressed and what was substituted.
2. `docker run --rm <image> <validate-command>` is run against the valid slice and exits 0.
3. The same command is run against `acid-slice-broken` and its **exact numeric exit code** is recorded, together with whether the semantic error was detected at all.
4. SVG is produced into `poc/data_model_from_dsl/out/<candidate>/`, from a container, with no local install.
5. PNG is produced the same way, or the story records the exact reason it cannot be.
6. Where the candidate claims application-type or DDL generation, it is run, and each of the ten constructs is marked survived or lost in the output.
7. Where the candidate claims named views, a view over a subset of the nine entities is produced and the rendered result is inspected.
8. Every command is captured verbatim in the comparison note, so a reader can re-run it.

## Scope

**In the first release:**

- The `acid-slice.md` specification and one broken-model variant per candidate.
- Four candidate stories: DBML, LinkML, Atlas HCL, Mermaid erDiagram.
- Four comparison notes, each answering the eight Definition-of-Done items.
- A Pugh Matrix over the four, scored from the comparison notes, via [pugh-matrix](../../factory/skills/pugh-matrix/SKILL.md).
- A written recommendation, or an explicit deferral with a stated reason.
- All prototype material confined to `poc/data_model_from_dsl/`.

**Explicitly deferred (do NOT plan stories for these):**

- **Prisma, PlantUML IE, and D2.** Each is excluded on recorded survey evidence, not on preference. Prisma has no official Docker image, cannot express CHECK constraints, mandates a single provider from a closed enum against ADR-0001's open product choice, and its only Python generator is archived. PlantUML degrades composite keys, multi-column UNIQUE, and value constraints to free-text notes, which makes the model unvalidatable in exactly the places that matter. D2 cannot express six of the ten constructs, and its maintainers state it cannot represent multi-column foreign keys at all. Any of the three may be revived if a story turns up evidence that overturns its exclusion.
- Porting the full 25-entity model. The slice is the experiment; the full port belongs to adoption.
- Writing the ADR, or amending `entity-model.md`.
- Building the `factory/scripts/<candidate>` Docker wrapper as shipped tooling. Throwaway container invocations only.
- Choosing the relational database product. ADR-0001 leaves it open and this PoC does not close it.
- Migration tooling, CI integration, and pre-commit gating.

## Design Details

Prototype material lives under `poc/data_model_from_dsl/` and stays marked as spike code, per [technical-poc.md § DONE](../../factory/playbooks/technical-poc.md). Nothing is promoted into the specification or the Factory scripts by this proposal.

Candidates are independent, so their stories may run in parallel, one worktree per candidate, per [branching-policy.md § Every Branch Has A Worktree](../../factory/rulebooks/conventions/branching-policy.md#every-branch-has-a-worktree). Note that the Factory install is gitignored, so a freshly created worktree contains no `factory/` and no CLI agent directory. Symlink both from the primary checkout before dispatching anything into such a worktree, and leave `.agent-factory/` per-worktree so the gate markers do not collide.

No agent builds the candidates. The builds are done directly, per [technical-poc.md § Step 2](../../factory/playbooks/technical-poc.md).

Comparison notes cite the survey's source records by filename wherever they confirm or contradict a documented claim, so the PoC's evidence chain joins the survey's rather than starting over.

Where a candidate needs a live database — Atlas is the known case — the container is ephemeral and disposable, and the note records that the dependency exists, because needing a database engine to validate a specification artifact is itself a finding.

## Open Questions

- Does a candidate that fails a MUST but wins decisively on expressiveness stay in the Pugh Matrix, or is a failed MUST eliminating? The survey establishes no candidate passes all three, so a strict reading eliminates the entire field and the PoC has nothing to score. Proposed resolution: MUST failures are scored as severe weighted penalties rather than as elimination, and the matrix records which MUSTs each candidate fails. This needs stakeholder agreement before scoring, not after.
- Is a two-language split acceptable — one language as the specification source of truth, a second generating code and DDL from it? The survey's uncorrelated-maturity finding makes this the obvious escape from a field where nothing passes everything. It doubles the toolchain, so it should be decided deliberately rather than backed into.
- Should the PNG requirement stand? Only PlantUML and Mermaid clearly satisfy it, D2 needs headless Chromium, and it is not obviously load-bearing if SVG renders everywhere. If PNG is a convenience rather than a requirement, saying so now widens the viable field.

## Completion Criteria

- `acid-slice.md` exists and demonstrably contains all ten constructs.
- Each of the four candidates has a comparison note answering all eight Definition-of-Done items, or recording precisely why an item could not be answered.
- Every exit code in every note was observed from a command that was run, never inferred from documentation.
- Every rendering claim is backed by a file in `out/<candidate>/` produced from a container with no local install.
- A Pugh Matrix scores the four against weighted criteria drawn from the comparison notes, and the weights were confirmed with the stakeholder before scoring.
- A recommendation is recorded, or the decision is explicitly deferred with a stated reason — not left implicit.
- Nothing under `poc/` has been promoted into the specification, the architecture, or the Factory scripts.

## Guiding Rule

Every claim in this PoC's output must name a command that was run and an output that was seen; where it cannot, it must say so plainly.
