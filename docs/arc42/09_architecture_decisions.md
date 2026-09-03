[back to index](../README.md)

# 9. Architecture Decisions

All architecture decisions are documented as ADRs (Architecture Decision Records) following the Nygard format. Each ADR includes frontmatter declaring whether alternatives were formally evaluated via Pugh Matrix (`evaluation: pugh-matrix`) or whether the decision was the direct application of an existing principle (`evaluation: none`).

## Decision Index

| ID   | Title                                                                                                                                                         | Status                 | Evaluation  |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ----------- |
| 0001 | [Pre-commit monorepo scoping](../adr/0001-precommit-monorepo-scoping.md)                                                                                      | accepted               | none        |
| 0002 | [Factory owns flow control; orchestrator is a trigger](../adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md)                                    | accepted               | pugh-matrix |
| 0003 | [Test execution via mechanically triggered gates](../adr/0003-test-execution-via-hooks.md)                                                                    | accepted               | none        |
| 0004 | [Pi runs a factory agent by spawning a separate `pi` subprocess](../adr/0004-pi-subagent-invocation-via-subprocess-spawn.md)                                  | accepted               | pugh-matrix |
| 0005 | [OpenRouter tiers curated into `model.conf`; discovery is a separate offline aid](../adr/0005-openrouter-model-discovery-for-model-conf.md)                   | accepted               | none        |
| 0006 | [Research: flat prefixed rulebook storage and a schema → policy → semantic validation pipeline](../adr/0006-research-flat-storage-and-validation-pipeline.md) | accepted               | none        |
| 0007 | [Normalize runtime usage through CLI adapters into local append-only records](../adr/0007-normalize-runtime-usage-through-cli-adapters.md)                    | superseded by ADR-0009 | none        |
| 0008 | [Separate proposal impact, governance, estimates, and actuals](../adr/0008-separate-proposal-impact-governance-estimates-and-actuals.md)                      | accepted               | none        |
| 0009 | [CLI-prefixed usage record filenames when filesystem-safe](../adr/0009-cli-prefixed-usage-record-filenames-when-filesystem-safe.md)                           | accepted               | none        |
| 0010 | [Refresh an installed factory/ by remove-and-reinstall](../adr/0010-refresh-installed-factory-by-remove-and-reinstall.md)                                     | accepted               | none        |
| 0011 | [Gherkin .feature as consolidated specification format](../adr/0011-gherkin-feature-as-consolidated-specification-format.md)                                  | proposed               | pugh-matrix |
| 0012 | [Dispatcher-owned semantic gate loop](../adr/0012-dispatcher-owned-semantic-gate-loop.md)                                                                     | proposed               | pugh-matrix |
| 0013 | [YAML agent context replaces markdown charter](../adr/0013-yaml-agent-context-replaces-markdown-charter.md)                                                   | proposed               | pugh-matrix |
| 0014 | [Two-layer routing with two-mode lifecycle](../adr/0014-two-layer-routing-with-two-mode-lifecycle.md)                                                         | proposed               | none        |

## Key Decisions

### Ownership and Control

**ADR-0002** establishes that `factory/scripts/{transition-lint,phase,trigger}` and the `run-step` skill own flow control state (the marker, FSM, gates). `orchestrator/` is one possible trigger among peers (human operator, orchestrator CLI). This inversion makes playbook runs CLI-agnostic and resume-from-observable-state by design.

### Validation Strategy

**ADR-0001** and **ADR-0003** establish the hook-triggered validation pattern:

- **Pre-commit hooks** gate which files may be staged (`transition-lint`).
- **PreToolUse hooks** block destructive git commands and bare test commands before they execute (`block-dangerous-git.sh`); charter-declared test commands are allowlisted with exact-string matching.
- **FSM gates** (`script_exit_zero`) resolve `charter:test_command` from `docs/charter/testing.yaml` and integrate test execution into phase advance entry conditions.

All follow the "Agentic Creation, Deterministic Validation" principle: agents create, hooks validate, no self-validation. Testing is project-owned infrastructure declared in the charter; Factory ensures test gates exist but does not own test execution or framework detection.

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
revises the storage-naming decision: the session-level key is
`<cli>_<session_id>` (record file and transcript directory), so a directory
listing identifies which CLI produced a run; the CLI token is itself passed
through `filesystem_key`, and the `opaque-<sha256>` digest is reserved for
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

