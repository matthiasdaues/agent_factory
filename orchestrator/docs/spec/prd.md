# PRD — Agent Session Orchestrator

**Status**: Draft
**Date**: 2026-07-05
**Domain**: Tooling for the Agent HQ semantic-anchor-driven development workflow
**Addendum**: [prd-tui-addendum.md](prd-tui-addendum.md) — TUI menu mode (FR-P through FR-V)

> **Scope note (amended 2026-07-12, PhaseRunner collapse):** the orchestrator no longer drives agent execution. `PhaseRunner`, the author↔reviewer loop, model resolution, prompt composition, findings ingestion, and the `run-step`/`run-phase`/`resume` commands moved to `factory/` — see the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`. Requirements below that describe this execution surface are marked `_(Superseded — moved to factory.)_` and kept for traceability and history; the orchestrator no longer implements them. Requirements for `status`, `approve`, `reject`, `abort`, `release`, `init`, the TUI, and configuration remain accurate and unmarked.

______________________________________________________________________

## 1. Problem Statement

The Agent HQ workflow is an eight-agent chain (requirements → spec-review → architecture → architecture-review → planning → implementation → reconciliation → qa) with deliberate author/reviewer loops and human approval points. Today it is driven entirely by hand: the operator edits the CLI instruction file to swap the active agent, starts a fresh session for each step to preserve context isolation, and copy-pastes handoff prompts between sessions. Correctness depends on the operator remembering to run gates, honour the separate-session rule, and loop until each review is clean.

This is slow, error-prone, and does not scale past a few steps. We want a thin orchestration layer that runs the chain — a single step or the whole sequence — with the deterministic quality gates enforced automatically and human judgement reserved for the decisions that genuinely need it.

## 2. Goals and Non-Goals

### Goals

- **G1** — _(Superseded — moved to factory.)_ A Python CLI that can run any single agent step, a whole phase (author ↔ reviewer loop), or the full chain.
- **G2** — _(Superseded — moved to factory.)_ Preserve session isolation: every agent runs in a fresh CLI subprocess with no shared context, so a reviewer never sees the author's reasoning.
- **G3** — Enforce **deterministic gates** between steps via `pre-commit` as the gate bus — the orchestrator commits each step's artifacts and the hooks (starting with `spec-lint`) block progress on failure.
- **G4** — Maintain a **local, validatable issue store** (file-per-finding JSON) as the source of truth for review findings and loop state. The orchestrator still reads this store (`status > findings`); populating it is now factory's job.
- **G5** — _(Superseded — moved to factory.)_ Run **autonomously within a phase**, pausing only at phase gates for human sign-off on the semantic artifacts.
- **G6** — _(Superseded — moved to factory.)_ Be **CLI-agnostic** behind an adapter contract, with **GitHub Copilot CLI** as the first concrete adapter.
- **G7** — _(Superseded — moved to factory.)_ Fail safe: loop-back is capped; on exhaustion the orchestrator halts and summons the human rather than churning.

### Non-Goals

- **NG1** — Not a re-implementation of agent or skill logic; the orchestrator *drives* the existing agents and skills, it does not embed their behaviour.
- **NG2** — Not a general-purpose CI system; `pre-commit` and the CLIs do the work, the orchestrator sequences them.
- **NG3** — No integration with GitHub Issues, Jira, or other external ticket tools in this version (deferred — see [T-04](todos.md)).
- **NG4** — No graphical UI; a terminal CLI with an interactive **text** menu only.
- **NG5** — The MVP does not attempt the full eight-agent chain — see MVP scope below.
- **NG6** — _(Deferred scope)_ No single-command automated full-chain run (`run-all`) and no unattended execution (a Scheduler running the chain headlessly with `--yes`) in this version. Every run is human-attended; the Operator drives the phases one at a time (UC-03). Automated and unattended chain execution return when the orchestrator gains a **messaging channel or Web-UI** for remote observation and approval ([T-36](todos.md)).

### MVP scope

The walking skeleton is the **requirements phase only** (author `requirements-agent`, reviewer `spec-review-agent`), driven through the **Copilot** adapter: run the author, commit the spec (pre-commit runs `spec-lint`), run the reviewer in a fresh session, write findings to the local store, loop back to the author if findings remain (capped), and persist `awaiting-approval` for human sign-off when clean. The other three phases (architecture, planning, implementation) are later generalizations of this proven pattern.

## 3. Target Users

- **Primary** — the workflow operator driving a project through the chain, who wants to launch a step or the whole sequence and step away, trusting the gates.
- **Secondary** — future practitioners adopting Agent HQ on other CLIs (Copilot, Claude, Gemini), who need the orchestration to be CLI-agnostic.

## 4. Functional Requirements

### FR-A — Execution surface

- **FR-A1** — _(Superseded — moved to factory.)_ `orchestrate run-step <agent>` runs a single agent once in a fresh session, verifies the working tree is clean after the agent exits (gate), and reports the result.
- **FR-A2** — _(Superseded — moved to factory.)_ `orchestrate run-phase <phase>` runs an author ↔ reviewer loop to completion (or cap). The Operator drives the chain by running `run-phase` for each phase in dependency order, approving each gate (UC-03).
- **FR-A4** — `orchestrate status` reports current phase, iteration, open findings, and last gate result.
- **FR-A5** — _(Superseded — moved to factory.)_ `orchestrate resume` continues an interrupted run from its last checkpoint.
- **FR-A6** — `orchestrate approve` records human sign-off at a paused phase gate.
- **FR-A7** — `orchestrate release` recovers a halted run by restoring the phase to its pre-halt sub-state (authoring, gating, or reviewing) and resetting the iteration count, so the operator can continue via the factory scripts without aborting.
- **FR-A8** — `orchestrate abort` releases a stale run lock, archives or deletes run state, and lets the operator start fresh.

### FR-B — Session isolation

_(Superseded — moved to factory. Fresh-subprocess invocation and prompt composition no longer live in the orchestrator.)_

- **FR-B1** — Each agent invocation is a fresh subprocess of the target CLI with no inherited conversation context.
- **FR-B2** — The orchestrator composes the agent prompt from the agent definition file plus project/root context, an `InvocationContext` (phase, role, iteration), and a call-to-action section that orients the agent to its specific workstep. The call-to-action varies by role and iteration (five templates: author-first, author-loopback, reviewer-first, reviewer-loopback, standalone).

### FR-C — CLI adapter contract

_(Superseded — moved to factory. CLI invocation no longer lives in the orchestrator; the orchestrator's own `AdapterRegistry` — a separate, lighter concern — persists adapter names and model dictionaries for menu display only.)_

- **FR-C1** — A single adapter interface abstracts CLI invocation: given a composed prompt and a working directory, run the CLI non-interactively and return exit status plus captured output.
- **FR-C2** — **GitHub Copilot CLI** is the first concrete adapter and must run the MVP loop end-to-end.
- **FR-C3** — Claude and Gemini adapters conform to the same contract; their MVP implementation depth is an open item ([T-02](todos.md)).

### FR-D — Deterministic gates (agent commits as the gate)

- **FR-D1** — _(Superseded — moved to factory.)_ Every agent commits its own artifacts; `pre-commit` hooks fire on each commit inside the agent subprocess, serving as the quality gate.
- **FR-D2** — `spec-lint` runs as a `pre-commit` hook and blocks the commit on any ERROR-severity finding. Unaffected by the collapse — this is a repo-level hook, not orchestrator logic.
- **FR-D3** — After the agent exits, the orchestrator verifies the working tree is clean. A clean tree means all artifacts were committed and all hooks passed. A dirty tree is a gate failure. The orchestrator no longer performs this check per phase iteration (that loop moved to factory); it still performs it once, for the artifact-staleness re-gate at `approve` (VR-012, `ApprovalService.approve()`).
- **FR-D4** — _(Superseded — moved to factory.)_ Later phases register additional hooks (e.g. `ruff`, `pytest`) under the same mechanism with no orchestrator change.
- **FR-D5** — _(Superseded — moved to factory.)_ Exit code 0 with a dirty working tree is a **confabulation** — the agent claimed success but did not commit. This is a trust violation that halts the run for operator intervention.
- **FR-D6** — _(Superseded — moved to factory.)_ Non-zero exit with a dirty working tree is a normal failure. The orchestrator cleans the tree (preserving committed work) and loops via RetryOrHalt.

### FR-E — Local findings store

- **FR-E1** — Findings are stored **one JSON file per finding**, each with a unique ID, under a `findings/` directory. Still accurate — the orchestrator reads this store for `status > findings`.
- **FR-E2** — Each finding validates against a JSON Schema. Fields include `id`, `phase`, `iteration`, `source` (`spec-lint` | `semantic`), `code`, `severity`, `artifact`, `message`, `status` (`open` | `superseded` | `resolved`), `created_by`, `resolved_by`. IDs are assigned by a monotonic allocator (never by the sources). Still accurate.
- **FR-E3** — Deterministic findings (from `spec-lint --format json`) and semantic findings (from the review agent) both land in the same store in the same shape. Still accurate; ingestion is now factory's job.
- **FR-E4** — _(Superseded — moved to factory.)_ The review agents' former "file a GitHub issue" step is redirected to local storage: agents file findings as `docs/findings/<TAG>-NNNN.md` and emit a fenced `json` findings block that the orchestrator ingests into this store (all review agents; [T-03](todos.md), [ADR-0011](../adr/0011-reviewer-findings-ingest-contract.md)).

### FR-F — Loop control

_(Superseded — moved to factory. Iteration caps and loop-exit evaluation no longer live in the orchestrator.)_

- **FR-F1** — A phase is *not done* while any latest-iteration finding has `status: open` or its gate fails; each authoring iteration supersedes the prior iteration's open findings so the loop can terminate.
- **FR-F2** — On open findings or a failed gate, the orchestrator re-runs the authoring agent with the findings/gate output as extra instruction.
- **FR-F3** — Loop-back is capped at N iterations (default N=3, configurable).
- **FR-F4** — On cap exhaustion the orchestrator halts and summons the human; it does not proceed with open findings.

### FR-G — Human approval at phase gates

- **FR-G1** — At a phase boundary (spec approved, architecture approved, backlog approved) the orchestrator pauses for interactive human confirmation before proceeding. The pause itself (reaching `awaiting-approval`) is now driven by factory's gate loop, which writes that status into `run.json`; the orchestrator's role is the human-facing `approve`/`reject` interaction, unchanged.
- **FR-G2** — _(Deferred)_ Unattended auto-approval (`--yes` / `--auto-approve`) returns with unattended execution (see Deferred scope, NG6).

### FR-H — Completion detection

- **FR-H1** — _(Superseded — moved to factory.)_ Completion is inferred from the working tree: a **gated phase** step is finished when the agent exits 0 and the working tree is clean (all artifacts committed, all hooks passed); a **`run-step`** invocation applies the same working-tree check; a **clean reviewer** that writes no findings is finished when its session exits zero.

### FR-I — Run state & resumability

- **FR-I1** — The orchestrator records run state (current phase, iteration, gate result) in `.orchestrator/run.json`. Still accurate — both the orchestrator (`approve`/`reject`/`release`/`abort`) and factory (execution) write to this same file and schema.
- **FR-I2** — _(Amended)_ Combined with on-disk artifacts and the findings store, a run is resumable after interruption. Resumability is now driven by `factory/scripts/trigger` and `factory/scripts/phase`, not an orchestrator `resume` command; the orchestrator's own recovery surface is `release` (restore a halted phase) plus `approve`/`reject`/`abort`.

### FR-J — Observability

- **FR-J1** — _(Superseded — moved to factory.)_ Each subprocess invocation is logged with agent, CLI, duration, exit status, and gate outcome. No orchestrator component writes this log any longer; `status > log` always renders empty (the `InvocationLogReader` port remains, unimplemented).

### FR-K — Model selection

- **FR-K1** — The planning phase assigns each story a `tier` (`economy`, `standard`, or `strong`) — the model strength its work needs. `tier` is a required field on the story, assigned by the planning agent, which runs on a strong model so its judgement rests on a full view of the dependency tree. Still accurate — unrelated to the orchestrator's own execution surface.
- **FR-K2** — _(Amended)_ `model.conf` is a per-CLI **tier router**: `[facts]` maps each tier to a concrete model for each configured CLI. The file format and `FileModelMatrix`'s read-only display of it remain in the orchestrator (`configure > model-matrix`); resolving a declared tier against `[facts]` at invocation time moved to factory.
- **FR-K3** — _(Superseded — moved to factory.)_ Model selection follows a fixed precedence: an explicit `--model` flag on the invocation overrides `model.conf`, which overrides the adapter's own default (`auto`). There is no per-story model field beyond `tier` itself; an operator who disagrees with a story's model edits its `tier`, which keeps the backlog CLI-agnostic.
- **FR-K4** — _(Superseded — moved to factory.)_ When `model.conf` has no entry for the active CLI and a required tier, the run halts by default, treating the gap as a configuration error (BR-020). The behaviour is configurable to fall back to the adapter default where a project accepts unmanaged model choice.
- **FR-K5** — `model.conf` is a first-class, operator-curated artifact maintained by its own workstep, independent of the phase chain. A `matrix-lint` check validates it (tier coverage per configured CLI, well-formed `on_missing`); a `backlog-lint` check validates each story's `tier` and serves as the planning phase's gate. Still accurate — `configure > model-matrix > validate` still shells out to `matrix-lint`.

### FR-L — Call-to-action in composed prompts

_(Superseded — moved to factory. Prompt composition no longer lives in the orchestrator.)_

- **FR-L1** — The prompt composer appends a `# Call to Action` section as the final block of every composed prompt, after findings. The call-to-action orients the agent to its specific workstep without duplicating the agent definition's workflow.
- **FR-L2** — An `InvocationContext` (phase, role, iteration) is a required parameter on the compose method. Every orchestrator invocation must provide context.
- **FR-L3** — Five template variants, selected by role and iteration: author-first-pass, author-loopback, reviewer-first-pass, reviewer-loopback, and standalone (for `run-step`).

