[back to index](README.md)

# 9. Architecture Decisions

All architecture decisions are documented as ADRs (Architecture Decision Records) following the Nygard format. Each ADR includes frontmatter declaring whether alternatives were formally evaluated via Pugh Matrix (`evaluation: pugh-matrix`) or whether the decision was the direct application of an existing principle (`evaluation: none`).

## Decision Index

| ID   | Title                                                                                                                                                      | Status                 | Evaluation  |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ----------- |
| 0001 | [Pre-commit monorepo scoping](adr/0001-precommit-monorepo-scoping.md)                                                                                      | accepted               | none        |
| 0002 | [Factory owns flow control; orchestrator is a trigger](adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md)                                    | accepted               | pugh-matrix |
| 0003 | [Test execution via unavoidable hooks only](adr/0003-test-execution-via-hooks.md)                                                                          | accepted               | none        |
| 0004 | [Pi runs a factory agent by spawning a separate `pi` subprocess](adr/0004-pi-subagent-invocation-via-subprocess-spawn.md)                                  | accepted               | pugh-matrix |
| 0005 | [OpenRouter tiers curated into `model.conf`; discovery is a separate offline aid](adr/0005-openrouter-model-discovery-for-model-conf.md)                   | accepted               | none        |
| 0006 | [Research: flat prefixed rulebook storage and a schema → policy → semantic validation pipeline](adr/0006-research-flat-storage-and-validation-pipeline.md) | accepted               | none        |
| 0007 | [Normalize runtime usage through CLI adapters into local append-only records](adr/0007-normalize-runtime-usage-through-cli-adapters.md)                    | superseded by ADR-0009 | none        |
| 0008 | [Separate proposal impact, governance, estimates, and actuals](adr/0008-separate-proposal-impact-governance-estimates-and-actuals.md)                      | accepted               | none        |
| 0009 | [Verbatim session id as the usage-record filename when filesystem-safe](adr/0009-verbatim-usage-record-filenames-when-filesystem-safe.md)                  | accepted               | none        |

## Key Decisions

### Ownership and Control

**ADR-0002** establishes that `factory/scripts/{transition-lint,phase,trigger}` and the `run-step` skill own flow control state (the marker, FSM, gates). `orchestrator/` is one possible trigger among peers (human operator, orchestrator CLI). This inversion makes playbook runs CLI-agnostic and resume-from-observable-state by design.

### Validation Strategy

**ADR-0001** and **ADR-0003** establish the hook-triggered validation pattern:

- **Pre-commit hooks** gate which files may be staged (`transition-lint`) and whether tests pass (`run-tests --changed-only`).
- **Pre-push hooks** enforce full test suite passage (`run-tests --full`) before work leaves local machine.
- **PreToolUse hooks** block destructive git commands and test commands before they execute (`block-dangerous-git.sh`).
- **FSM gates** (`script_exit_zero`) integrate test execution into phase advance entry conditions.

All follow the "Agentic Creation, Deterministic Validation" principle: agents create, hooks validate, no self-validation.

### Monorepo Scoping

**ADR-0001** declares one root `.pre-commit-config.yaml` for the monorepo, with each subproject's hooks namespaced (e.g., `-orchestrator` suffix) and path-scoped (`files: ^orchestrator/`). `factory/scripts/merge-precommit-config` splices subproject hook blocks into the root file.

### Pi Invocation Layer

**ADR-0004** establishes that Pi, which has no native subagent concept, runs a factory agent by spawning a separate `pi` subprocess through the model-callable `run_agent` tool (a project-local extension). This restores author/reviewer independence and parallel dispatch under Pi over the exact mechanism Pi's own documentation sanctions, rejecting in-context role-play (fails independence) and a custom agent hierarchy (fights Pi's design, YAGNI). **ADR-0005** keeps Pi tier→model resolution static and offline in `model.conf`, adding `openrouter-discover` as a separate operator aid for curating and validating `pi.*` OpenRouter rows — never a network call on the runtime path.

### Research Feature Structure and Validation

**ADR-0006** records three structural decisions behind the falsification-driven research feature. Research rulebook files use flat, by-kind storage with a `research-` filename prefix rather than a per-feature subtree, keeping `index-lint`'s directory-derived category intact. A new `rulebooks/schemas/` category holds JSON-Schema data contracts, deliberately outside `INDEX.yaml` (which scans Markdown only). Research artifacts pass a fixed three-stage pipeline — schema (`schema-validate`), then policy (`policy-validate`), then semantic review — that splits validation by whether a machine can decide it, applying the "Agentic Creation, Deterministic Validation" principle. Research agents group under phase 6, a self-contained workflow driven by the `research-topic` playbook, not a sixth step in the linear production chain.

### Runtime Usage Observability

**ADR-0007** (superseded by **ADR-0009** for the identifier-to-path rule)
establishes one CLI-agnostic runtime usage pipeline with per-CLI transcript
normalizers and native lifecycle adapters. Fixed `cl100k_base` counts
provide the cross-CLI comparison metric, while nullable provider counts
support cost reconciliation. Append-only local JSONL and linked transcript
copies are the MVP backend; the orchestrator does not duplicate CLI-owned
capture. Root and child records follow each platform's conservation
semantics so attribution is not added twice to an inclusive root. **ADR-0009**
revises the storage-naming decision: a verbatim session id is the filename
when it is a single filesystem-safe component (mixed case allowed, so Pi root
ids stay readable), and the `opaque-<sha256>` digest is reserved for
identifiers that are genuinely unsafe as a filename — the SEC-0001
containment property is unchanged. The rest of ADR-0007's pipeline design
remains in force.

### Proposal Effort Forecasting and Calibration

**ADR-0008** separates proposal impact, governance, and dated forecasts from
append-only actual accounting. Human-review hours represent active human
attention rather than elapsed time; normalized tokens remain ADR-0007's
cross-CLI comparison metric rather than a provider-cost estimate. Future
actuals reference the proposal path and accepted full Git SHA outside the
proposal, preserving the original forecast for calibration.

## Superseded Decisions

None yet.

## Referenced from

- [04_solution_strategy.md](04_solution_strategy.md) — solution strategy derives from these decisions
- [05_building_block_view.md](05_building_block_view.md) — building blocks implement these decisions
- [08_crosscutting_concepts.md](08_crosscutting_concepts.md) — principles codified here