## Factory Install, Update, and Removal

**ADR-0010** gives the one-time install a forward path: `update-factory`
refreshes an installed `factory/` to the current checkout by remove-and-
reinstall — a byte-exact replacement followed by a re-run of the sourced
`init-factory` — rather than a recency-based diff-and-merge, which is
nondeterministic and rests on unreliable file mtimes. `init-factory` records
the checkout it copied from (`factory_source`) in the install manifest so
`update-factory` knows which repo to pull from by default, `--source`
overriding. `update-factory` replaces only `factory/`; `.agent-factory/` usage
transcripts and lifecycle state survive an update.

### Consolidated Specification Format

**ADR-0011** selects Gherkin `.feature` files with a Rule-per-actor-goal
structure as the consolidated specification format, superseding the
`derive-spec` chain of intermediate Cockburn documents. Three alternatives
were evaluated via Pugh Matrix: keeping the Cockburn UC chain (baseline),
consolidated Gherkin, and structured YAML. Gherkin dominates on executability
(test frameworks consume `.feature` files directly), tool ecosystem breadth,
and single-pass readability (one file instead of N `UC-XX` documents). The
`derive-feature` skill retains Cockburn's actor-goal reasoning as an internal
discipline without committing intermediate artifacts. Supplementary specs
(`entity-model.md`, `interface-contracts.md`, `state-machines.md`,
`validation-rules.md`) continue as separate outputs for structural facts the
`.feature` file does not encode.

### Semantic Gate Execution Model

**ADR-0012** places the semantic quality gates under the implementation-agent
dispatcher, not the developer agent or a CI pipeline. Three alternatives were
evaluated via Pugh Matrix: developer-owned (baseline, self-validation),
dispatcher-owned, and CI-owned. The dispatcher model wins on the foundational
"Agentic Creation, Deterministic Validation" principle (the developer agent
never validates its own work), context contamination prevention (fresh
developer per fix iteration), and infrastructure fit (the dispatcher already
owns wave scheduling and merge ordering). CI-owned gates satisfy the
no-self-validation requirement but add network latency and require
infrastructure the Factory does not currently have. The gate loop fires after
each developer commit: CRAP scoring, dependency checking, then proceed-or-fix.
Maximum three fix iterations per tier before the story escalates or is marked
blocked. Mutation testing is project-owned infrastructure that Factory encourages
via the `mutation-analysis` skill (see [ADR-0012 § Amended](../adr/0012-dispatcher-owned-semantic-gate-loop.md#amended)).

### Agent Context Format and Structure

**ADR-0013** replaces the markdown charter (`docs/charter/`) with a YAML-based
agent context (`docs/agent-context/`). Three format alternatives were evaluated
via Pugh Matrix: markdown (baseline), YAML, and JSON. YAML dominates on machine
parseability, staleness resistance, and per-field source pointers while
maintaining human readability parity with markdown. Format detection provides
backward compatibility: factory consumers walk a three-step chain and select the
appropriate validation mode. A new `context-lint` script (replacing
`charter-lint`) validates the YAML structure with `CX-*` finding codes.

**ADR-0014** records the two structural mechanisms that sit on top of the format
decision. Two-layer routing separates concern-based access (Layer 1:
`reading-guides.yaml`) from decision-domain indexing (Layer 2: `stack.yaml`,
`workflow.yaml`, `governance.yaml`), keeping source pointers in exactly one
place. A two-mode lifecycle lets greenfield projects write values directly
(`mode: primary`) and mature projects maintain a pure link index
(`mode: index`); the transition is one-directional and atomic. Neither mechanism
has genuine alternatives: two layers resolve a concrete drift failure from the
single-layer predecessor, and two modes follow from the greenfield-to-mature
constraint.

## Superseded Decisions

None yet.

## Referenced from

- [05_building_block_view.md](05_building_block_view.md) — building blocks implement these decisions
- [08_crosscutting_concepts.md](08_crosscutting_concepts.md) — principles codified here