### FR-M — Parallelism boundary

_(Superseded — moved to factory. This now describes a property of the factory-driven implementation phase, not the orchestrator.)_

- **FR-M1** — Story-level parallelism during implementation is the CLI agent's responsibility. The orchestrator sees `run-phase implementation` as one atomic invocation — the agent internally parallelizes across stories and returns a consolidated result.
- **FR-M2** — The orchestrator never spawns multiple CLI processes for a single phase, never manages parallel branches, and never tracks individual stories during execution. Parallelism is below the adapter boundary.

### FR-N — Story-commit consistency

- **FR-N1** — `backlog-lint` enforces story-commit consistency as a pre-commit check: a story's `status: done` is allowed only if at least one file matching its `outputs` globs exists on the branch (same or prior commit). This is error-severity and blocks the commit.
- **FR-N2** — If committed files match a story's `outputs` globs or the commit message references `(ST-NNNN)` but the story's status is not `done`, `backlog-lint` emits a warning (does not block).

## 5. Non-Functional Requirements

_NFR-1, 2, 3, 5, and 6 describe execution-time properties (gate determinism, session isolation, loop safety, adapter portability, invocation timeouts) that now hold at the factory layer, not the orchestrator (see the scope note at the top of this document). Retained here for history; the orchestrator's own NFRs are state-integrity (`.orchestrator/run.json`, findings, config) and menu responsiveness (see the [TUI addendum](prd-tui-addendum.md))._

- **NFR-1 (Determinism)** — Gate outcomes are reproducible: same artifacts → same gate result. The LLM sits between deterministic checks (Eichhorst's principle at the orchestration layer).
- **NFR-2 (Isolation)** — No agent invocation may inherit another's conversation context; a reviewer's judgement must be independent of the author's.
- **NFR-3 (Safety)** — No unbounded loops (FR-F3); a single active run enforced by a lock; all state (`run.json`, finding files) written atomically; commits go to a dedicated run branch from a clean tree, never force-pushed.
- **NFR-4 (Operability)** — A run can be observed (FR-J), interrupted, and resumed (FR-I) without corrupting state.
- **NFR-5 (Portability)** — Core logic is CLI-agnostic (FR-C); the MVP targets a local developer machine, CI/container later ([T-08](todos.md)).
- **NFR-6 (Bounded cost)** — Each agent invocation has a timeout; a hung CLI subprocess is killed and treated as a failed step.
- **NFR-7 (Minimal dependencies)** — Prefer the Python standard library, consistent with `spec-lint`; justify any third-party dependency ([T-06](todos.md)).

## 6. Constraints and Assumptions

- **C1** — Implementation language is Python (assume 3.10+ for typing).
- **C2** — The host is a git repository with `pre-commit` installed and configured.
- **C3** — GitHub Copilot CLI is installed and authenticated in the run environment for the MVP.
- **C4** — Each target CLI provides a non-interactive ("headless") invocation mode; exact flags differ per CLI ([T-01](todos.md)).
- **C5** — The orchestrator reuses `agents/`, `skills/`, and `scripts/` as-is, resolved from the package-relative path and exposed in target projects via symlinks (ADR-0010).
- **C6** — Proposed project home: `orchestrator/` ([T-07](todos.md)).
- **A1** — Agents reliably write their declared output artifacts to known paths, so filesystem-based completion detection (FR-H) is sound.

## 7. Open Questions

Each is tracked in [`todos.md`](todos.md):

- **[T-01]** Exact non-interactive invocation syntax for the Copilot CLI (and per-CLI differences).
- **[T-02]** Implementation depth of the Claude/Gemini adapters in the MVP.
- **[T-03]** ~~Redirecting review-agent issue-filing from GitHub to the local store.~~ **Resolved** — see FR-E4 and [ADR-0011](../adr/0011-reviewer-findings-ingest-contract.md).
- **[T-04]** Design of the future external-ticket adapter (GitHub Issues / Jira).
- **[T-05]** How a human "resolves" a finding — manual status edit vs agent-driven transition.
- **[T-06]** Python CLI framework and dependency policy (stdlib `argparse` vs `typer`/`click`; `jsonschema` for validation).
- **[T-07]** Confirm project home (`orchestrator/`).
- **[T-08]** Runtime environment beyond MVP (CI / container) and its auth/cost implications.
- **[T-09]** Retry cap default (proposed N=3) and whether it varies per phase.
